# Recommendations (YouTube + Bilibili)

Fetch personalized home recommendations as JSONL candidates to rank. Uses only
the independent profile described in [web.md](web.md), never daily browsing data.

```bash
web-skill login https://www.bilibili.com/
web-skill login https://www.youtube.com/
uv run ${CLAUDE_SKILL_DIR}/scripts/recommend.py --platform both --limit 20 > /tmp/recs.jsonl
```

`--platform` accepts `bilibili`, `youtube` or `both`; limit is positive and per
platform. One candidate per line:
`{platform, video_id, title, creator, creator_id, url, duration_sec, views, reason}`.
Bilibili's recommendation hint appears in `reason` when present, else null.

Recommendations are ephemeral: fetch fresh, without persistent candidate storage.
The read-only recommendation APIs use only the selected site's session from our
profile, in memory; credentials are never printed or exported. Missing login
prints the relevant `web-skill login` command. A failed platform prints to stderr
and is skipped; exit is nonzero only if every requested platform fails.

Rank the candidate pool against the user's tastes, following/watch history they
have supplied and recurring topics. Return title · creator · why · URL; drop
irrelevant trending noise. Do not interact with accounts or videos.
