# Recommendations (YouTube + Bilibili)

Recommend **videos to watch**: fetch the personalized list of videos YouTube / Bilibili
suggest on your home page, as structured candidates (JSONL) to rank. Read-only; uses your
live browser login (same cookies as normal browsing).

```
uv run ${CLAUDE_SKILL_DIR}/scripts/recommend.py [--platform bilibili|youtube|both] [--limit N] [--browser chrome] > /tmp/recs.jsonl
```
Redirect to a file; `grep`/`Read` it on demand. One candidate per line:
`{platform, video_id, title, creator, creator_id, url, duration_sec, views, reason}`
- `reason` — Bilibili's own rec hint (e.g. `"7万点赞"`) when present; `null` otherwise.
- Recommendations are **ephemeral** — fetch fresh each time, never cache or store.
- A platform that fails prints to stderr and is skipped; exits non-zero only if **every** platform fails.

## Auth
- **Bilibili** needs the `SESSDATA` cookie, **YouTube** the `SAPISID` cookie — i.e. be logged into
  bilibili.com / youtube.com in the chosen browser (`--browser`, default `chrome`; `edge`/`firefox`/`brave`/…).
- Not logged in → that platform errors with a clear `no <cookie>` message.
- macOS may prompt for Keychain access to the browser's Safe Storage — approve it (sticks after).

## Using the candidates
This is a candidate **pool**, not a ranking. To surface what the user would actually watch, rank
the lines against their tastes — creators they already follow/watch, recurring topics — and drop
pure trending noise (YouTube's feed skews seasonal/viral). Return a short list: title · creator · why · url.
