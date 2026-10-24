"""Xiaohongshu page reads through the independent web-skill profile."""
from urllib.parse import urlsplit

from .web import WebChannel


class XiaoHongShuChannel(WebChannel):
    name = "xiaohongshu"
    description = "Xiaohongshu notes (read-only)"
    login_url = "https://www.xiaohongshu.com/"
    tier = 1

    def can_handle(self, url):
        host = urlsplit(url).hostname or ""
        return host in ("xiaohongshu.com", "xhslink.com") or host.endswith(".xiaohongshu.com")
