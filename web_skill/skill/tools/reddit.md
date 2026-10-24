# Reddit

Use [web.md](web.md) for independent manual login and read-only page options.

```bash
web-skill login https://www.reddit.com/
uv run ${CLAUDE_SKILL_DIR}/scripts/page.py "https://www.reddit.com/r/python/" --links --wait 2
uv run ${CLAUDE_SKILL_DIR}/scripts/page.py "https://www.reddit.com/search/?q=python" --links
```

Open a full post URL from the links to read visible comments. A subreddit URL
browses its rendered listing; user profiles use `/user/NAME/`. URL-encode search
queries. Output contains only rendered content; no comment expansion or automatic
pagination. Reddit may block anonymous/datacenter access; mainland China may need
the user's proxy. Login walls and captchas require manual resolution.

Stay read-only: no votes, saves, subscriptions, comments or messages.
