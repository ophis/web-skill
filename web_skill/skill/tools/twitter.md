# Twitter / X

Use [web.md](web.md) for independent manual login and read-only page options.

```bash
web-skill login https://x.com/
uv run ${CLAUDE_SKILL_DIR}/scripts/page.py "https://x.com/home" --links --wait 3
uv run ${CLAUDE_SKILL_DIR}/scripts/page.py "https://x.com/search?q=python&f=live" --links --wait 3
```

Read a full tweet URL from the returned links, or a profile at `https://x.com/HANDLE`.
URL-encode search queries. X may require requests unavailable in strict read-only
mode; report missing content rather than attempting another authentication path.
Only visible tweets/replies are returned; no automatic timeline pagination.

Never post, reply, like, repost, bookmark, follow or send messages. If rate-limited,
wait before retrying; login walls/captchas need the user's manual resolution.
