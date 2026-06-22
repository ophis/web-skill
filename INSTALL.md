# web-skill — Installation Guide

## For AI Agents

### Goal

Install web-skill and its dependencies so the user has video transcription
available in Claude Code. After installation, the skill is registered at
`~/.claude/skills/web-skill/` and ready to use.

### ⚠️ Boundaries

- **DO NOT** use `sudo` unless the user explicitly approves
- **DO NOT** modify files outside `~/.web-skill/` (source clone) and `~/.claude/skills/web-skill/` (installed copy)
- **DO NOT** create files in the current working directory / user's project

### Step 1: Clone the repo

Clone to a **source** location — NOT into the skills dir. `install.sh` copies
`skill/` from here into `~/.claude/skills/web-skill/`.

```bash
git clone https://github.com/ophis/web-skill.git ~/.web-skill
```

If already cloned, pull latest:

```bash
git -C ~/.web-skill pull --ff-only
```

### Step 2: Install system dependencies

```bash
bash ~/.web-skill/scripts/install.sh
```

This installs: `uv`, `ffmpeg`, and the `xhs` CLI (`xiaohongshu-cli`).

First-run model downloads happen automatically when each tool is first used:
- Whisper large-v3-turbo ~1.6 GB (English STT)
- Qwen3-ASR 1.7B 4bit ~0.9 GB (Chinese STT)

Xiaohongshu needs a one-time browser login before use: `xhs login` (auto-extract
browser cookies) or `xhs login --qrcode` — the user must do this themselves.

### Step 3: Verify

```bash
uv --version && ffmpeg -version | head -1 && command -v xhs
ls ~/.claude/skills/web-skill/SKILL.md
```

### Step 4: Report to user

Tell the user which steps succeeded and which (if any) need manual action
(e.g. first-run model downloads, or `xhs login` for Xiaohongshu).
