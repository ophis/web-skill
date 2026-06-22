# OpenCLI (shared fallback backend)

OpenCLI (`@jackwener/opencli`) drives your **real logged-in Chrome** via a browser
extension + local daemon, so it reuses sessions you're already signed into — no
per-site cookie/login dance. **Desktop only; Chrome must stay open.**

Two roles:
1. **Fallback** for `reddit` / `twitter` when their primary CLI is unavailable or blocked.
2. **Escape hatch** for any of its **155 site adapters** that has no dedicated tool —
   zhihu, weibo, bilibili, douban, v2ex, arxiv, github, taobao, xueqiu, hackernews,
   pubmed, wikipedia, and more. List them with `opencli` (no args) or `opencli list`.

Call it as `opencli <site> <cmd>` (e.g. `opencli zhihu search …`). Discover a site's
commands first — don't guess flags:
```
opencli <site> --help -f yaml      # all commands + args/options, structured
```
**Stay read-only**: search/read/list only — no posting, commenting, or liking.

## One-time setup (partly manual — can't be fully scripted)

1. Install the CLI (auto-done by `web-skill install --with-opencli`):
   ```
   npm install -g @jackwener/opencli      # needs Node.js >= 20
   ```
2. **Install the Chrome extension** (manual — a Web Store click, not scriptable):
   https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk
3. Keep Chrome open and logged into the target site(s). Verify:
   ```
   opencli daemon status      # Daemon: running / Extension: connected
   ```

The daemon auto-starts on first use. "Extension not connected" → confirm it's
installed and enabled in `chrome://extensions`, with Chrome open.
