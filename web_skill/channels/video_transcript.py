# -*- coding: utf-8 -*-
"""Video transcript — local uv-run scripts (yt-dlp captions / mlx STT). No login."""
import shutil
from urllib.parse import urlparse

from .base import Channel

_VIDEO_HOSTS = ("youtube.com", "youtu.be", "bilibili.com", "b23.tv",
                "vimeo.com", "twitch.tv", "tiktok.com")


class VideoTranscriptChannel(Channel):
    name = "video-transcript"
    description = "Video transcript / STT"
    backends = ["uv-scripts"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        d = urlparse(url).netloc.lower()
        return any(h in d for h in _VIDEO_HOSTS)

    def check(self, config=None):
        self.active_backend = None
        missing = [c for c in ("uv", "ffmpeg") if not shutil.which(c)]
        if missing:
            return "error", f"missing {', '.join(missing)} → web-skill install"
        self.active_backend = "uv-scripts"
        return "ok", "uv-run scripts ready (STT models download on first use)"
