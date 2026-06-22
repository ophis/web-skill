# -*- coding: utf-8 -*-
"""Shared OpenCLI backend probe — the cross-channel fallback (reddit, twitter, …).

`opencli daemon status` is a pure query (unlike `opencli doctor`, which auto-starts
the daemon). "Extension: connected" means the browser bridge is live and usable.
"""
from .probe import probe_command


def check(usage):
    """Return (level, message), or None if opencli isn't installed.

    usage = the native command hint to surface when the bridge is connected.
    """
    probe = probe_command("opencli", ["daemon", "status"], timeout=10, package="@jackwener/opencli")
    if probe.status == "missing":
        return None
    if probe.status in ("broken", "timeout"):
        return "error", "opencli installed but not responding\n" + probe.hint
    if "Extension: connected" in probe.output:
        return "ok", usage
    return "warn", "opencli installed — open Chrome + install/enable its extension (see opencli.md)"
