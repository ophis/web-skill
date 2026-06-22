#!/usr/bin/env bash
# Install web-skill: copies skill files to ~/.claude/skills/web-skill, then installs dependencies.
# macOS / Apple Silicon only (mlx stack requires Metal GPU)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DST="$HOME/.claude/skills/web-skill"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}!${RESET} $*"; }
fail() { echo -e "${RED}✗${RESET} $*"; }
info() { echo -e "  $*"; }

# ── Guard ────────────────────────────────────────────────────────────────────

if [[ "$(uname)" != "Darwin" ]]; then
  fail "macOS only (MLX requires Apple Silicon Metal GPU)"; exit 1
fi
if [[ "$(uname -m)" != "arm64" ]]; then
  fail "Apple Silicon (arm64) required"; exit 1
fi

echo -e "\n${BOLD}Installing web-skill${RESET}\n"

# ── Register skill ────────────────────────────────────────────────────────────

echo -e "${BOLD}Skill registration${RESET}"
if [[ "$REPO_DIR" == "$SKILL_DST" ]]; then
  fail "Clone is inside the skills dir ($SKILL_DST) — installer would delete its own source."
  fail "Clone elsewhere (e.g. ~/.web-skill) and re-run."; exit 1
fi
rm -rf "$SKILL_DST"
cp -r "$REPO_DIR/skill" "$SKILL_DST"
ok "Copied to $SKILL_DST"

echo ""
echo -e "${BOLD}System dependencies${RESET}"

# ── Homebrew ─────────────────────────────────────────────────────────────────

if ! command -v brew &>/dev/null; then
  warn "Homebrew not found — installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
else
  ok "Homebrew $(brew --version | head -1 | awk '{print $2}')"
fi

# ── Core CLI tools ───────────────────────────────────────────────────────────

install_brew() {
  local formula="$1" cmd="${2:-$1}"
  if command -v "$cmd" &>/dev/null; then
    local ver
    ver=$("$cmd" --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1) || ver=""
    ok "$cmd${ver:+ $ver}"
  else
    warn "$cmd not found — installing $formula..."
    brew install "$formula"
    ok "$cmd installed"
  fi
}

install_brew uv uv
install_brew ffmpeg ffmpeg

# ── uv-managed tools (auto-install on first use) ─────────────────────────────

echo ""
echo -e "${BOLD}uv-managed tools (video-transcript)${RESET}"
info "yt-dlp, mlx-whisper, mlx-audio — auto-installed on first use via uv."
info "First run will download:"
info "  Whisper large-v3-turbo  ~1.6 GB  (English/other STT)"
info "  Qwen3-ASR 1.7B 4bit     ~0.9 GB  (Chinese STT)"

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Done.${RESET} Run this to verify:"
echo "  uv --version && ffmpeg -version | head -1"
