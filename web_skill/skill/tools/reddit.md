# Reddit

Read Reddit posts, comments, subreddits, and users via the `rdt` CLI (`rdt-cli`).
Output is YAML on a non-TTY (or pass `--json`); payloads live under `.data`.
Add `-c`/`--compact` for token-efficient output.

> No anonymous path: Reddit 403s the public `.json` API for logged-out / datacenter
> requests, so **login is required** in practice. Mainland China also needs a proxy.

## Auth (one-time, needs a browser login)
```
rdt status --json 2>/dev/null | grep -q '"authenticated": *true' && echo AUTH_OK || echo AUTH_NEEDED
```
If `AUTH_NEEDED`: the user logs into reddit.com in a browser, then:
```
rdt login        # auto-extract cookies (Chrome/Firefox/Edge/Brave/Arc/Safari/...)
```
Verify with `rdt whoami`. `Session expired` → `rdt logout && rdt login`.

## Read
```
rdt search <query>              # -r <sub>  -s top|new|relevance  -t day|week|month|year
rdt read <post_id>              # post + comments;  --expand-more for more comments
rdt show <index>                # read by short index from the last listing
rdt sub <name>                  # browse a subreddit (-s top -t week)
rdt sub-info <name>             # subreddit stats
rdt feed | rdt popular | rdt all      # home / r/popular / r/all  (feed needs login)
rdt user <name>                 # profile;  rdt user-posts / user-comments <name>
rdt export <query> -o out.csv   # bulk export to CSV/JSON
```
Short index: after a listing (`search`/`sub`/`feed`), `rdt show 1` reads result #1.

## Fallback — OpenCLI (only if rdt is unavailable/blocked)
If `rdt` is broken or hitting walls, and OpenCLI is set up (see [opencli.md](opencli.md)):
```
opencli reddit search|read|subreddit|hot
```
OpenCLI drives your real logged-in Chrome — heavier setup, but no separate login.

## Disabled — read-only tool
Never vote, save, subscribe, or comment: `rdt upvote`, `rdt save`, `rdt subscribe`,
`rdt comment` (and `rdt open`, which launches a browser).

## Notes
- **Pace requests: don't parallelize.** rdt has a built-in ~1s jitter; bursty use trips `rate_limited`.
- No DMs, no media download, single account.
- Install (auto-done by `web-skill install`): `uv tool install rdt-cli`; upgrade with `uv tool upgrade rdt-cli`.
- Full command list: `rdt --help` (the package ships its own detailed skill doc).
