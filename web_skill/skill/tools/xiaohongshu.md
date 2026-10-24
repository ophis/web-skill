# Xiaohongshu (小红书)

Use [web.md](web.md) for independent manual login and read-only page options.

```bash
web-skill login https://www.xiaohongshu.com/
uv run ${CLAUDE_SKILL_DIR}/scripts/page.py "https://www.xiaohongshu.com/explore" --links --wait 3
uv run ${CLAUDE_SKILL_DIR}/scripts/page.py "https://www.xiaohongshu.com/search_result?keyword=美食" --links --wait 3
```

Search in Chinese and URL-encode queries. Read a full note URL from returned
links, preserving its `xsec_token`; bare note IDs can fail. Text includes only
visible content/comments; images and hidden comments are not read or downloaded.
Image-heavy notes may therefore be incomplete. Explain that limitation.

Wait 2–3 seconds between requests and do not parallelize. Login walls, captchas
and IP blocks require the user to resolve them manually. Never publish, comment,
reply, delete, like, favorite or follow.
