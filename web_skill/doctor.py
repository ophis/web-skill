# -*- coding: utf-8 -*-
"""Environment health checker (ported from Agent-Reach's doctor.py).

Each channel checks itself; doctor collects the results. A misbehaving channel
degrades to status='error' so it never takes the whole report down.
"""
from .channels import get_all_channels

_ICON = {"ok": "✅", "warn": "⚠️ ", "off": "⛔", "error": "❌"}


def check_all(config=None):
    results = {}
    for ch in get_all_channels():
        try:
            status, message = ch.check(config)
            active = getattr(ch, "active_backend", None)
        except Exception as e:  # doctor must survive any channel
            status, message, active = "error", f"check failed: {e}", None
        results[ch.name] = {
            "status": status, "name": ch.description, "message": message,
            "tier": ch.tier, "backends": ch.backends, "active_backend": active,
        }
    return results


def format_report(results) -> str:
    lines = ["web-skill status", "=" * 32]
    for r in results.values():
        active = ""
        if r["active_backend"] and len(r["backends"]) > 1:
            active = f" (backend: {r['active_backend']})"
        lines.append(f"{_ICON.get(r['status'], '?')} {r['name']} — {r['message']}{active}")
    return "\n".join(lines)
