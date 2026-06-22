# web-skill

Zero-auth, on-device tools for Claude Code — video transcripts, local LLM inference, and TTS. No API keys required.

## Install

```bash
git clone git@github.com:ophis/web-skill.git ~/playground/web-skill
bash ~/playground/web-skill/script/install.sh
```

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
skill/          ← installed to ~/.claude/skills/web-skill/
  SKILL.md      ← router (auto-loaded by Claude Code)
  references/
    video-transcript/
script/
  install.sh    ← installs system deps + registers skill
INSTALL.md      ← instructions for AI agents
```
