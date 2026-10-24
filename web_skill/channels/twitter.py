"""Twitter / X page reads through the independent web-skill profile."""
from urllib.parse import urlsplit

from .web import WebChannel


class TwitterChannel(WebChannel):
    name = "twitter"
    description = "Twitter / X tweets & timelines (read-only)"
    login_url = "https://x.com/"
    tier = 1

    def can_handle(self, url):
        host = urlsplit(url).hostname or ""
        return host in ("twitter.com", "x.com") or host.endswith((".twitter.com", ".x.com"))
