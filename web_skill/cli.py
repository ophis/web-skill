"""web-skill CLI — install (deps), doctor (status), skill (register)."""
import argparse
import subprocess
import sys

from . import __version__
from .channels import CHANNELS
from .probe import have
from .skillreg import install_skill, uninstall_skill

_ICON = {"ok": "✅", "warn": "⚠️ ", "error": "❌", "off": "⛔"}


def doctor():
    for ch in CHANNELS:
        level, msg = ch.status()
        print(f"{_ICON.get(level, '?')} {ch.name:18} {msg}")
    return 0


def _ensure_brew():
    if have("brew"):
        return
    print("Homebrew required: https://brew.sh", file=sys.stderr)
    sys.exit(1)


def install():
    if sys.platform != "darwin":
        print("macOS / Apple Silicon only (MLX needs Metal).", file=sys.stderr)
        return 1
    _ensure_brew()
    brew = sorted({f for ch in CHANNELS for f in ch.brew_deps} | {"uv"})
    for f in brew:
        if not have(f):
            print(f"brew install {f}")
            subprocess.run(["brew", "install", f], check=True)
    for tool in sorted({t for ch in CHANNELS for t in ch.uv_tools}):
        print(f"uv tool install {tool}")
        subprocess.run(["uv", "tool", "install", tool], check=True)
    print("\nDone. Next: web-skill skill --install   (then: web-skill doctor)")
    return 0


def main():
    p = argparse.ArgumentParser(prog="web-skill", description=__doc__)
    sub = p.add_subparsers(dest="command")
    sub.add_parser("install", help="Install system deps + per-channel CLIs")
    sub.add_parser("doctor", help="Show each channel's install/auth status")
    ps = sub.add_parser("skill", help="Register/unregister the skill in ~/.claude/skills")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--install", action="store_true")
    g.add_argument("--uninstall", action="store_true")
    sub.add_parser("version", help="Show version")

    args = p.parse_args()
    if args.command == "install":
        return install()
    if args.command == "doctor":
        return doctor()
    if args.command == "skill":
        return install_skill() if args.install else uninstall_skill()
    if args.command == "version":
        print(__version__)
        return 0
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
