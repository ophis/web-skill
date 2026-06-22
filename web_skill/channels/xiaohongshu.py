# -*- coding: utf-8 -*-
"""XiaoHongShu — xhs-cli (browser-cookie login). OpenCLI fallback added later by
appending it to `backends` + an `_check_opencli` (see Agent-Reach's pattern)."""
from urllib.parse import urlparse

from ..probe import probe_command
from .base import Channel


class XiaoHongShuChannel(Channel):
    name = "xiaohongshu"
    description = "Xiaohongshu notes (read-only)"
    backends = ["xhs-cli"]
    tier = 1  # needs a one-time browser login

    def can_handle(self, url: str) -> bool:
        d = urlparse(url).netloc.lower()
        return "xiaohongshu.com" in d or "xhslink.com" in d

    def check(self, config=None):
        """Probe candidates in order; first fully-usable wins, else first fixable (warn)."""
        self.active_backend = None
        findings = []  # (backend, status, message)
        for backend in self.ordered_backends(config):
            result = self._check_xhs_cli() if backend == "xhs-cli" else None
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
        return "off", "xhs (xiaohongshu-cli) not installed → web-skill install"

    def _check_xhs_cli(self):
        """xhs-cli candidate. None = not installed."""
        probe = probe_command("xhs", ["status", "--yaml"], timeout=15, package="xiaohongshu-cli")
        if probe.status == "missing":
            return None
        if probe.status == "broken":
            return "error", "xhs exists but won't execute\n" + probe.hint
        if probe.status == "timeout":
            return "warn", "xhs installed but status check timed out\n" + probe.hint
        if probe.ok:  # `xhs status` exits 0 only when authenticated
            return "ok", "xhs ready (logged in): search / read / comments"
        return "warn", "xhs installed but not logged in → xhs login --cookie-source chrome"
