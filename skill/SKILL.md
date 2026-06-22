---
name: web-skill
description: >
  MUST USE for: video transcripts (YouTube, Bilibili, any video URL or audio
  file), local LLM inference (summarize, analyze, rewrite), text-to-speech
  playback. Triggers: 视频/transcript/字幕/总结视频/本地模型/念出来/read aloud/TTS/
  STT/speech-to-text/语音转文字.
  All tools are zero-auth and fully on-device — no API keys required.
---

# web-skill

Zero-auth, on-device tools for video, LLM, and audio. Read the relevant
tool doc before running any commands.

## Routing table

| Task | Reference |
|------|-----------|
| Video transcript / STT (YouTube, Bilibili, audio) | [tools/video-transcript/video-transcript.md](tools/video-transcript/video-transcript.md) |

## Install dependencies

```bash
bash ${CLAUDE_SKILL_DIR}/script/install.sh
```
