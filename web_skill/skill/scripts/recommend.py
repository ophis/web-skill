# /// script
# requires-python = ">=3.10"
# dependencies = ["browser-cookie3", "requests"]
# ///
"""Personalized recommendation candidates (Bilibili + YouTube) -> JSONL on stdout.

Read-only, no storage: recommendations are ephemeral, so fetch fresh each call. One candidate
per line: {platform, video_id, title, creator, creator_id, url, duration_sec, views, reason}.

Cookies are read live from the browser (--browser, default chrome):
  Bilibili - web rcmd API, needs the SESSDATA cookie.
  YouTube  - InnerTube `what_to_watch` feed, SAPISIDHASH-signed with the SAPISID cookie.
A separate consumer ranks these candidates against the user's tastes; this script only fetches.
"""
import argparse, hashlib, json, re, sys, time

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def cookiejar(browser, domain):
    import browser_cookie3
    fn = getattr(browser_cookie3, browser, None)
    if fn is None:
        raise RuntimeError(f"unsupported browser '{browser}'")
    return fn(domain_name=domain)


# ---------- parsing (pure) ----------
def parse_views(s):
    """'9,300,882 views' / '73K views' / '1.2M views' -> int; None / 'No views' -> None."""
    m = re.search(r"([\d.]+)\s*([kmb]?)", (s or "").lower().replace(",", ""))
    if not m:
        return None
    return int(float(m.group(1)) * {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(m.group(2), 1))


def parse_duration(s):
    """'2:01' -> 121, '1:02:03' -> 3723; None / non-numeric -> None."""
    parts = (s or "").split(":")
    if not s or not all(p.isdigit() for p in parts):
        return None
    sec = 0
    for p in parts:
        sec = sec * 60 + int(p)
    return sec


def _runs_text(o):
    return "".join(r.get("text", "") for r in (o or {}).get("runs", []))


# ---------- bilibili ----------
def norm_bili_rcmd(it):
    bvid = it.get("bvid")
    if not bvid:                       # skip ad / live / non-video cards
        return None
    owner = it.get("owner") or {}
    rr = it.get("rcmd_reason")
    return {
        "platform": "bilibili", "video_id": bvid, "title": it.get("title"),
        "creator": owner.get("name") or None,
        "creator_id": str(owner["mid"]) if owner.get("mid") else None,
        "url": f"https://www.bilibili.com/video/{bvid}",
        "duration_sec": it.get("duration"),
        "views": (it.get("stat") or {}).get("view"),
        "reason": rr.get("content") if isinstance(rr, dict) and rr.get("content") else None,
    }


def bili_candidates(browser, limit):
    import requests
    jar = cookiejar(browser, "bilibili.com")
    if not any(c.name == "SESSDATA" for c in jar):
        raise RuntimeError("no SESSDATA — log in at bilibili.com in the browser")
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    for c in jar:
        s.cookies.set(c.name, c.value)
    out, idx = [], 1
    while len(out) < limit and idx <= 8:   # rcmd returns ~10/page; page via fresh_idx
        d = s.get("https://api.bilibili.com/x/web-interface/index/top/rcmd",
                  params={"fresh_type": 3, "ps": 12, "fresh_idx": idx, "fresh_idx_1h": idx,
                          "feed_version": "V8", "homepage_ver": 1}, timeout=15).json()
        if d.get("code") != 0:
            raise RuntimeError(f"bili rcmd code={d.get('code')} {d.get('message')}")
        items = (d.get("data") or {}).get("item") or []
        if not items:
            break
        out += [r for r in map(norm_bili_rcmd, items) if r]
        idx += 1
    return out[:limit]


# ---------- youtube ----------
def sapisidhash(sapisid, origin, ts):
    return hashlib.sha1(f"{ts} {sapisid} {origin}".encode()).hexdigest()


def norm_yt_rec(vr):
    vid = vr.get("videoId")
    if not vid:
        return None
    owner = vr.get("ownerText") or vr.get("longBylineText") or {}
    runs = owner.get("runs") or []
    handle = None
    if runs:
        base = ((runs[0].get("navigationEndpoint") or {}).get("browseEndpoint") or {}).get("canonicalBaseUrl") or ""
        if base.startswith("/@"):
            handle = base[1:]
    return {
        "platform": "youtube", "video_id": vid, "title": _runs_text(vr.get("title")),
        "creator": _runs_text(owner) or None, "creator_id": handle,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "duration_sec": parse_duration((vr.get("lengthText") or {}).get("simpleText")),
        "views": parse_views((vr.get("viewCountText") or {}).get("simpleText")),
        "reason": None,
    }


def norm_yt_lockup(lv):
    """Current YouTube home shape: `lockupViewModel` (replaced `videoRenderer`)."""
    if lv.get("contentType") != "LOCKUP_CONTENT_TYPE_VIDEO":   # skip playlists / shorts
        return None
    vid = lv.get("contentId")
    if not vid:
        return None
    m = (lv.get("metadata") or {}).get("lockupMetadataViewModel") or {}
    rows = ((m.get("metadata") or {}).get("contentMetadataViewModel") or {}).get("metadataRows") or []
    parts = [p.get("text", {}).get("content") for row in rows for p in (row.get("metadataParts") or [])]
    parts = [p for p in parts if p]
    handle = next((b[1:] for b in _walk(m.get("image") or {}, "canonicalBaseUrl")
                   if isinstance(b, str) and b.startswith("/@")), None)
    dur = next((b.get("text") for b in _walk(lv.get("contentImage") or {}, "thumbnailBadgeViewModel")
                if b.get("text") and ":" in b["text"]), None)
    return {
        "platform": "youtube", "video_id": vid, "title": (m.get("title") or {}).get("content"),
        "creator": parts[0] if parts else None, "creator_id": handle,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "duration_sec": parse_duration(dur),
        "views": next((parse_views(p) for p in parts if "view" in p.lower()), None),
        "reason": None,
    }


def _walk(o, key):
    if isinstance(o, dict):
        if key in o:
            yield o[key]
        for v in o.values():
            yield from _walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v, key)


def _continuation(data):
    for ci in _walk(data, "continuationItemRenderer"):
        tok = ((ci.get("continuationEndpoint") or {}).get("continuationCommand") or {}).get("token")
        if tok:
            return tok
    return None


def youtube_candidates(browser, limit):
    import requests
    ck = {c.name: c.value for c in cookiejar(browser, "youtube.com")}
    sapisid = ck.get("SAPISID") or ck.get("__Secure-3PAPISID")
    if not sapisid:
        raise RuntimeError("no SAPISID cookie — log in at youtube.com in the browser")
    origin, ts = "https://www.youtube.com", int(time.time())
    headers = {"Authorization": f"SAPISIDHASH {ts}_{sapisidhash(sapisid, origin, ts)}",
               "Origin": origin, "X-Origin": origin, "Content-Type": "application/json", "User-Agent": UA}
    ctx = {"client": {"clientName": "WEB", "clientVersion": "2.20240101.00.00", "hl": "en", "gl": "US"}}
    payload = {"context": ctx, "browseId": "FEwhat_to_watch"}
    out, seen, legacy, pages = [], set(), [], 0
    while len(out) < limit and pages < 6:
        data = requests.post("https://www.youtube.com/youtubei/v1/browse?prettyPrint=false",
                             headers=headers, json=payload, cookies=ck, timeout=20).json()
        for lv in _walk(data, "lockupViewModel"):                    # current personalized home shape
            r = norm_yt_lockup(lv)
            if r and r["video_id"] not in seen:
                seen.add(r["video_id"])
                out.append(r)
        legacy += [norm_yt_rec(vr) for vr in _walk(data, "videoRenderer")]   # legacy shape, fallback only
        tok = _continuation(data)
        pages += 1
        if not tok:
            break
        payload = {"context": ctx, "continuation": tok}
    if not out:                                                      # account still served the old shape
        for r in legacy:
            if r and r["video_id"] not in seen:
                seen.add(r["video_id"])
                out.append(r)
    return out[:limit]


FETCHERS = {"bilibili": bili_candidates, "youtube": youtube_candidates}


def main():
    ap = argparse.ArgumentParser(description="Fetch recommendation candidates as JSONL (no storage).")
    ap.add_argument("--platform", choices=["bilibili", "youtube", "both"], default="both")
    ap.add_argument("--limit", type=int, default=20, help="candidates per platform")
    ap.add_argument("--browser", default="chrome", help="browser to read cookies from")
    args = ap.parse_args()
    platforms = ["bilibili", "youtube"] if args.platform == "both" else [args.platform]
    failed = 0
    for p in platforms:
        try:
            for rec in FETCHERS[p](args.browser, args.limit):
                print(json.dumps(rec, ensure_ascii=False))
        except Exception as e:
            failed += 1
            print(f"{p}: ERROR {e}", file=sys.stderr)
    sys.exit(1 if failed == len(platforms) else 0)   # fail only if every platform failed


if __name__ == "__main__":
    main()
