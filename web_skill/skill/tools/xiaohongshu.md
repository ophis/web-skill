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
**Never read a bare note_id.** XHS requires an `xsec_token` bound to the note, so a
raw id 404s/empties. Always `search`/`feed`/`hot` first, then read a *result* — by
its short index (`xhs read 1`) or its full URL/ID from the results (which carry the
token). Same rule for every backend.

## Read the images — content is often IN the pictures, not the caption
XHS is image-first: price boards (价格表), specs, and key details are frequently
only in a note's photos. After `xhs read`, fetch and view the images yourself:
```
xhs read <id|index> --json        # → .data.items[0].note_card.image_list[].url_default
curl -s -o /tmp/xhs.webp "<url_default>"          # xhscdn URLs need no auth/Referer
sips -s format png /tmp/xhs.webp --out /tmp/xhs.png   # WebP → PNG, then view it
```
`xhs` itself can't download/OCR images — it only returns the URLs.

## Disabled — read-only tool
Never publish, delete, or alter content: `xhs comment`, `xhs reply`, `xhs post`,
`xhs delete`, `xhs delete-comment`. (xhs-cli v0.6.x write ops also tend to fail with
a 406 signature error anyway — read-only is both the policy and the reliable path.)

## Engagement — not auto-permitted; ask the user first
```
xhs like|favorite <id>          # --undo / unfavorite to reverse
xhs follow <user_id>
```

## Notes
- **Pace requests: wait 2–3s between calls, never parallelize.** Bursty use (batch
  search, deep comment paging) trips a captcha the platform won't let you bypass.
- Captcha / IP-block: ask the user to resolve it in the browser, then retry.
- Full command list: `xhs --help` (the package ships its own detailed skill doc).
- Limits: no DMs, single account; the CLI won't download media (but image URLs are fetchable — see above).
- Install (auto-done by `web-skill install`): `uv tool install xiaohongshu-cli`;
  upgrade with `uv tool upgrade xiaohongshu-cli` to avoid upstream API drift.
