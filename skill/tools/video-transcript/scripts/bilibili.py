# /// script
# requires-python = ">=3.9"
# dependencies = ["requests"]
# ///
"""Bilibili helper. yt-dlp 412s on Bilibili's anti-crawl, so use the web API directly.

  meta  <url>            -> print title / duration(s) / description
  audio <url> [out.m4a]  -> download best audio track (default /tmp/vt_<BVID>.m4a), print path

Chain (the 412 fix): a Session GETs the homepage to receive a fresh anonymous buvid3
cookie, then hits the login-free official endpoints (cookie auto-resent) with UA + Referer:
  x/web-interface/view?bvid=    -> title, cid, desc, duration
  x/player/playurl?...&fnval=16 -> DASH audio baseUrl
Download the audio WITH a Referer header (CDN 403s without it; hotlink protection).
Feed the .m4a to stt.py for local transcription. See SKILL.md.
"""
import re
import sys

import requests

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    s.get("https://www.bilibili.com/", stream=True).close()  # seeds the fresh buvid3 cookie
    return s


def bvid(s, url):
    if "b23.tv" in url:  # short link -> resolve to the real video URL
        url = s.head(url, allow_redirects=True).url
    m = re.search(r"(BV[0-9A-Za-z]{10})", url)
    if not m:
        sys.exit(f"no BV id in: {url}")
    return m.group(1)


def api(s, url):
    d = s.get(url).json()
    if d.get("code") != 0:
        sys.exit(f"bilibili api error {d.get('code')}: {d.get('message')}")
    return d["data"]


def audio_url(s, bv, cid):
    d = api(s, f"https://api.bilibili.com/x/player/playurl?bvid={bv}&cid={cid}&fnval=16")
    tracks = (d.get("dash") or {}).get("audio") or []
    if not tracks:
        sys.exit("no DASH audio track (DRM or unusual format) -- cannot transcribe")
    return max(tracks, key=lambda a: a.get("bandwidth", 0))["baseUrl"]


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("meta", "audio"):
        sys.exit("usage: uv run bilibili.py meta|audio <url> [out.m4a]")
    cmd, url = sys.argv[1], sys.argv[2]
    s = session()
    info = api(s, f"https://api.bilibili.com/x/web-interface/view?bvid={bvid(s, url)}")

    if cmd == "meta":
        print(info["title"])
        print(f"duration: {info['duration']}s")
        print(info.get("desc", ""))
    else:
        out = sys.argv[3] if len(sys.argv) > 3 else f"/tmp/vt_{info['bvid']}.m4a"  # name by BVID -> audio maps to video
        with s.get(audio_url(s, info["bvid"], info["cid"]), stream=True) as r, open(out, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        print(out)


if __name__ == "__main__":
    main()
