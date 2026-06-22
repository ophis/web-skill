# /// script
# requires-python = ">=3.9"
# dependencies = ["pytest"]
# ///
"""Tests for tools/scripts/transcript.py (pure logic only).

Run one file:  uv run tests/test_transcript.py
Whole suite:   uv run --with pytest --with requests pytest tests/
Network paths (caption fetch, yt-dlp) need live services — out of scope.
"""
import sys
import tempfile

import pytest

from _common import load

transcript = load("transcript")


@pytest.mark.parametrize("url, want", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),            # bare 11-char id
    ("https://example.com/no-id-here", None),
    ("too-short", None),                       # not 11 chars, no marker
])
def test_youtube_id(url, want):
    assert transcript.youtube_id(url) == want


def test_site_detection():
    assert transcript.is_youtube("https://youtu.be/x")
    assert transcript.is_youtube("https://www.youtube.com/watch?v=x")
    assert not transcript.is_youtube("https://vimeo.com/123")
    assert transcript.is_bilibili("https://www.bilibili.com/video/BV1xx411c7mD")
    assert transcript.is_bilibili("https://b23.tv/abc")
    assert not transcript.is_bilibili("https://youtu.be/x")


def test_vtt_to_text():
    vtt = (
        "WEBVTT\n"
        "Kind: captions\n"
        "Language: en\n"
        "\n"
        "1\n"
        "00:00:01.000 --> 00:00:04.000\n"
        "Hello <c>world</c>\n"      # cue tags stripped
        "\n"
        "2\n"
        "00:00:04.000 --> 00:00:06.000\n"
        "Hello world\n"             # consecutive duplicate -> collapsed
        "\n"
        "3\n"
        "00:00:06.000 --> 00:00:08.000\n"
        "Goodbye\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".vtt", delete=False, encoding="utf-8") as f:
        f.write(vtt)
        path = f.name
    assert transcript._vtt_to_text(path) == "Hello world Goodbye"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
