# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Fake-only page reads and manual-login entry point."""
import sys
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from _common import load

p = load("page")


@pytest.mark.parametrize("url", ["", "file:///tmp/private", "javascript:alert(1)",
                                     "https://", "ftp://host", "https://u:p@host"])
def test_bad_url_before_launch(url, monkeypatch):
    monkeypatch.setattr(p.browser, "browser_context", lambda **kw: pytest.fail("browser launched"))
    with pytest.raises(ValueError):
        p.read_page(url)


@pytest.mark.parametrize("wait", [-1, float("nan"), float("inf")])
def test_bad_wait_before_launch(wait):
    with pytest.raises(ValueError):
        p.read_page("https://example.com", wait=wait)


def test_read_selector_links_and_close(monkeypatch):
    events = []
    class Locator:
        def count(self):
            return 1
        def all_inner_texts(self):
            return ["Example body"]
        def evaluate_all(self, script):
            return [{"text": "More", "url": "https://example.org/"},
                    {"text": "Mail", "url": "mailto:a@b"}]
    class Page:
        url = "https://example.com/final"
        def goto(self, url, **kwargs):
            events.append((url, kwargs))
        def wait_for_timeout(self, ms):
            events.append(ms)
        def title(self):
            return "Example"
        def locator(self, selector):
            events.append(selector)
            return Locator()
    @contextmanager
    def context(**kw):
        try:
            yield SimpleNamespace(new_page=lambda: Page())
        finally:
            events.append("closed")
    monkeypatch.setattr(p.browser, "browser_context", context)
    result = p.read_page("https://example.com", selector="main", links=True, wait=2)
    assert result == {"title": "Example", "url": "https://example.com/final",
                      "text": "Example body", "links": [{"text": "More", "url": "https://example.org/"}]}
    assert "main" in events and 2000 in events and events[-1] == "closed"


def test_missing_selector_and_navigation_failure_close(monkeypatch):
    closed = []
    page = SimpleNamespace(goto=lambda *a, **kw: None, url="https://example.com",
                           locator=lambda s: SimpleNamespace(count=lambda: 0))
    @contextmanager
    def context(**kw):
        try:
            yield SimpleNamespace(new_page=lambda: page)
        finally:
            closed.append(True)
    monkeypatch.setattr(p.browser, "browser_context", context)
    with pytest.raises(RuntimeError, match="selector"):
        p.read_page("https://example.com", selector=".absent")
    assert closed == [True]


def test_manual_login_only_records_after_confirmation(monkeypatch):
    events = []
    @contextmanager
    def context(**kw):
        assert kw == {"headless": False}
        try:
            yield SimpleNamespace(new_page=lambda: SimpleNamespace(goto=lambda *a, **kw: events.append("opened")))
        finally:
            events.append("closed")
    monkeypatch.setattr(p.browser, "browser_context", context)
    monkeypatch.setattr(p.browser, "record_login", lambda url: events.append("recorded"))
    monkeypatch.setattr("builtins.input", lambda message: events.append("confirmed"))
    p.login("https://x.com")
    assert events == ["opened", "confirmed", "closed", "recorded"]
    events.clear()
    def eof(message):
        raise EOFError()
    monkeypatch.setattr("builtins.input", eof)
    with pytest.raises(EOFError):
        p.login("https://x.com")
    assert events == ["opened", "closed"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
