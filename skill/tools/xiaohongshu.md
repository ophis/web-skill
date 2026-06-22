# Xiaohongshu (小红书)

Search, read, and interact with Xiaohongshu via the `xhs` CLI (`xiaohongshu-cli`).
Output is YAML on a non-TTY (or pass `--json`). Payloads live under `.data`.

## Auth (one-time, needs a browser login)

`xhs` needs a logged-in session — check first, don't assume:
```
xhs status --yaml >/dev/null && echo AUTH_OK || echo AUTH_NEEDED
```
If `AUTH_NEEDED`: the user logs into xiaohongshu.com in a browser, then extract its cookies:
```
xhs login                          # auto-detect a logged-in browser
xhs login --cookie-source chrome   # name it explicitly (arc/edge/firefox/safari/brave/...)
```
macOS may prompt to allow Keychain access to "Chrome Safe Storage" — approve it.
Verify with `xhs whoami`; cookies last ~7 days, re-run to refresh.

Avoid `xhs login --qrcode` unless cookie extraction is impossible — it downloads a
~600 MB Camoufox browser on first use and has been unreliable.

## Read
```
xhs search <keyword>            # --sort popular  --type video
xhs read <id|url|index>         # note content
xhs comments <id|url|index>     # add --all to auto-paginate
xhs user <user_id>              # profile;  xhs user-posts <user_id> for their notes
xhs hot -c <category>           # trending: fashion food cosmetics movie career love home gaming travel fitness
xhs feed                        # recommendation feed
```
Short index: after a `search`, `xhs read 1` / `xhs comments 1` reuse result #1.

## Write — confirm with the user before running
```
xhs like|favorite <id>          # --undo / unfavorite to reverse
xhs comment <id> -c "text"
xhs post --title "..." --body "..." [--images a.png]
```

## Notes
- **Do NOT parallelize** `xhs` calls — it has a built-in rate-limit delay for account safety.
- Captcha / IP-block: ask the user to resolve it in the browser, then retry.
- Full command list: `xhs --help` (the package ships its own detailed skill doc).
- Limits: no image/video download, no DMs, single account at a time.
- Install (auto-done by `scripts/install.sh`): `uv tool install xiaohongshu-cli`;
  upgrade with `uv tool upgrade xiaohongshu-cli` to avoid upstream API drift.
