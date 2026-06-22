# web-skill — Installation Guide

## For AI Agents

### Goal

Install web-skill so the user has its on-device tools (video transcripts,
Xiaohongshu, …) available in Claude Code. web-skill is a Python package: it
installs the upstream CLIs, registers the skill, and reports status — it is the
installer/router, the agent drives the upstream tools directly.

### ⚠️ Boundaries

- **DO NOT** use `sudo` unless the user explicitly approves
- **DO NOT** modify files outside `~/.claude/skills/web-skill/` and the uv tool dirs
- **DO NOT** create files in the current working directory / user's project

### Step 1: Install the package (provides the `web-skill` CLI)

```bash
uv tool install git+https://github.com/ophis/web-skill.git
```

Upgrade later with `uv tool upgrade web-skill`.

### Step 2: Install tool dependencies

```bash
web-skill install
```

Installs (idempotent): Homebrew formulae (`ffmpeg`), `uv`, and per-channel CLIs
(`xiaohongshu-cli`). macOS / Apple Silicon only (MLX needs Metal).

First-run model downloads happen automatically on first use:
- Whisper large-v3-turbo ~1.6 GB (English STT)
- Qwen3-ASR 1.7B 4bit ~0.9 GB (Chinese STT)

### Step 3: Register the skill

```bash
web-skill skill --install      # copies the bundled skill into ~/.claude/skills/web-skill
```

### Step 4: Verify + report

```bash
web-skill doctor               # per-channel install/auth status
```

Tell the user what's green and what needs manual action — e.g. Xiaohongshu shows
`not logged in` until they run `xhs login --cookie-source chrome`, and STT models
download on first transcription.
