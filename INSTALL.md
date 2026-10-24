# web-skill — Installation Guide

## Install

```bash
uv tool install git+https://github.com/ophis/web-skill.git
web-skill install
web-skill skill --install
web-skill doctor
```

`install` retains video dependencies (`uv`, `ffmpeg`) on macOS / Apple Silicon.
Browser scripts declare Python dependencies inline for `uv run`; they install no
global browser tooling and never download a browser. Install Google Chrome
manually if absent. STT model downloads still happen on first transcription:
Whisper large-v3-turbo ~1.6 GB; Qwen3-ASR 1.7B 4bit ~0.9 GB.

## First login

Run only for sites the user needs:

```bash
web-skill login https://www.reddit.com/
web-skill login https://x.com/
web-skill login https://www.xiaohongshu.com/
web-skill login https://www.bilibili.com/
web-skill login https://www.youtube.com/
```

The user completes login in the visible web-skill window, then presses Enter in
the terminal to close it. Do not automate login or account interactions. An
expired session requires the same command again. Mainland-China Reddit access
may require the user's proxy.

Profile location, permissions, persistence and read-only behavior are documented
in [tools/web.md](web_skill/skill/tools/web.md). Agents may write only the skill
install locations, uv tool directories, and web-skill's owned state when invoking
its browser commands; do not use sudo or write into the user's project.

## Rebuild after source edits

```bash
uv tool install . --force
web-skill skill --install
```

The installed CLI copies the skill from its installed wheel. Alternatively,
`uv run web-skill skill --install` copies freshly built source. For a released
update, force-install the Git URL above, then re-register the skill.

## Verify

```bash
web-skill read https://example.com --links
web-skill doctor
```

Doctor performs offline availability checks only. A recorded manual login is not
proof of a valid remote session. It never launches the browser or an upstream
social authentication probe.
