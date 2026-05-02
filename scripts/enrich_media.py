#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_media.py — Enrich anime / tvshow records with detail fields.

Visits each IMDb title page and extracts:
  runtime_minutes, episodes, release_status,
  director, cast, language, country, tagline, awards, trailer_url

Uses Selenium (via lazy init) for IMDb pages; plain urllib for YouTube search.

Usage:
    python scripts/enrich_media.py                  # enrich anime + tvshow + reseed
    python scripts/enrich_media.py --type anime     # only anime
    python scripts/enrich_media.py --type tvshow    # only tvshow
    python scripts/enrich_media.py --no-seed        # update JSON only
    python scripts/enrich_media.py --dry-run        # print plan, change nothing
    python scripts/enrich_media.py --limit 10       # only first N items
    python scripts/enrich_media.py --no-headless    # show browser window
    python scripts/enrich_media.py --resume         # skip already-enriched items
    python scripts/enrich_media.py --no-trailer     # skip YouTube trailer fetch
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "app" / "data"

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
RATE = 1.2   # seconds between requests
TIMEOUT = 20


# ── Fetch __NEXT_DATA__ ───────────────────────────────────────────────────────

def fetch_next_data_requests(imdb_id: str) -> dict:
    url = f"https://www.imdb.com/title/{imdb_id}/"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _UA,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        m = re.search(
            r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            html,
            re.DOTALL,
        )
        if m:
            return json.loads(m.group(1))
    except Exception as exc:
        print(f"      urllib failed: {exc}")
    return {}


def fetch_next_data_selenium(driver, imdb_id: str) -> dict:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    url = f"https://www.imdb.com/title/{imdb_id}/"
    try:
        driver.get(url)
        time.sleep(2)
        el = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
        )
        return json.loads(el.get_attribute("innerHTML"))
    except Exception as exc:
        # Print only the first line to avoid multi-line stacktrace noise
        print(f"      selenium failed: {str(exc).splitlines()[0]}")
        return {}


# ── Detail field extraction ───────────────────────────────────────────────────

def _text(obj, *keys, default=""):
    """Walk a nested dict path, returning a string or default."""
    for key in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key, {})
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("text", obj.get("plainText", default))
    return default


def extract_details(nd: dict) -> dict:
    """Pull all detail fields from a title page __NEXT_DATA__ dict."""
    page_props = nd.get("props", {}).get("pageProps", {})
    above = page_props.get("aboveTheFoldData", {})
    main = page_props.get("mainColumnData", {})

    result: dict = {}

    # ── runtime ──────────────────────────────────────────────────────────────
    # Try above first, then main
    for section in (above, main):
        rt = section.get("runtime", {})
        if isinstance(rt, dict) and rt.get("seconds"):
            result["runtime_minutes"] = rt["seconds"] // 60
            break

    # ── episodes (TV / anime) ─────────────────────────────────────────────────
    eps = None
    # Path A: mainColumnData.episodes.totalEpisodes (confirmed structure)
    ep_section = main.get("episodes", {})
    if isinstance(ep_section, dict):
        te = ep_section.get("totalEpisodes")
        if isinstance(te, dict):
            eps = te.get("total")
        elif isinstance(te, int):
            eps = te
        if eps is None:
            # fallback: .episodes.total
            inner = ep_section.get("episodes", {})
            if isinstance(inner, dict):
                eps = inner.get("total")
    # Path B: aboveTheFoldData.series.episodeCount
    if eps is None:
        series = above.get("series", {})
        if isinstance(series, dict):
            eps = series.get("episodeCount")
    if eps is not None:
        result["episodes"] = eps

    # ── release_status ────────────────────────────────────────────────────────
    status = (
        above
        .get("productionStatus", {})
        .get("currentProductionStage", {})
        .get("text", "")
    )
    if not status:
        status = (
            main
            .get("productionStatus", {})
            .get("currentProductionStage", {})
            .get("text", "")
        )
    if not status:
        # Infer from releaseYear.endYear
        ry = above.get("releaseYear", {})
        if isinstance(ry, dict):
            end = ry.get("endYear")
            status = "Ongoing" if end is None else "Ended"
    if status:
        result["release_status"] = status

    # ── language ──────────────────────────────────────────────────────────────
    # spokenLanguages is in mainColumnData as a dict with 'spokenLanguages' list
    sl_obj = main.get("spokenLanguages", {})
    if isinstance(sl_obj, dict):
        langs = sl_obj.get("spokenLanguages", [])
        if isinstance(langs, list) and langs:
            first = langs[0]
            result["language"] = first.get("text") or first.get("id", "")

    # ── country ───────────────────────────────────────────────────────────────
    # countriesOfOrigin is in aboveTheFoldData; id is the ISO code (e.g. "JP")
    countries = above.get("countriesOfOrigin", {}).get("countries", [])
    if isinstance(countries, list) and countries:
        c = countries[0]
        result["country"] = c.get("text") or c.get("id", "")

    # ── director / creator ────────────────────────────────────────────────────
    # principalCreditsV2 in above has groupings like Creator, Director, Stars
    pc = above.get("principalCreditsV2", [])
    if isinstance(pc, list):
        for group in pc:
            label = group.get("grouping", {}).get("text", "").lower()
            if label in ("director", "directors", "creator", "creators"):
                credits = group.get("credits", [])
                names = [
                    c.get("name", {}).get("nameText", {}).get("text", "")
                    for c in credits
                    if isinstance(c, dict)
                ]
                names = [n for n in names if n]
                if names:
                    result["director"] = ", ".join(names[:3])
                break

    # ── cast ──────────────────────────────────────────────────────────────────
    # castV2 in main is a list of groupings; find "Top Cast" group
    cast_v2 = main.get("castV2", [])
    if isinstance(cast_v2, list):
        for group in cast_v2:
            label = group.get("grouping", {}).get("text", "").lower()
            if "cast" in label or label == "":
                credits = group.get("credits", [])
                names = [
                    c.get("name", {}).get("nameText", {}).get("text", "")
                    for c in credits[:8]
                    if isinstance(c, dict)
                ]
                result["cast"] = [n for n in names if n]
                break
    # fallback: Stars group from principalCreditsV2
    if not result.get("cast") and isinstance(pc, list):
        for group in pc:
            label = group.get("grouping", {}).get("text", "").lower()
            if label == "stars":
                credits = group.get("credits", [])
                names = [
                    c.get("name", {}).get("nameText", {}).get("text", "")
                    for c in credits[:8]
                    if isinstance(c, dict)
                ]
                result["cast"] = [n for n in names if n]
                break

    # ── tagline ───────────────────────────────────────────────────────────────
    taglines = main.get("taglines", {})
    if isinstance(taglines, dict):
        edges = taglines.get("edges", [])
        if isinstance(edges, list) and edges:
            tl = edges[0].get("node", {}).get("text", "")
            if tl:
                result["tagline"] = tl

    # ── awards ────────────────────────────────────────────────────────────────
    wins = main.get("wins", {})
    noms = main.get("nominationsExcludeWins", {})
    if isinstance(wins, dict) and isinstance(noms, dict):
        w = wins.get("total", 0) or 0
        n = noms.get("total", 0) or 0
        if w or n:
            result["awards"] = f"{w} wins & {n} nominations total"

    return result


# ── YouTube trailer search ────────────────────────────────────────────────────

_YT_RATE = 0.8   # seconds between YouTube requests

def fetch_youtube_trailer(title: str, year=None, media_type: str = "") -> str:
    """Search YouTube and return the first matching video URL, or ''."""
    suffix = "anime trailer" if media_type == "anime" else "official trailer"
    query = f"{title} {year or ''} {suffix}".strip()
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _UA,
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        ids = re.findall(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"', html)
        if ids:
            return f"https://www.youtube.com/watch?v={ids[0]}"
    except Exception as exc:
        print(f"      YouTube search failed: {exc}")
    return ""


# ── Per-item enrichment ───────────────────────────────────────────────────────

def enrich_item(
    item: dict,
    driver=None,
    use_selenium: bool = False,
    fetch_trailer: bool = True,
) -> bool:
    """Fetch detail data for one item. Returns True if any field was set."""
    imdb_id = item.get("imdb_id", "")
    if not imdb_id:
        return False

    nd = {}
    if use_selenium and driver:
        nd = fetch_next_data_selenium(driver, imdb_id)
    if not nd:
        nd = fetch_next_data_requests(imdb_id)
    if not nd and driver:
        nd = fetch_next_data_selenium(driver, imdb_id)

    if not nd:
        return False

    details = extract_details(nd)
    if details:
        for k, v in details.items():
            item[k] = v

    # YouTube trailer (independent of IMDb fetch success)
    if fetch_trailer and not item.get("trailer_url"):
        time.sleep(_YT_RATE)
        trailer = fetch_youtube_trailer(
            title=item.get("title", ""),
            year=item.get("year"),
            media_type=item.get("media_type", ""),
        )
        if trailer:
            item["trailer_url"] = trailer

    return bool(details) or bool(item.get("trailer_url"))


# ── Main pipeline ─────────────────────────────────────────────────────────────

DETAIL_FIELDS = (
    "runtime_minutes", "episodes", "release_status",
    "director", "cast", "language", "country",
    "tagline", "awards", "trailer_url",
)

TYPES: dict[str, Path] = {
    "anime":  DATA_DIR / "anime.json",
    "tvshow": DATA_DIR / "tvshow.json",
}


CHECKPOINT_EVERY = 10   # save JSON every N items


def is_enriched(item: dict) -> bool:
    """Return True if the item already has at least one detail field populated."""
    return any(item.get(f) for f in DETAIL_FIELDS if f != "trailer_url")


def _make_driver(headless: bool):
    from selenium import webdriver as wd
    from selenium.webdriver.chrome.options import Options
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    return wd.Chrome(options=opts)


def _save(json_path: Path, items: list[dict]) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"  💾 Checkpoint saved → {json_path.name}", flush=True)


def run(
    *,
    types: list[str],
    dry_run: bool,
    no_seed: bool,
    limit: int | None,
    headless: bool,
    resume: bool,
    fetch_trailer: bool = True,
) -> None:
    print("=" * 60)
    print("🎬 Media Detail Enrichment")
    print("=" * 60)

    driver = None

    try:
        for media_type in types:
            json_path = TYPES[media_type]
            print(f"\n{'─'*60}")
            print(f"  {media_type.upper()}  ←  {json_path.name}")
            print(f"{'─'*60}")

            with open(json_path, encoding="utf-8") as f:
                items: list[dict] = json.load(f)

            # Ensure all detail fields exist (null if not set)
            for item in items:
                for field in DETAIL_FIELDS:
                    item.setdefault(field, None)

            targets = [i for i in items if i.get("imdb_id")]
            if resume:
                targets = [i for i in targets if not is_enriched(i)]
                print(f"  {len(targets)} items need enrichment (--resume mode)")
            else:
                print(f"  {len(targets)} items to enrich")

            if limit:
                targets = targets[:limit]
                print(f"  Limiting to first {limit} items")

            enriched = 0
            failed = 0

            for idx, item in enumerate(targets, 1):
                iid = item["imdb_id"]
                print(f"  [{idx:>3}/{len(targets)}] {iid}  {item.get('title','')[:45]}", end="  ", flush=True)

                if dry_run:
                    print("(dry-run)")
                    continue

                try:
                    ok = enrich_item(item, driver=driver, use_selenium=False, fetch_trailer=fetch_trailer)

                    # Lazy-init Selenium on first failure
                    if not ok and driver is None:
                        print("\n  ⚙️  Starting Selenium for fallback...", flush=True)
                        driver = _make_driver(headless)
                        ok = enrich_item(item, driver=driver, use_selenium=True, fetch_trailer=fetch_trailer)

                    # If driver exists but item still failed, maybe session is dead — recreate
                    elif not ok and driver is not None:
                        try:
                            driver.title  # probe: throws if session is dead
                        except Exception:
                            print("\n  ♻️  Recreating Selenium session...", flush=True)
                            try:
                                driver.quit()
                            except Exception:
                                pass
                            driver = _make_driver(headless)
                            ok = enrich_item(item, driver=driver, use_selenium=True, fetch_trailer=fetch_trailer)

                except Exception as exc:
                    print(f"(error: {str(exc).splitlines()[0]})")
                    failed += 1
                    # Save progress before continuing
                    if not dry_run:
                        _save(json_path, items)
                    time.sleep(RATE)
                    continue

                if ok:
                    enriched += 1
                    summary = []
                    if item.get("director"):
                        summary.append(f"dir={item['director'][:20]}")
                    if item.get("episodes"):
                        summary.append(f"eps={item['episodes']}")
                    if item.get("runtime_minutes"):
                        summary.append(f"rt={item['runtime_minutes']}m")
                    if item.get("trailer_url"):
                        summary.append("trailer=✓")
                    print(", ".join(summary) if summary else "ok")
                else:
                    failed += 1
                    print("(no data)")

                # Checkpoint every N items so progress survives a crash
                if not dry_run and idx % CHECKPOINT_EVERY == 0:
                    _save(json_path, items)

                time.sleep(RATE)

            print(f"\n  Result: {enriched} enriched, {failed} failed, {len(items) - len(targets)} skipped")

            if not dry_run:
                _save(json_path, items)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
            print("\n🔒 Browser closed")

    # ── Re-seed ───────────────────────────────────────────────────────────────
    if dry_run or no_seed:
        print("\n⏭  Seeding skipped.")
        return

    print("\n" + "=" * 60)
    print("🌱 Re-seeding media  (seeds.py --clear --media-only)")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "seeds.py"), "--clear", "--media-only"],
        cwd=str(ROOT),
    )
    if result.returncode == 0:
        print("\n✅ Database re-seeded successfully.")
    else:
        print("\n❌ Seeding exited with errors — check output above.")

    print("\n✨ Enrichment complete.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Enrich anime/tvshow with IMDb detail fields")
    ap.add_argument("--type",        choices=("anime", "tvshow"), help="Only this media type")
    ap.add_argument("--dry-run",     action="store_true", help="Print plan, change nothing")
    ap.add_argument("--no-seed",     action="store_true", help="Update JSON only, skip DB seed")
    ap.add_argument("--no-headless", action="store_true", help="Show browser window (Selenium fallback)")
    ap.add_argument("--limit",       type=int, help="Only process the first N items")
    ap.add_argument("--resume",      action="store_true", help="Skip items already enriched")
    ap.add_argument("--no-trailer",  action="store_true", help="Skip YouTube trailer fetch")
    args = ap.parse_args()

    run(
        types=[args.type] if args.type else ["anime", "tvshow"],
        dry_run=args.dry_run,
        no_seed=args.no_seed,
        limit=args.limit,
        headless=not args.no_headless,
        resume=args.resume,
        fetch_trailer=not args.no_trailer,
    )
