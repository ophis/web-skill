from ..probe import have
from .base import Channel


class VideoTranscript(Channel):
    name = "video-transcript"
    doc = "video-transcript.md"
    brew_deps = ["ffmpeg"]
    uv_tools = []  # yt-dlp / mlx-* auto-install on first `uv run` via PEP 723

    def status(self):
        missing = [c for c in ("uv", "ffmpeg") if not have(c)]
        if missing:
            return "error", f"missing {', '.join(missing)} — run: web-skill install"
        return "ok", "uv + ffmpeg ready (STT models download on first use)"
