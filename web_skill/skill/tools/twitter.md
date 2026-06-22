# Twitter / X

Read tweets, timelines, threads, and profiles via the `twitter` CLI (`twitter-cli`).
Output is YAML on a non-TTY (or `--yaml`/`--json`); payloads live under `.data`.
Use `-c`/`--compact` for token-efficient output.

## Auth (one-time, needs a browser login — no login command)
`twitter` auto-extracts cookies from a browser you're logged into x.com on. Check first:
```
twitter status --yaml >/dev/null && echo AUTH_OK || echo AUTH_NEEDED
```
If `AUTH_NEEDED`: the user logs into **x.com** in Arc / Chrome / Edge / Firefox / Brave,
then it just works — verify with `twitter whoami`. Pick a browser with
`TWITTER_BROWSER=chrome`. For headless/remote, set `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`
env vars instead (read-only; full writes need real cookies).

## Read
```
twitter search <query>          # -t Latest|Top  --max N
twitter tweet <id|url>          # a tweet + its replies;  twitter show <index> for last list
twitter feed                    # home timeline;  -t following for the following feed
twitter user <handle>           # profile;  twitter user-posts <handle> --max N for their tweets
twitter followers <handle> | twitter following <handle>
twitter bookmarks               # your bookmarks
twitter list <list_id>          # a list timeline
```
Short index: after a listing (`search`/`feed`/`user-posts`), `twitter show 1` opens result #1.

## Fallback — OpenCLI (only if twitter-cli is unavailable/blocked)
If `twitter` breaks and OpenCLI is set up (see [opencli.md](opencli.md)):
```
opencli twitter search|timeline|tweet|user|thread|trending
```
OpenCLI drives your real logged-in Chrome — heavier setup, no separate login.

## Disabled — read-only tool
Never post or interact: `twitter post`, `twitter reply`, `twitter quote`,
`twitter delete`, `twitter like`/`unlike`, `twitter retweet`/`unretweet`,
`twitter bookmark`, `twitter follow`/`unfollow`.

## Notes
- **Pace requests: don't parallelize.** HTTP 429 → wait 15+ min. Write ops carry a 1.5–4s delay.
- Likes are private since June 2024 — `twitter likes` only works for your own account.
- No DMs, no polls; image-only media. Single account.
- Install (auto-done by `web-skill install`): `uv tool install twitter-cli`; upgrade with `uv tool upgrade twitter-cli`.
- Full command list: `twitter --help` (the package ships its own detailed skill doc).
