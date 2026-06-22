# -*- coding: utf-8 -*-
"""web-skill CLI — install (deps), doctor (status), skill (register)."""
import argparse
import subprocess
import sys

from . import __version__
from .probe import probe_command
from .skillreg import install_skill, uninstall_skill


def doctor():
    from .doctor import check_all, format_report
    print(format_report(check_all()))
    return 0


def _brew(formula):
    if probe_command(formula).status == "missing":
        print(f"brew install {formula}")
        subprocess.run(["brew", "install", formula], check=True)


def _uv_tool(pkg, cmd):
    if probe_command(cmd).status == "missing":
        print(f"uv tool install {pkg}")
        subprocess.run(["uv", "tool", "install", pkg], check=True)


def _install_opencli():
    """Shared fallback backend — heavy + partly manual (npm + Chrome extension + daemon)."""
    if probe_command("node").status == "missing":
        _brew("node")
    if probe_command("opencli").status == "missing":
        print("npm install -g @jackwener/opencli")
        subprocess.run(["npm", "install", "-g", "@jackwener/opencli"], check=True)
    print("OpenCLI installed. MANUAL step: install its Chrome extension + keep Chrome\n"
          "open + log into the target sites. See tools/opencli.md.")


def install(with_opencli=False):
    """Install upstream backends. Concrete per channel (mirrors Agent-Reach's install funcs)."""
    if sys.platform != "darwin":
        print("macOS / Apple Silicon only (MLX needs Metal).", file=sys.stderr)
        return 1
    if probe_command("brew").status == "missing":
        print("Homebrew required: https://brew.sh", file=sys.stderr)
        return 1
    _brew("uv")
    _brew("ffmpeg")                      # video-transcript
    _uv_tool("xiaohongshu-cli", "xhs")   # xiaohongshu
    _uv_tool("rdt-cli", "rdt")           # reddit (primary)
    _uv_tool("twitter-cli", "twitter")   # twitter (primary)
    if with_opencli:                     # shared fallback for reddit/xiaohongshu/…
        _install_opencli()
    print("\nDone. Next: web-skill skill --install   (then: web-skill doctor)")
    return 0


def main():
    p = argparse.ArgumentParser(prog="web-skill", description=__doc__)
    sub = p.add_subparsers(dest="command")
    p_install = sub.add_parser("install", help="Install system deps + per-channel backends")
    p_install.add_argument("--with-opencli", action="store_true",
                           help="Also install OpenCLI (shared fallback; npm + manual Chrome extension)")
    sub.add_parser("doctor", help="Check each channel's backend availability")
    ps = sub.add_parser("skill", help="Register/unregister the skill in ~/.claude/skills")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--install", action="store_true")
    g.add_argument("--uninstall", action="store_true")
    sub.add_parser("version", help="Show version")

    args = p.parse_args()
    if args.command == "install":
        return install(args.with_opencli)
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
