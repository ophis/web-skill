# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Hermetic checks of browser ownership, launch and read-only guards."""
import json
import stat
import sys
from types import SimpleNamespace

import pytest

from _common import load

b = load("browser")


@pytest.fixture(autouse=True)
def isolated_home(monkeypatch, tmp_path):
    monkeypatch.setattr(b.Path, "home", lambda: tmp_path)


def test_profile_private_fixed_and_login_record():
    profile = b.profile_dir()
    assert profile == b.Path.home() / ".local/share/web-skill/chrome-profile"
    assert stat.S_IMODE(profile.stat().st_mode) == 0o700
    assert not b.login_status("x.com")
    b.record_login("https://x.com/home?secret=unused")
    assert b.login_status("x.com")
    record = profile.parent / "logins.json"
    assert json.loads(record.read_text()) == ["x.com"]
    assert stat.S_IMODE(record.stat().st_mode) == 0o600
    record.write_text("corrupt")
    assert not b.login_status("x.com")


def test_profile_rejects_symlink(tmp_path):
    outside = tmp_path / "ordinary-profile"
    outside.mkdir()
    root = tmp_path / ".local/share/web-skill"
    root.mkdir(parents=True)
    (root / "chrome-profile").symlink_to(outside, target_is_directory=True)
    with pytest.raises(RuntimeError, match="symlink"):
        b.profile_dir()
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("method,url,allowed", [
    ("GET", "https://example.com/", True), ("HEAD", "http://example.com/", True),
    ("POST", "https://example.com/action", False), ("GET", "file:///private", False),
    ("GET", "ftp://example.com/file", False),
])
def test_read_route(method, url, allowed):
    calls = []
    route = SimpleNamespace(request=SimpleNamespace(method=method, url=url),
                            continue_=lambda: calls.append("allow"),
                            abort=lambda: calls.append("block"))
    b.read_route(route)
    assert calls == ["allow" if allowed else "block"]


@pytest.mark.parametrize("failure", [None, RuntimeError, KeyboardInterrupt])
def test_pipe_launch_guards_and_cleanup(monkeypatch, failure):
    calls = {}
    class Context:
        pages = []
        def route(self, pattern, handler):
            calls["route"] = handler
        def route_web_socket(self, pattern, handler):
            ws = SimpleNamespace(close=lambda: calls.update(ws_closed=True))
            handler(ws)
        def on(self, event, handler):
            calls[event] = handler
        def close(self):
            calls["closed"] = True
    class Playwright:
        def __enter__(self):
            return SimpleNamespace(chromium=SimpleNamespace(launch_persistent_context=self.launch))
        def __exit__(self, *args):
            calls["stopped"] = True
        def launch(self, **kwargs):
            calls["launch"] = kwargs
            return Context()
    monkeypatch.setitem(sys.modules, "playwright.sync_api", SimpleNamespace(sync_playwright=Playwright))
    monkeypatch.setattr(b, "chrome_path", lambda: b.Path("/fake/Google Chrome"))
    def run():
        with b.browser_context() as ctx:
            assert isinstance(ctx, Context)
            if failure:
                raise failure()
    if failure:
        with pytest.raises(failure):
            run()
    else:
        run()
    opts = calls["launch"]
    assert opts["channel"] == "chrome" and opts["headless"]
    assert opts["user_data_dir"] == str(b.profile_dir())
    assert opts["accept_downloads"] is False and opts["service_workers"] == "block"
    assert "--remote-debugging-pipe" in opts["args"]
    assert "--use-mock-keychain" in opts["args"] and "--password-store=basic" in opts["args"]
    assert not any("remote-debugging-port" in arg for arg in opts["args"])
    assert calls["ws_closed"] and calls["closed"] and calls["stopped"]
    events = {}
    p = SimpleNamespace(on=lambda name, fn: events.update({name: fn}))
    calls["page"](p)
    events["download"](SimpleNamespace(cancel=lambda: events.update(cancelled=True)))
    assert events["cancelled"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
