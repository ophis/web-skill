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

## Architecture (doc = router, package = engine)

```
web_skill/                    ← Python package (the engine)
  cli.py                      ← web-skill install | doctor | skill --install
  probe.py                    ← tiny CLI prober
  channels/                   ← one file per tool: deps + status()
    base.py  video_transcript.py  xiaohongshu.py
  skill/                      ← bundled, copied to ~/.claude/skills/web-skill/
    SKILL.md                  ← router (auto-loaded by Claude Code)
    tools/                    ← pure router docs, one .md per tool
      video-transcript.md  xiaohongshu.md
    scripts/                  ← standalone uv-run scripts (PEP 723 inline deps)
      transcript.py  stt.py  bilibili.py
pyproject.toml                ← packaging + `web-skill` entry point
tests/                        ← one test_<script>.py per script
```

## Adding a channel

1. `web_skill/channels/<name>.py` — a `Channel` subclass (name, doc, `brew_deps`, `uv_tools`, `status()`); register it in `channels/__init__.py`.
2. `web_skill/skill/tools/<name>.md` — the router doc; add a row to `skill/SKILL.md`.
3. Reusable scripts (if any) go in `web_skill/skill/scripts/`; add `tests/test_<script>.py`.

## Requirements

macOS, Apple Silicon (MLX needs Metal GPU), Homebrew.
