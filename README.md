# web-skill

Zero-auth, on-device tools for Claude Code — video transcripts. No API keys required.

## Install

```bash
git clone https://github.com/ophis/web-skill.git ~/.web-skill
bash ~/.web-skill/scripts/install.sh
```

The clone is the source; `install.sh` copies `skill/` into `~/.claude/skills/web-skill/`. Don't clone into the skills dir directly.

See [INSTALL.md](INSTALL.md) for full instructions (including the one-liner for AI agents).

## What's included

| Skill | What it does |
|-------|-------------|
| video-transcript | Transcribe YouTube / Bilibili / any video URL or local audio file |

## Requirements

- macOS, Apple Silicon (MLX stack requires Metal GPU)
- Homebrew

## Repo layout

```
skill/                  ← installed to ~/.claude/skills/web-skill/
  SKILL.md              ← router (auto-loaded by Claude Code)
  tools/
    video-transcript.md ← one .md per tool
    scripts/            ← shared scripts referenced by the tool docs
scripts/
  install.sh            ← installs system deps + registers skill
tests/                  ← one test_<script>.py per script
INSTALL.md              ← instructions for AI agents
```
