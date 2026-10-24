# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Source/docs absence checks. No browser, subprocess or network is used."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def repository_sources():
    return [ROOT / name for name in ("README.md", "INSTALL.md", "CLAUDE.md", "pyproject.toml", "uv.lock")] + [
        p for p in (ROOT / "web_skill").rglob("*") if p.suffix in (".py", ".md")]


def test_no_legacy_browser_credential_paths():
    forbidden = ("opencli", "browser_cookie3", "browser-cookie3", "cookies-from-browser", "Safe Storage")
    for path in repository_sources():
        text = path.read_text(encoding="utf-8").casefold()
        for word in forbidden:
            assert word.casefold() not in text, f"{path}: {word}"
            assert word.casefold() not in path.name.casefold(), str(path)


def test_no_social_cli_instructions_or_invocations():
    for path in repository_sources():
        text = path.read_text(encoding="utf-8")
        for command in ("rdt status", "twitter status", "xhs status", "rdt login", "xhs login",
                        "cookie-source", "TWITTER_BROWSER", "auto-extract"):
            assert command not in text, f"{path}: {command}"


def test_fallback_does_not_add_description_triggers():
    text = (ROOT / "web_skill/skill/SKILL.md").read_text()
    frontmatter = text.split("---", 2)[1]
    assert "MUST USE for: video transcript" in frontmatter
    assert "recommending videos to watch" in frontmatter
    assert "any other site" not in frontmatter.lower()
    assert "读任意网页" not in frontmatter
    assert "tools/web.md" in text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
