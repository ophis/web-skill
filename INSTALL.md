# web-skill — Installation Guide

## For AI Agents

### Goal

Install web-skill and its dependencies so the user has video transcription,
local LLM inference, and TTS available in Claude Code. After installation,
the skill is registered at `~/.claude/skills/web-skill/` and ready to use.

### ⚠️ Boundaries

- **DO NOT** use `sudo` unless the user explicitly approves
- **DO NOT** modify files outside `~/.claude/skills/web-skill/` and `~/.agent-reach/`
- **DO NOT** create files in the current working directory / user's project

### Step 1: Clone the repo

```bash
git clone https://github.com/ophis/web-skill.git ~/.claude/skills/web-skill
```

If already cloned, pull latest:

```bash
git -C ~/.claude/skills/web-skill pull --ff-only
```

### Step 2: Install system dependencies

```bash
bash ~/.claude/skills/web-skill/script/install.sh
```

This installs: `uv`, `ffmpeg`, `ollama` (+ prompts for model pull).

First-run model downloads happen automatically when each tool is first used:
- Whisper large-v3-turbo ~1.6 GB (English STT)
- Qwen3-ASR 1.7B 4bit ~0.9 GB (Chinese STT)
- Kokoro TTS ~0.5 GB (read-aloud)

### Step 3: Verify

```bash
uv --version && ffmpeg -version | head -1 && ollama list
ls ~/.claude/skills/web-skill/SKILL.md
```

### Step 4: Report to user

Tell the user which steps succeeded and which (if any) need manual action
(e.g. `ollama pull` for the large model, or first-run model downloads).
