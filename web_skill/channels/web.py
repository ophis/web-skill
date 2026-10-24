"""Offline availability of system Chrome and our own manual-login records."""
import shutil
from urllib.parse import urlsplit

from ..skill.scripts import browser
from .base import Channel


class WebChannel(Channel):
    name = "web"
    description = "Web pages (read-only)"
    backends = ["Playwright"]
    login_url = None
    tier = 0

    def can_handle(self, url):
        return urlsplit(url).scheme in ("http", "https")

    def check(self, config=None):
        self.active_backend = None
        if not shutil.which("uv"):
            return "off", "uv missing; install uv to run the page script"
        if not browser.chrome_path():
            return "off", "Google Chrome missing; install it manually"
        self.active_backend = "Playwright"
        if self.login_url:
            domain = urlsplit(self.login_url).hostname
            if browser.login_status(domain):
                return "warn", "manual login recorded in own profile; session not verified and may have expired"
            return "warn", f"no manual login recorded → web-skill login {self.login_url}"
        return "ok", "system Chrome available; page dependencies resolve via uv run (no browser started)"
