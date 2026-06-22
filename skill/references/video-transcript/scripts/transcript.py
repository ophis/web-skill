# /// script
# requires-python = ">=3.9"
# dependencies = ["youtube-transcript-api>=1.1,<2"]
# ///
"""Fetch a video transcript by URL.

Routing:
  - YouTube      -> youtube-transcript-api (keyless; auto-picks an available caption language)
  - other sites  -> yt-dlp subtitles via uvx (1800+ sites)
Prints plain text. Exits non-zero with a clean message when no captions exist
anywhere -> then fall back to scripts/stt.py (local speech-to-text). See SKILL.md.

Usage: uv run transcript.py <url> [lang]
"""
import os
import re
import subprocess
import sys
import tempfile


def is_youtube(url):
    return re.search(r"(?:youtube\.com|youtu\.be)", url) is not None


def is_bilibili(url):
    return "bilibili.com" in url or "b23.tv" in url


def youtube_id(s):
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    m = re.search(r"(?:v=|/shorts/|/embed/|youtu\.be/)([\w-]{11})", s)
    return m.group(1) if m else None


def from_youtube(url, lang):
    vid = youtube_id(url)
    if not vid:
        sys.exit(f"no video id in: {url}")
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(vid, languages=[lang, "en"])
    except Exception:
        fetched = next(iter(api.list(vid))).fetch()  # fall back to any available language
    return " ".join(s.text for s in fetched)


def _vtt_to_text(path):
    out, prev = [], None
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if (not line or line == "WEBVTT" or "-->" in line or line.isdigit()
                or line.startswith(("Kind:", "Language:", "NOTE"))):
            continue
        line = re.sub(r"<[^>]+>", "", line)  # strip cue tags
        if line and line != prev:
            out.append(line)
            prev = line
    return " ".join(out)


def from_yt_dlp(url, lang):
    d = tempfile.mkdtemp()
    langs = (f"{lang}," if lang else "") + "en,zh,zh-Hans,zh-Hant"
    # curl_cffi + --impersonate: YouTube 429s the caption/timedtext endpoint without a real browser TLS
    # fingerprint. (A persistent 429 here is an IP-level rate limit; the caller then falls back to STT.)
    subprocess.run(
        ["uvx", "--with", "curl_cffi", "yt-dlp", "--impersonate", "chrome",
         "--write-subs", "--write-auto-subs", "--sub-format", "vtt",
         "--sub-langs", langs, "--skip-download", "-o", os.path.join(d, "sub"), url],
        capture_output=True, text=True,
    )
    vtts = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".vtt")]
    return _vtt_to_text(vtts[0]) if vtts else None


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: uv run transcript.py <url> [lang]")
    url = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"

    if is_youtube(url):
        try:
            print(from_youtube(url, lang))
        except Exception as e:
            text = from_yt_dlp(url, None if lang == "en" else lang)  # yt-dlp + impersonation: more robust than the api
            if text:
                print(text)
            else:
                sys.exit(f"no YouTube captions ({type(e).__name__}); yt-dlp caption fetch also failed "
                         "(YouTube 429s the timedtext endpoint for this IP) -- fall back to stt.py")
    elif is_bilibili(url):
        # ponytail: yt-dlp 412s + public subs rare -> audio+STT via bilibili.py; add a sub fetch if ever needed
        d = os.path.dirname(os.path.abspath(__file__))
        lc = "" if lang == "en" else f" {lang}"
        sys.exit("Bilibili: no caption route (yt-dlp 412s). Download audio + transcribe "
                 "(audio is named /tmp/vt_<BVID>.m4a; the first command prints the exact path):\n"
                 f'  uv run {d}/bilibili.py audio "{url}"\n'
                 f"  uv run {d}/stt.py /tmp/vt_<BVID>.m4a{lc}")
    else:
        text = from_yt_dlp(url, None if lang == "en" else lang)
        if text:
            print(text)
        else:
            sys.exit(f"no subtitles for {url} -- fall back to stt.py")


if __name__ == "__main__":
    main()
