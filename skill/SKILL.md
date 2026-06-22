---
name: web-skill
description: >
  MUST USE for: video transcripts (YouTube, Bilibili, any video URL or audio
  file); Xiaohongshu (小红书) note search / read / comments / posting.
  Triggers: 视频/transcript/字幕/总结视频/STT/语音转文字/小红书/xiaohongshu/xhs/redbook.
  On-device; video tools are keyless, Xiaohongshu needs a one-time browser login.
allowed-tools: Bash(uv run:*), Bash(uvx:*), Bash(uv tool:*), Bash(xhs:*)
---

# web-skill

On-device tools. Read the relevant tool doc before running any commands.

## Routing table

| Task | Reference |
|------|-----------|
| Video transcript / STT (YouTube, Bilibili, audio) | [tools/video-transcript.md](tools/video-transcript.md) |
| Xiaohongshu (小红书) search / read / comments / post | [tools/xiaohongshu.md](tools/xiaohongshu.md) |

Requires `uv` + `ffmpeg`, and `xhs` for Xiaohongshu (one-time install via the repo's `scripts/install.sh`).
