"""Reddit page reads through the independent web-skill profile."""
from urllib.parse import urlsplit

from .web import WebChannel


class RedditChannel(WebChannel):
    name = "reddit"
    description = "Reddit posts & comments (read-only)"
    login_url = "https://www.reddit.com/"
    tier = 1

    def can_handle(self, url):
        host = urlsplit(url).hostname or ""
        return host == "redd.it" or host == "reddit.com" or host.endswith(".reddit.com")
