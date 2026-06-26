# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Tests for skill/scripts/recommend.py (pure logic: parsers + normalizers).

Run one file:  uv run tests/test_recommend.py
Whole suite:   uv run --with pytest --with requests pytest tests/
Network paths (rcmd / InnerTube fetch) need a live login — out of scope.
"""
import sys

import pytest

from _common import load

r = load("recommend")


def test_parse_views():
    assert r.parse_views("9,300,882 views") == 9300882
    assert r.parse_views("73K views") == 73000
    assert r.parse_views("1.2M views") == 1200000
    assert r.parse_views("No views") is None
    assert r.parse_views(None) is None


def test_norm_yt_lockup():
    lv = {"contentType": "LOCKUP_CONTENT_TYPE_VIDEO", "contentId": "vid123",
          "metadata": {"lockupMetadataViewModel": {
              "title": {"content": "Cool Video"},
              "image": {"decoratedAvatarViewModel": {"rendererContext": {"commandContext": {"onTap":
                  {"innertubeCommand": {"browseEndpoint": {"canonicalBaseUrl": "/@cool"}}}}}}},
              "metadata": {"contentMetadataViewModel": {"metadataRows": [
                  {"metadataParts": [{"text": {"content": "Cool Channel"}}]},
                  {"metadataParts": [{"text": {"content": "73K views"}}, {"text": {"content": "1 month ago"}}]}]}}}},
          "contentImage": {"thumbnailViewModel": {"overlays": [{"thumbnailBottomOverlayViewModel":
              {"badges": [{"thumbnailBadgeViewModel": {"text": "1:15:40"}}]}}]}}}
    rec = r.norm_yt_lockup(lv)
    assert rec["video_id"] == "vid123" and rec["title"] == "Cool Video"
    assert rec["creator"] == "Cool Channel" and rec["creator_id"] == "@cool"
    assert rec["views"] == 73000 and rec["duration_sec"] == 4540   # 1:15:40
    assert rec["url"].endswith("watch?v=vid123")
    assert r.norm_yt_lockup({"contentType": "LOCKUP_CONTENT_TYPE_PLAYLIST", "contentId": "x"}) is None


def test_parse_duration():
    assert r.parse_duration("2:01") == 121
    assert r.parse_duration("1:02:03") == 3723
    assert r.parse_duration("LIVE") is None
    assert r.parse_duration(None) is None


def test_norm_bili_rcmd():
    rec = r.norm_bili_rcmd({"bvid": "BV1x", "title": "T", "owner": {"name": "U", "mid": 42},
                            "duration": 1220, "stat": {"view": 4184184},
                            "rcmd_reason": {"content": "7万点赞"}})
    assert rec["platform"] == "bilibili" and rec["video_id"] == "BV1x"
    assert rec["url"].endswith("BV1x") and rec["creator"] == "U" and rec["creator_id"] == "42"
    assert rec["views"] == 4184184 and rec["duration_sec"] == 1220 and rec["reason"] == "7万点赞"
    assert r.norm_bili_rcmd({"title": "ad", "bvid": ""}) is None   # no bvid → skipped


def test_norm_yt_rec():
    vr = {"videoId": "abc", "title": {"runs": [{"text": "Hello "}, {"text": "World"}]},
          "ownerText": {"runs": [{"text": "Cool",
                        "navigationEndpoint": {"browseEndpoint": {"canonicalBaseUrl": "/@cool"}}}]},
          "lengthText": {"simpleText": "2:01"}, "viewCountText": {"simpleText": "1,234 views"}}
    rec = r.norm_yt_rec(vr)
    assert rec["video_id"] == "abc" and rec["title"] == "Hello World"
    assert rec["creator"] == "Cool" and rec["creator_id"] == "@cool"
    assert rec["url"].endswith("watch?v=abc") and rec["duration_sec"] == 121 and rec["views"] == 1234
    assert r.norm_yt_rec({"title": {}}) is None   # no videoId → skipped


def test_sapisidhash_deterministic():
    a = r.sapisidhash("SECRET", "https://www.youtube.com", 1)
    assert a == r.sapisidhash("SECRET", "https://www.youtube.com", 1)
    assert len(a) == 40 and all(c in "0123456789abcdef" for c in a)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
