---
name: web-skill
description: >
  MUST USE for: video transcripts (YouTube, Bilibili, any video URL or audio
  file). Triggers: 视频/transcript/字幕/总结视频/STT/speech-to-text/语音转文字.
  Zero-auth and fully on-device — no API keys required.
allowed-tools: Bash(uv run:*), Bash(uvx:*)
---

# web-skill

Zero-auth, on-device tools for video. Read the relevant tool doc before running any commands.

## Routing table

| Task | Reference |
|------|-----------|
| Video transcript / STT (YouTube, Bilibili, audio) | [tools/video-transcript/video-transcript.md](tools/video-transcript/video-transcript.md) |

Requires `uv` and `ffmpeg` (one-time install via the repo's `scripts/install.sh`).
