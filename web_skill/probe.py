"""Tiny CLI prober — enough for doctor/install, no framework."""
import shutil
import subprocess


def have(cmd):
    return shutil.which(cmd) is not None


def run(cmd, args, timeout=15):
    """Run a command. Returns the CompletedProcess, or None if cmd is missing."""
    if not have(cmd):
        return None
    try:
        return subprocess.run([cmd, *args], capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return False  # installed but unrunnable / hung
