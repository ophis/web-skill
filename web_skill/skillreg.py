"""Register the bundled skill into the agent skill directory (copy, like Agent-Reach)."""
import importlib.resources as ir
import shutil
from pathlib import Path

SKILL_DST = Path.home() / ".claude" / "skills" / "web-skill"


def install_skill():
    res = ir.files("web_skill") / "skill"
    with ir.as_file(res) as src:  # real path whether run from source or installed wheel
        if SKILL_DST.exists():
            shutil.rmtree(SKILL_DST)
        SKILL_DST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, SKILL_DST)
    print(f"Skill installed: {SKILL_DST}")
    return 0


def uninstall_skill():
    if SKILL_DST.exists():
        shutil.rmtree(SKILL_DST)
        print(f"Skill removed: {SKILL_DST}")
    else:
        print("Skill not installed.")
    return 0
