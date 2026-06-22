# /// script
# requires-python = ">=3.9"
# dependencies = ["requests"]
# ///
"""Unit tests for the pure logic in tools/video-transcript/scripts/.

Run:  uv run tests/test_scripts.py        (plain asserts, no framework)
  or: uv run --with pytest pytest tests/  (same test_* functions)

Network/model paths (caption fetch, yt-dlp, STT models, Bilibili API) are NOT
covered — they need live services. stt.py has no importable pure functions
(logic runs at module import), so it is out of scope here.
"""
import importlib.util
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skill/tools/video-transcript/scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


transcript = _load("transcript")
bilibili = _load("bilibili")


def test_youtube_id():
    cases = {
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s": "dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ": "dQw4w9WgXcQ",
        "dQw4w9WgXcQ": "dQw4w9WgXcQ",  # bare 11-char id
    }
    for url, want in cases.items():
        assert transcript.youtube_id(url) == want, url
    assert transcript.youtube_id("https://example.com/no-id-here") is None
    assert transcript.youtube_id("too-short") is None  # not 11 chars, no marker


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


def test_bvid():
    # bvid() only touches the network for b23.tv short links; a full URL needs no session.
    assert bilibili.bvid(None, "https://www.bilibili.com/video/BV1xx411c7mD") == "BV1xx411c7mD"
    assert bilibili.bvid(None, "BV1xx411c7mD?p=2") == "BV1xx411c7mD"
    try:
        bilibili.bvid(None, "https://www.bilibili.com/video/av12345")
        assert False, "expected SystemExit on missing BV id"
    except SystemExit:
        pass


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} passed")
