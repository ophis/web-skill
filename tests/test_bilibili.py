# /// script
# requires-python = ">=3.9"
# dependencies = ["pytest", "requests"]
# ///
"""Tests for tools/scripts/bilibili.py (pure logic only).

Run one file:  uv run tests/test_bilibili.py
Whole suite:   uv run --with pytest --with requests pytest tests/
Web-API paths (session, playurl, download) need live services — out of scope;
only BV-id extraction is tested. requests is a dep because bilibili.py imports
it at module top.
"""
import sys

import pytest

from _common import load

bilibili = load("bilibili")


# bvid() only hits the network for b23.tv short links; a full URL needs no session.
def test_bvid_full_url():
    assert bilibili.bvid(None, "https://www.bilibili.com/video/BV1xx411c7mD") == "BV1xx411c7mD"


def test_bvid_bare_with_query():
    assert bilibili.bvid(None, "BV1xx411c7mD?p=2") == "BV1xx411c7mD"


def test_bvid_missing_exits():
    with pytest.raises(SystemExit):
        bilibili.bvid(None, "https://www.bilibili.com/video/av12345")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
