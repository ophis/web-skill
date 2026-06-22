# -*- coding: utf-8 -*-
"""Twitter / X — twitter-cli (primary) with OpenCLI as the shared opt-in fallback.

No anonymous access: X requires a logged-in session. twitter-cli auto-extracts
browser cookies (Arc/Chrome/Edge/Firefox/Brave) or takes env vars; OpenCLI reuses
the browser directly.
"""
from urllib.parse import urlparse

from .. import opencli
from ..probe import probe_command
from .base import Channel


class TwitterChannel(Channel):
    name = "twitter"
    description = "Twitter / X tweets & timelines (read-only)"
    backends = ["twitter-cli", "OpenCLI"]  # twitter-cli preferred; OpenCLI is the opt-in fallback
    tier = 1  # needs a browser login (cookie auto-extraction)

    def can_handle(self, url: str) -> bool:
        d = urlparse(url).netloc.lower()
        return d in ("twitter.com", "x.com") or d.endswith((".twitter.com", ".x.com"))

    def check(self, config=None):
        self.active_backend = None
        findings = []
        for backend in self.ordered_backends(config):
            result = self._check_twitter_cli() if backend == "twitter-cli" else self._check_opencli()
            if result is None:
                continue
            findings.append((backend, *result))
        for wanted in ("ok", "warn"):
            for backend, status, message in findings:
                if status == wanted:
                    self.active_backend = backend
                    return status, message
        if findings:
            return "error", "\n".join(m for _, _, m in findings)
        return "off", "no twitter backend → web-skill install (twitter-cli); OpenCLI via --with-opencli"

    def _check_twitter_cli(self):
        """twitter-cli candidate. None = not installed."""
        # status auto-extracts browser cookies first — can be slow, so allow generous time.
        probe = probe_command("twitter", ["status", "--yaml"], timeout=30, package="twitter-cli")
        if probe.status == "missing":
            return None
        if probe.status == "broken":
            return "error", "twitter exists but won't execute\n" + probe.hint
        if probe.status == "timeout":
            return "warn", "twitter installed but status check timed out\n" + probe.hint
        if probe.ok:  # `twitter status` exits 0 only when authenticated
            return "ok", "twitter ready (logged in): feed / search / tweet / user"
        return "warn", "twitter installed but not logged in → log into x.com in a browser (auto-extracts cookies)"

    def _check_opencli(self):
        return opencli.check("opencli ready (browser bridge): twitter search/timeline/tweet/user")
