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
install_brew ollama ollama
install_brew googleworkspace-cli gws

# ── Ollama model ─────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Ollama model (local-llm skill)${RESET}"

MODEL="qwen3.6:35b-mlx"
if ollama list 2>/dev/null | grep -q "$MODEL"; then
  ok "$MODEL already pulled"
else
  warn "$MODEL not found"
  if [[ ! -t 0 ]]; then
    warn "Non-interactive — skipping. Run 'ollama pull $MODEL' manually."
  else
  info "This model is ~22GB. Pull now? [y/N] "
  read -r reply
  if [[ "$reply" =~ ^[Yy]$ ]]; then
    # ollama needs the server running to pull
    if ! pgrep -x ollama &>/dev/null; then
      info "Starting ollama server..."
      ollama serve &>/dev/null &
      sleep 3
    fi
    ollama pull "$MODEL"
    ok "$MODEL pulled"
  else
    warn "Skipped — run 'ollama pull $MODEL' when ready"
  fi
  fi  # end interactive block
fi

# ── uv-managed tools (auto-install on first use, just warm the cache) ────────

echo ""
echo -e "${BOLD}uv-managed tools (video-transcript, read-aloud)${RESET}"
info "yt-dlp, mlx-whisper, mlx-audio, kokoro — auto-installed on first use via uv."
info "First run of each will download:"
info "  Whisper large-v3-turbo  ~1.6 GB  (English/other STT)"
info "  Qwen3-ASR 1.7B 4bit     ~0.9 GB  (Chinese STT)"
info "  Kokoro TTS model         ~0.5 GB  (read-aloud)"

# ── gws auth ─────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Google Workspace auth (gws skill)${RESET}"
if gws auth status &>/dev/null 2>&1; then
  ok "gws already authenticated"
else
  warn "gws not authenticated — run 'gws auth login' to set up OAuth"
fi

# ── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Done.${RESET} Run this to verify everything:"
echo "  uv --version && ffmpeg -version | head -1 && ollama list && gws --version"
