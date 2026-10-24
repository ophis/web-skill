# -*- coding: utf-8 -*-
"""web-skill CLI — install (deps), doctor (status), skill (register)."""
import argparse
import importlib.resources as ir
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


def install():
    """Install existing video dependencies; browser Python deps stay in uv scripts."""
    if sys.platform != "darwin":
        print("macOS / Apple Silicon only (MLX needs Metal).", file=sys.stderr)
        return 1
    if probe_command("brew").status == "missing":
        print("Homebrew required: https://brew.sh", file=sys.stderr)
        return 1
    _brew("uv")
    _brew("ffmpeg")                      # video-transcript
    print("Web reads use installed Google Chrome; Python dependencies are resolved by uv run.")
    print("\nDone. Next: web-skill skill --install   (then: web-skill doctor)")
    return 0


def _page(args):
    resource = ir.files("web_skill") / "skill" / "scripts" / "page.py"
    try:
        with ir.as_file(resource) as script:
            return subprocess.run(["uv", "run", str(script), *args]).returncode
    except OSError as error:
        print(f"cannot run page script: {error}", file=sys.stderr)
        return 1


def main(argv=None):
    p = argparse.ArgumentParser(prog="web-skill", description=__doc__)
    sub = p.add_subparsers(dest="command")
    sub.add_parser("install", help="Install existing video dependencies")
    sub.add_parser("doctor", help="Check each channel's backend availability")
    ps = sub.add_parser("skill", help="Register/unregister the skill in ~/.claude/skills")
    g = ps.add_mutually_exclusive_group(required=True)
    g.add_argument("--install", action="store_true")
    g.add_argument("--uninstall", action="store_true")
    sub.add_parser("version", help="Show version")
    read = sub.add_parser("read", help="Read a page with isolated headless Chrome")
    read.add_argument("url")
    read.add_argument("--selector")
    read.add_argument("--links", action="store_true")
    read.add_argument("--wait", type=float, default=0)
    login = sub.add_parser("login", help="Manually log in using a visible web-skill browser")
    login.add_argument("url")

    args = p.parse_args(argv)
    if args.command == "install":
        return install()
    if args.command == "login":
        return _page(["--login", args.url])
    if args.command == "read":
        options = [args.url, "--wait", str(args.wait)]
        if args.selector is not None:
            options += ["--selector", args.selector]
        if args.links:
            options.append("--links")
        return _page(options)
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
