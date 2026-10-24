# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Offline doctor, CLI delegation, process-group cleanup and skill ownership."""
import os
from pathlib import Path
import signal
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from web_skill import cli, doctor, probe, skillreg
from web_skill.channels import get_all_channels
from web_skill.skill.scripts import browser


@pytest.fixture(autouse=True)
def fake_home(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)


def test_doctor_never_executes_social_or_browser(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail(f"doctor launched process: {args}")
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(browser, "chrome_path", lambda: Path("/fake/Chrome"))
    monkeypatch.setattr("shutil.which", lambda cmd: f"/fake/{cmd}")
    report = doctor.format_report(doctor.check_all())
    assert "web-skill login" in report
    browser.record_login("https://x.com")
    report = doctor.format_report(doctor.check_all())
    assert "not verified" in report
    for ch in get_all_channels():
        if ch.name != "video-transcript":
            assert ch.backends == ["Playwright"]


def test_probe_timeout_kills_group_and_reaps(monkeypatch):
    events = []
    class Process:
        pid = 12345
        def communicate(self, timeout=None):
            events.append(("communicate", timeout))
            if timeout is not None:
                raise subprocess.TimeoutExpired("fake", timeout)
            return ("", "")
    def popen(command, **kw):
        assert command == ["/fake", "--version"] and kw["start_new_session"]
        return Process()
    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(os, "killpg", lambda pid, sig: events.append((pid, sig)))
    result = probe._run_once("/fake", ["--version"], 1, "fake")
    assert result.status == "timeout"
    assert events == [("communicate", 1), (12345, signal.SIGKILL), ("communicate", None)]


def test_probe_interrupt_kills_group_and_reaps(monkeypatch):
    events = []
    class Process:
        pid = 12345
        def communicate(self, timeout=None):
            events.append(timeout)
            if timeout is not None:
                raise KeyboardInterrupt()
            return ("", "")
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: Process())
    monkeypatch.setattr(os, "killpg", lambda pid, sig: events.append((pid, sig)))
    with pytest.raises(KeyboardInterrupt):
        probe._run_once("/fake", [], 1, "fake")
    assert events == [1, (12345, signal.SIGKILL), None]


@pytest.mark.parametrize("code,status", [(0, "ok"), (127, "broken"), (1, "error")])
def test_probe_classification(monkeypatch, code, status):
    process = SimpleNamespace(returncode=code, communicate=lambda **kw: ("out", "err"))
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **kw: process)
    assert probe._run_once("/fake", [], 1, "fake").status == status


def test_cli_read_and_login(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda args, **kw: calls.append(args) or SimpleNamespace(returncode=0))
    assert cli.main(["login", "https://x.com"]) == 0
    assert calls[-1][:2] == ["uv", "run"]
    assert calls[-1][-2:] == ["--login", "https://x.com"]
    assert cli.main(["read", "https://example.com", "--selector", "main", "--links", "--wait", "2"]) == 0
    assert "--selector" in calls[-1] and "--links" in calls[-1]


def test_install_only_existing_video_dependencies(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(cli, "probe_command", lambda c: SimpleNamespace(status="ok"))
    installed = []
    monkeypatch.setattr(cli, "_brew", lambda name: installed.append(name))
    assert cli.install() == 0
    assert installed == ["uv", "ffmpeg"]


def test_skill_reinstall_keeps_profile(tmp_path, monkeypatch):
    profile = browser.profile_dir()
    (profile / "owned-state").write_text("keep")
    source = tmp_path / "bundled"
    source.mkdir()
    (source / "SKILL.md").write_text("new")
    target = tmp_path / ".claude/skills"
    target.mkdir(parents=True)
    monkeypatch.setattr(skillreg, "_skill_dirs", lambda: [target])
    monkeypatch.setattr(skillreg.ir, "files", lambda package: SimpleNamespace(__truediv__=lambda self, name: source))
    # Exercise the real copy operation twice; its target is outside the profile.
    skillreg._copy(source, target)
    skillreg._copy(source, target)
    assert (profile / "owned-state").read_text() == "keep"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
