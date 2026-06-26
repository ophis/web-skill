---
name: web-skill
description: >
  MUST USE for: video transcript / STT — YouTube, Bilibili, any video URL or audio file
  (视频/字幕/总结视频/语音转文字); Xiaohongshu note search/read/comments (小红书/xhs/redbook);
  Reddit posts/comments/subreddit search (redd.it); Twitter/X tweets/timelines/search (推特/x.com);
  recommending videos to watch — which videos to watch next from your personalized
  YouTube/Bilibili home recommendations (推荐视频/看什么视频/有什么好看的/首页推荐).
  Video tools are keyless; social + recommendation tools are read-only and need a one-time
  browser login (Reddit also needs a mainland-China proxy). On-device.
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
| Recommend videos to watch — personalized YouTube / Bilibili home video recommendations (read-only) | [tools/recommend.md](tools/recommend.md) |
| **Any other site** with no row above (zhihu, weibo, bilibili, douban, v2ex, arxiv, github, taobao…) | run `opencli <site>` directly — [tools/opencli.md](tools/opencli.md) |

Backends install via `web-skill install`; check status with `web-skill doctor`.
OpenCLI drives **155 sites** out of the box and is the escape hatch for anything
without a dedicated tool above (also the shared opt-in fallback for reddit/twitter).
Discover commands with `opencli <site> --help -f yaml`. Stay read-only.
