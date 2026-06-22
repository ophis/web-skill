---
name: web-skill
description: >
  MUST USE for: video transcripts (YouTube, Bilibili, any video URL or audio
  file); Xiaohongshu (小红书) note search / read / comments; Reddit posts /
  comments / subreddit search; Twitter / X tweets / timelines / search.
  Triggers: 视频/transcript/字幕/总结视频/STT/语音转文字/小红书/xiaohongshu/xhs/redbook/
  reddit/subreddit/redd.it/twitter/tweet/x.com/推特.
  On-device; video tools are keyless. Social tools (Xiaohongshu / Reddit /
  Twitter) are read-only and need a one-time browser login; Reddit also needs a
  proxy in mainland China.
allowed-tools: Bash
---

# web-skill

On-device tools. Read the relevant tool doc before running any commands.

## Routing table

| Task | Reference |
|------|-----------|
| Video transcript / STT (YouTube, Bilibili, audio) | [tools/video-transcript.md](tools/video-transcript.md) |
| Xiaohongshu (小红书) search / read / comments (read-only) | [tools/xiaohongshu.md](tools/xiaohongshu.md) |
| Reddit posts / comments / subreddit / search (read-only) | [tools/reddit.md](tools/reddit.md) |
| Twitter / X tweets / timelines / search (read-only) | [tools/twitter.md](tools/twitter.md) |

Backends install via `web-skill install`; check status with `web-skill doctor`.
OpenCLI is a shared opt-in fallback ([tools/opencli.md](tools/opencli.md)).
