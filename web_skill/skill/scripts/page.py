# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Read an http(s) page using installed Chrome and web-skill's own profile.

Usage: uv run page.py URL [--selector CSS] [--links] [--wait SECONDS]
Manual login: uv run page.py --login URL
"""
import argparse
import math
import sys
from urllib.parse import urlsplit

import browser


def read_page(url, selector=None, links=False, wait=0):
    browser.validate_url(url)
    if not math.isfinite(wait) or wait < 0:
        raise ValueError("wait must be a finite, non-negative number of seconds")
    with browser.browser_context() as context:
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if wait:
            page.wait_for_timeout(wait * 1000)
        browser.validate_url(page.url)
        target = page.locator(selector or "body")
        if not target.count():
            raise RuntimeError(f"no matches for selector: {selector or 'body'}")
        result = {"title": page.title(), "url": page.url,
                  "text": "\n\n".join(target.all_inner_texts())}
        if links:
            items = page.locator("a[href]").evaluate_all(
                "nodes => nodes.map(a => ({text: a.innerText, url: a.href}))")
            result["links"] = [item for item in items
                               if urlsplit(item["url"]).scheme in ("http", "https")]
        return result


def login(url):
    browser.validate_url(url)
    with browser.browser_context(headless=False) as context:
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        input("Log in manually in this web-skill window, then press Enter here to close it: ")
    browser.record_login(url)
    print("Manual login recorded locally; remote session validity is not verified.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--selector", help="CSS selector (default: body)")
    parser.add_argument("--links", action="store_true", help="also print http(s) links")
    parser.add_argument("--wait", type=float, default=0, help="seconds after DOM load")
    parser.add_argument("--login", action="store_true", help="manual login in a visible, isolated window")
    args = parser.parse_args(argv)
    try:
        if args.login:
            login(args.url)
        else:
            result = read_page(args.url, args.selector, args.links, args.wait)
            print(f"Title: {result['title']}\nURL: {result['url']}\n\n{result['text']}")
            if args.links:
                print("\nLinks:")
                for link in result["links"]:
                    print(f"{link['text']}\t{link['url']}")
        return 0
    except ValueError as error:
        parser.error(str(error))
    except (Exception, KeyboardInterrupt) as error:
        print(f"page: {type(error).__name__}: {error}\n"
              "Close other web-skill browser windows before retrying if the profile is busy.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
