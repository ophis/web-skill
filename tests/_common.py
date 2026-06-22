"""Shared loader: import a script from skill/tools/scripts/ by name (no package)."""
import importlib.util
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "web_skill/skill/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
