# -*- coding: utf-8 -*-
"""Register the bundled skill into agent skill directories (ported from Agent-Reach).

Installs into EVERY known agent skill dir that exists (.agents / .openclaw /
.claude, plus $OPENCLAW_HOME), so the skill works across Claude Code, OpenClaw,
and generic agents. If none exist, defaults to ~/.agents/skills.
"""
import importlib.resources as ir
import os
import shutil
from pathlib import Path

SKILL_NAME = "web-skill"


def _skill_dirs():
    dirs = [
        Path.home() / ".agents" / "skills",      # generic agents (priority)
        Path.home() / ".openclaw" / "skills",    # OpenClaw
        Path.home() / ".claude" / "skills",      # Claude Code
    ]
    openclaw_home = os.environ.get("OPENCLAW_HOME")
    if openclaw_home:
        dirs.insert(0, Path(openclaw_home) / ".openclaw" / "skills")
    return dirs


def _copy(src, skill_dir):
    target = skill_dir / SKILL_NAME
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(src, target)
    return target


def install_skill():
    res = ir.files("web_skill") / "skill"
    targets = []
    with ir.as_file(res) as src:  # real path whether run from source or installed wheel
        for d in _skill_dirs():
            if d.is_dir():
                targets.append(_copy(src, d))
        if not targets:  # no known agent dir — default to ~/.agents/skills
            d = Path.home() / ".agents" / "skills"
            d.mkdir(parents=True, exist_ok=True)
            targets.append(_copy(src, d))
    for t in targets:
        print(f"Skill installed: {t}")
    return 0


def uninstall_skill():
    removed = False
    for d in _skill_dirs():
        target = d / SKILL_NAME
        if target.exists():
            shutil.rmtree(target)
            print(f"Skill removed: {target}")
            removed = True
    if not removed:
        print("Skill not installed.")
    return 0
