---
name: video-transcript
description: >-
  Fetch a video's transcript/captions from a URL — YouTube and 1800+ other sites
  (Bilibili, Vimeo, Twitch, TikTok, …) — for summarizing, quoting, or analyzing a
  video. Keyless, local, runs via uv. Use whenever a task involves a video link and
  you need what was said.
allowed-tools: Bash(uv run:*), Bash(uvx:*)
---

# Video transcript

## 1. Transcript (auto-routes by site)
```
uv run ${CLAUDE_SKILL_DIR}/scripts/transcript.py "<url>" [lang] > /tmp/vt_<id>.txt
```
Redirect to a file. `grep` or `Read` it only when you need the transcript's full or partial content.
- **YouTube** → `youtube-transcript-api` (fast, keyless), then falls back to yt-dlp captions
  (with `curl_cffi` impersonation). Auto-picks whatever caption language exists, so non-English
  videos work **without passing `lang`**. If YouTube is rate-limiting the caption endpoint for your
  IP (HTTP 429 on both routes — not a code bug, and cookies/impersonation don't bypass it), → step 2 (STT).
- **Bilibili** → no caption route (yt-dlp 412s on its anti-crawl); prints the exact
  audio+STT commands to run → step 2 (Bilibili branch).
- **Other sites** (1800+ via yt-dlp) → downloads the site's subtitles. Pass `lang` to prefer one.
- Prints plain text. Exits non-zero with a clean message when **no captions exist anywhere** → step 2.

## 2. No captions anywhere → local speech-to-text (heavier)
Download the audio, then transcribe **locally on the GPU**:
```
uvx yt-dlp -f bestaudio -o '/tmp/vt_%(id)s.%(ext)s' --no-simulate --print after_move:filepath "<url>"
# names the audio by video id and prints its exact path, e.g. /tmp/vt_<id>.webm — pass that path to stt.py
uv run ${CLAUDE_SKILL_DIR}/scripts/stt.py /tmp/vt_<id>.<ext> [lang] > /tmp/vt_<id>.txt
```
**Bilibili** (yt-dlp 412s — use the official-API helper instead, always outputs .m4a):
```
uv run ${CLAUDE_SKILL_DIR}/scripts/bilibili.py audio "<url>"     # -> /tmp/vt_<BVID>.m4a (prints the path)
uv run ${CLAUDE_SKILL_DIR}/scripts/stt.py /tmp/vt_<BVID>.m4a [lang] > /tmp/vt_<BVID>.txt
```
`bilibili.py meta "<url>"` prints title/duration/description (yt-dlp's `--print` also 412s).
- `mlx-whisper` (Apple **MLX / Metal GPU**), `large-v3-turbo` model — **Apple Silicon only**; needs `ffmpeg` (`brew install ffmpeg`). First run downloads ~1.6GB to `~/.cache/huggingface`. Fully on-device, keyless.
- `lang` optional (auto-detected); pass e.g. `zh` to skip detection. Heavy (model + a couple min) — only when there are genuinely no captions.

## 3. Metadata (title / description)
```
uvx yt-dlp --print title --print description --print duration_string "<url>"   # Bilibili: use bilibili.py meta
```

## Notes
- **Audio naming convention**: downloaded audio is `/tmp/vt_<video-id>.<ext>` (YouTube id / Bilibili BVID).
  Each file maps unambiguously to its source video, and parallel downloads of different videos never collide.
  The download command **prints the exact path** — use that, don't guess the extension.
- **Always quote the URL** (`"<url>"`) — zsh globs the `?` and `&` in YouTube/Bilibili URLs, so an
  unquoted link fails with `no matches found`.
- YouTube blocks datacenter IPs; running on a local/residential IP is most reliable.
- DRM streaming (Netflix / Spotify / Disney+ …) cannot be downloaded.
- Login-gated sites: add `--cookies-from-browser chrome` to the yt-dlp commands.
