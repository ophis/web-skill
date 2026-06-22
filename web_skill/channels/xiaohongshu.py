from ..probe import have, run
from .base import Channel


class Xiaohongshu(Channel):
    name = "xiaohongshu"
    doc = "xiaohongshu.md"
    brew_deps = []
    uv_tools = ["xiaohongshu-cli"]

    def status(self):
        if not have("xhs"):
            return "error", "xhs not installed — run: web-skill install"
        r = run("xhs", ["status", "--yaml"])
        if r is False:
            return "error", "xhs installed but unrunnable"
        if r and r.returncode == 0:
            return "ok", "xhs logged in"
        return "warn", "xhs installed, not logged in — run: xhs login --cookie-source chrome"
