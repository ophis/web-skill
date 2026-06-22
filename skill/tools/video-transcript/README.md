# video-transcript — setup & dependencies

Fetch a video's transcript from a URL — captions when they exist, local speech-to-text as a
fallback — for YouTube, Bilibili, and 1800+ other sites. Keyless, runs locally. Usage is in
`SKILL.md`; this file is the one-time setup.

## You install these
- **uv** — runs every script (`brew install uv`). Scripts use PEP 723 inline dependencies, so uv
  auto-installs each script's Python deps into a cached env on first run; there is nothing to
  `pip install` yourself.
- **ffmpeg** — `brew install ffmpeg`. Required by the speech-to-text step (whisper decodes audio
  through it) and by yt-dlp.
- **Apple Silicon Mac** — required only for the speech-to-text fallback (`mlx-whisper` uses the
  Metal GPU). Plain caption fetching (step 1) works on any platform.

## uv / the model handle the rest (no action needed)
- **Python** — uv fetches a compatible interpreter per script (each file pins `requires-python`).
- **Per-script deps**, installed by uv on first run:
  - `transcript.py` → `youtube-transcript-api`
  - `bilibili.py` → `requests`
  - `stt.py` → `mlx-whisper`
  - yt-dlp runs via `uvx` (no install).
- **STT model** — `mlx-community/whisper-large-v3-turbo` (~1.6 GB), downloaded to
  `~/.cache/huggingface` on the first STT run. On-device, keyless.

## Notes
- No API keys anywhere.
- First run of each step is slow (deps + model download); cached and fast afterwards.
- YouTube blocks datacenter IPs — run on a local/residential connection.
- DRM streams (Netflix / Spotify / Disney+) can't be downloaded; login-gated sites need
  `--cookies-from-browser chrome` on the yt-dlp commands.
