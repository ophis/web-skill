# -*- coding: utf-8 -*-
"""Reddit — rdt-cli (primary) with OpenCLI as a shared opt-in fallback.

No zero-config path: Reddit blocks anonymous .json (403) and closed self-service
API registration, so every backend rides a logged-in session. rdt-cli extracts
browser cookies; OpenCLI reuses the browser directly. Mainland China needs a proxy.
"""
from urllib.parse import urlparse

from .. import opencli
from ..probe import probe_command
from .base import Channel


class RedditChannel(Channel):
    name = "reddit"
    description = "Reddit posts & comments (read-only)"
    backends = ["rdt-cli", "OpenCLI"]  # rdt-cli preferred; OpenCLI is the opt-in fallback
    tier = 1  # needs a one-time browser login

    def can_handle(self, url: str) -> bool:
        d = urlparse(url).netloc.lower()
        return "reddit.com" in d or "redd.it" in d

    def check(self, config=None):
        self.active_backend = None
        findings = []
        for backend in self.ordered_backends(config):
            result = self._check_rdt() if backend == "rdt-cli" else self._check_opencli()
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
        return "off", "no reddit backend → web-skill install (rdt-cli); OpenCLI via --with-opencli"

    def _check_rdt(self):
        """rdt-cli candidate. None = not installed."""
        # rdt status extracts browser cookies first — can take ~20s, so allow generous time.
        probe = probe_command("rdt", ["status", "--json"], timeout=35, package="rdt-cli")
        if probe.status == "missing":
            return None
        if probe.status == "broken":
            return "error", "rdt exists but won't execute\n" + probe.hint
        if probe.status == "timeout":
            return "warn", "rdt installed but status check timed out\n" + probe.hint
        # `rdt status` exits 0 even unauthenticated; read the payload (stderr noise is harmless here).
        if '"authenticated": true' in probe.output or '"authenticated":true' in probe.output:
            return "ok", "rdt ready (logged in): search / read / sub / user"
        return "warn", "rdt installed but not logged in → rdt login"

    def _check_opencli(self):
        return opencli.check("opencli ready (browser bridge): reddit search/read/subreddit/hot")
