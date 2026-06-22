# -*- coding: utf-8 -*-
"""Lightweight upstream command probing (ported from Agent-Reach's probe.py).

Distinguishes the failure modes that look identical to shutil.which():
  - missing: not on PATH
  - broken: exists but cannot execute (stale venv shim after a Python upgrade —
    uv tool / pipx installs break this way: which() finds the shim, exec fails)
  - timeout/error: runs but misbehaves

Channels use probe_command() inside check() so doctor reports real health.
"""
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional, Sequence

_BROKEN_EXIT_CODES = (126, 127)  # shell "found but not executable" / "not found"


def _utf8_env():
    env = dict(os.environ)
    env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
    return env


@dataclass
class ProbeResult:
    status: str  # "ok" | "missing" | "broken" | "timeout" | "error"
    output: str = ""
    hint: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def reinstall_hint(package: str) -> str:
    return (
        "command exists but won't execute — usually a stale venv interpreter after a "
        f"Python upgrade. Reinstall to fix:\n  uv tool install --force {package}"
    )


def probe_command(cmd, args=("--version",), timeout=10, retries=0, package=None):
    """Execute `cmd *args` and classify. SIDE-EFFECT-FREE probes only (retries re-run verbatim)."""
    path = shutil.which(cmd)
    if not path:
        return ProbeResult("missing")
    last = None
    for _ in range(retries + 1):
        last = _run_once(path, args, timeout, package or cmd)
        if last.ok or last.status in ("missing", "broken"):
            return last
    return last


def _run_once(path: str, args: Sequence[str], timeout: int, package: str) -> ProbeResult:
    try:
        r = subprocess.run([path, *args], capture_output=True, encoding="utf-8",
                           errors="replace", timeout=timeout, env=_utf8_env())
    except OSError:
        return ProbeResult("broken", hint=reinstall_hint(package))
    except subprocess.TimeoutExpired:
        return ProbeResult("timeout", hint=f"`{path}` timed out (>{timeout}s)")
    if r.returncode in _BROKEN_EXIT_CODES:
        return ProbeResult("broken", hint=reinstall_hint(package))
    output = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode != 0:
        return ProbeResult("error", output=output)
    return ProbeResult("ok", output=output)
