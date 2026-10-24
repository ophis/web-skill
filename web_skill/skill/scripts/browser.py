"""Shared isolated Chrome lifecycle. Importing this module never starts a browser.

The fixed profile belongs to web-skill, outside copied skill directories. No browser
discovery, credential import, system password integration or remote browser attachment.
"""
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit


def validate_url(url):
    try:
        parsed = urlsplit(url)
        valid = (parsed.scheme in ("http", "https") and parsed.hostname
                 and not parsed.username and not parsed.password)
        parsed.port  # reject malformed ports before starting Chrome
    except ValueError:
        valid = False
    if not valid or any(c.isspace() for c in url):
        raise ValueError("expected an http(s) URL without embedded credentials")
    return url


def _state_root():
    root = Path.home() / ".local" / "share" / "web-skill"
    for path in (root.parent.parent, root.parent, root, root / "chrome-profile",
                 root / "chrome-profile" / "Default", root / "logins.json"):
        if path.is_symlink():
            raise RuntimeError(f"refusing symlink in web-skill state: {path}")
    return root


def profile_dir():
    root = _state_root()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    root.chmod(0o700)
    profile = root / "chrome-profile"
    profile.mkdir(mode=0o700, exist_ok=True)
    profile.chmod(0o700)
    return profile


def _logins():
    try:
        value = json.loads((_state_root() / "logins.json").read_text(encoding="utf-8"))
        return value if isinstance(value, list) and all(isinstance(v, str) for v in value) else []
    except (OSError, ValueError):
        return []


def login_status(domain):
    """Local manual confirmation only; never a claim that remote auth is valid."""
    root = _state_root()
    return (root / "chrome-profile").is_dir() and domain in _logins()


def record_login(url):
    domain = urlsplit(validate_url(url)).hostname
    profile = profile_dir()
    values = sorted(set(_logins()) | {domain})
    path = profile.parent / "logins.json"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(values, stream)


def chrome_path():
    """Only installed Google Chrome, never a Playwright-managed browser download."""
    if sys.platform == "darwin":
        candidates = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                      Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    else:
        candidates = [Path("/opt/google/chrome/chrome"), Path("/usr/bin/google-chrome"),
                      Path("/usr/bin/google-chrome-stable")]
    return next((path for path in candidates if path.is_file()), None)


def read_route(route):
    request = route.request
    if request.method in ("GET", "HEAD") and urlsplit(request.url).scheme in ("http", "https"):
        route.continue_()
    else:
        route.abort()


def _guard_page(page):
    page.on("download", lambda download: download.cancel())
    page.on("popup", lambda popup: popup.close())
    page.on("dialog", lambda dialog: dialog.dismiss())


@contextmanager
def browser_context(headless=True):
    """One owned browser per invocation; closing persistent context closes Chrome.

    Only explicit manual login uses headless=False and permits user interactions.
    Chrome's default Playwright pipe transport is retained; no debugging server.
    """
    executable = chrome_path()
    if not executable:
        raise RuntimeError("Google Chrome is not installed; install it manually (no browser download performed)")
    profile = profile_dir()
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile), channel="chrome", executable_path=str(executable),
            headless=headless, accept_downloads=False, service_workers="block",
            args=["--remote-debugging-pipe", "--password-store=basic", "--use-mock-keychain",
                  "--disable-extensions", "--disable-background-networking", "--disable-sync"],
        )
        try:
            if headless:
                context.route("**/*", read_route)
                context.route_web_socket("**/*", lambda socket: socket.close())
                context.on("page", _guard_page)
                for page in context.pages:
                    _guard_page(page)
            yield context
        finally:
            context.close()
