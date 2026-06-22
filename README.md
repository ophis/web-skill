# web-skill

On-device tools for Claude Code — video transcripts and Xiaohongshu (小红书).
Packaged as a Python CLI that installs deps, registers the skill, and reports
status. The **agent is the router**: it reads the skill docs and drives the
upstream CLIs directly.

## Install

```bash
uv tool install git+https://github.com/ophis/web-skill.git
web-skill install            # ffmpeg, uv, per-channel CLIs (macOS / Apple Silicon)
web-skill skill --install    # register into ~/.claude/skills/web-skill
web-skill doctor             # check status
```

See [INSTALL.md](INSTALL.md) for the AI-agent install flow.

## What's included

| Tool | What it does |
|------|-------------|
| video-transcript | Transcribe YouTube / Bilibili / any video URL or local audio file (keyless) |
| xiaohongshu | Search / read / browse 小红书 notes + comments via `xhs` (read-only; one-time browser login) |
| reddit | Search / read posts, comments, subreddits, users via `rdt` (read-only; browser login; proxy in CN). OpenCLI fallback. |

OpenCLI (`@jackwener/opencli`) is a shared opt-in fallback backend reused across
social channels — install with `web-skill install --with-opencli`.

## Architecture (doc = router, package = engine)

```
web_skill/                    ← Python package (the engine; framework ported from Agent-Reach)
  cli.py                      ← web-skill install | doctor | skill --install
  probe.py                    ← probe_command() — installed vs broken vs not-logged-in
  doctor.py                   ← check_all() / format_report()
  channels/                   ← one Channel per platform
    base.py                   ← Channel ABC: backends (ordered), check(), active_backend
    video_transcript.py  xiaohongshu.py
  skill/                      ← bundled, copied to ~/.claude/skills/web-skill/
    SKILL.md                  ← router (auto-loaded by Claude Code)
    tools/                    ← pure router docs, one .md per tool
      video-transcript.md  xiaohongshu.md
    scripts/                  ← standalone uv-run scripts (PEP 723 inline deps)
      transcript.py  stt.py  bilibili.py
pyproject.toml                ← packaging + `web-skill` entry point
tests/                        ← one test_<script>.py per script
```

A `Channel` lists its `backends` in priority order; `check()` probes them with
`probe_command()` and sets `active_backend` to the first usable one (the
deterministic backend selection lives in code, not in the agent). The agent
reads the skill docs and runs the active backend's native CLI directly.

## Adding a channel

1. `web_skill/channels/<name>.py` — a `Channel` subclass: `name`, `description`, `backends` (ordered), `tier`, `can_handle()`, `check()` (probe each backend, set `active_backend`); register it in `channels/__init__.py`.
2. Add its install line(s) to `install()` in `web_skill/cli.py`.
3. `web_skill/skill/tools/<name>.md` — the router doc; add a row to `skill/SKILL.md`.
4. Reusable scripts (if any) go in `web_skill/skill/scripts/`; add `tests/test_<script>.py`.

## Requirements

macOS, Apple Silicon (MLX needs Metal GPU), Homebrew.
