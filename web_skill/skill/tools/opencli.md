# OpenCLI (shared fallback backend)

OpenCLI (`@jackwener/opencli`) drives your **real logged-in Chrome** via a browser
extension + local daemon, so it reuses sessions you're already signed into — no
per-site cookie/login dance. It's the cross-channel fallback for `reddit` and
`twitter` (and later `zhihu`). **Desktop only; Chrome must stay open.**

Use it only when a channel's primary CLI is unavailable or blocked. The channel
docs call it as `opencli <site> <cmd>` (e.g. `opencli reddit search …`).

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
