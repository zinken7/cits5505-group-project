#!/usr/bin/env python3
"""
enrich_genres.py — Add genre data to anime and tvshow records.

Strategy
--------
1. Re-scrape the 2 source pages (anime list + tvshow chart) using Selenium.
   IMDb embeds full title metadata in <script id="__NEXT_DATA__"> — genres
   are extracted from there.  This is just 2 page loads (fast path).
2. For any titles still missing genres after step 1, visit each title's own
   IMDb page individually (slow path, ~2 s/title).
3. Write updated app/data/anime.json and app/data/tvshow.json.
4. Re-seed media via scripts/seeds.py --clear --media-only.

Usage
-----
    python scripts/enrich_genres.py             # enrich + reseed
    python scripts/enrich_genres.py --no-seed   # update JSON only
    python scripts/enrich_genres.py --no-headless  # show browser window
    python scripts/enrich_genres.py --dry-run   # print plan, change nothing
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "app" / "data"

# Source pages used to originally scrape anime / tvshow
SOURCES: dict[str, str] = {
    "anime":  "https://www.imdb.com/list/ls088526366/",
    "tvshow": "https://www.imdb.com/chart/toptv/",
}

WAIT = 15   # seconds for __NEXT_DATA__ to appear
RATE = 1.5  # seconds between individual-page requests


# ── Selenium helpers ──────────────────────────────────────────────────────────

def make_driver(headless: bool = True):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)


def fetch_next_data(driver, url: str) -> dict:
    """Load *url*, wait for __NEXT_DATA__, return parsed JSON (or {})."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    print(f"    ↳ GET {url}")
    driver.get(url)
    time.sleep(3)
    try:
        el = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
        )
        return json.loads(el.get_attribute("innerHTML"))
    except Exception as exc:
        print(f"    ⚠️  __NEXT_DATA__ not found: {exc}")
        return {}


# ── Genre extraction helpers ──────────────────────────────────────────────────

def _genres_from_node(node: dict) -> list[str]:
    """
    Try every known IMDb __NEXT_DATA__ shape for the genres field.
    Works for both chart / list pages and individual title pages.
    """
    # The title data may live directly in the node or under node["title"]
    candidates = [node, node.get("title", {})]

    for obj in candidates:
        if not isinstance(obj, dict):
            continue

        # Shape A  titleGenres.genres[].genre.text  (chart pages, most common)
        tg = obj.get("titleGenres", {})
        if isinstance(tg, dict):
            result = [
                g.get("genre", {}).get("text", "")
                for g in tg.get("genres", [])
                if isinstance(g, dict)
            ]
            result = [g for g in result if g]
            if result:
                return result

        # Shape B  genres.genres[].text  (some list & title pages)
        g2 = obj.get("genres", {})
        if isinstance(g2, dict):
            result = [
                (g.get("text", "") if isinstance(g, dict) else str(g))
                for g in g2.get("genres", [])
            ]
            result = [g for g in result if g]
            if result:
                return result

        # Shape C  genres as a plain list of strings
        g3 = obj.get("genres", [])
        if isinstance(g3, list) and g3 and isinstance(g3[0], str):
            return g3

        # Shape D  individual title page — aboveTheFoldData.genres.genres[].text
        above = obj.get("aboveTheFoldData", {})
        if isinstance(above, dict):
            ag = above.get("genres", {})
            if isinstance(ag, dict):
                result = [
                    (g.get("text", "") if isinstance(g, dict) else str(g))
                    for g in ag.get("genres", [])
                ]
                result = [g for g in result if g]
                if result:
                    return result

    return []


def _find_edges(obj, min_len: int = 10, depth: int = 0) -> list:
    """Recursively find the first 'edges' list with ≥ min_len items."""
    if depth > 8:
        return []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "edges" and isinstance(v, list) and len(v) >= min_len:
                return v
            found = _find_edges(v, min_len, depth + 1)
            if found:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_edges(item, min_len, depth + 1)
            if found:
                return found
    return []


def build_genre_map(next_data: dict) -> dict[str, list[str]]:
    """Return {imdb_id: [genres]} extracted from a chart/list page's __NEXT_DATA__."""
    page_props = next_data.get("props", {}).get("pageProps", {})
    edges = _find_edges(page_props)

    genre_map: dict[str, list[str]] = {}
    for edge in edges:
        node = edge if isinstance(edge, dict) else {}
        inner = node.get("node", node)
        # Resolve title object for the imdb_id
        title_obj = inner if "id" in inner else inner.get("title", inner)
        imdb_id = title_obj.get("id", "")
        if not imdb_id:
            continue
        genre_map[imdb_id] = _genres_from_node(inner)

    hit = sum(1 for v in genre_map.values() if v)
    print(f"    Source page: {hit}/{len(genre_map)} items with genres")
    return genre_map


def genres_from_title_page(driver, imdb_id: str) -> list[str]:
    """Visit /title/<imdb_id>/ and return genres."""
    nd = fetch_next_data(driver, f"https://www.imdb.com/title/{imdb_id}/")
    if not nd:
        return []
    page_props = nd.get("props", {}).get("pageProps", {})
    # Pass the whole pageProps as a pseudo-node so _genres_from_node can search it
    return _genres_from_node(page_props)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def enrich(*, dry_run: bool, no_seed: bool, headless: bool) -> None:
    print("=" * 60)
    print("🎭 Genre Enrichment Script")
    print("=" * 60)

    driver = make_driver(headless)

    try:
        for media_type, source_url in SOURCES.items():
            json_path = DATA_DIR / f"{media_type}.json"
            print(f"\n{'─'*60}")
            print(f"  {media_type.upper()}  ←  {source_url}")
            print(f"{'─'*60}")

            with open(json_path, encoding="utf-8") as f:
                items: list[dict] = json.load(f)
            print(f"  {len(items)} records loaded")

            by_id = {item["imdb_id"]: item for item in items if item.get("imdb_id")}

            # ── Fast path: source-page __NEXT_DATA__ ──────────────────
            print("  [1/2] Extracting genres from source page…")
            nd = fetch_next_data(driver, source_url)
            genre_map = build_genre_map(nd)

            no_genre: list[str] = []
            for item in items:
                iid = item.get("imdb_id", "")
                if not iid:
                    continue
                genres = genre_map.get(iid, [])
                if genres:
                    item["genres"] = genres
                else:
                    no_genre.append(iid)

            # ── Slow path: individual title pages ─────────────────────
            if no_genre:
                print(f"  [2/2] Fetching {len(no_genre)} individual title pages…")
                for i, iid in enumerate(no_genre, 1):
                    print(f"    [{i:>3}/{len(no_genre)}] {iid}", end="  ", flush=True)
                    genres = genres_from_title_page(driver, iid)
                    by_id[iid]["genres"] = genres
                    print(genres if genres else "(none)")
                    time.sleep(RATE)
            else:
                print("  [2/2] All genres found in source page — skipping individual fetches ✓")

            # ── Results ───────────────────────────────────────────────
            with_genres = sum(1 for item in items if item.get("genres"))
            print(f"\n  Result: {with_genres}/{len(items)} items have genres")
            print("  Sample:")
            for item in items[:5]:
                print(f"    • {item['title']!r:40s} → {item.get('genres', [])}")

            if not dry_run:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
                print(f"  💾 Saved {json_path.name}")
            else:
                print("  (dry-run: JSON not written)")

    finally:
        driver.quit()
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
    ap = argparse.ArgumentParser(description="Add genre data to anime/tvshow records")
    ap.add_argument("--dry-run",      action="store_true", help="Print plan, change nothing")
    ap.add_argument("--no-seed",      action="store_true", help="Update JSON only, skip DB seed")
    ap.add_argument("--no-headless",  action="store_true", help="Show browser window")
    args = ap.parse_args()

    enrich(dry_run=args.dry_run, no_seed=args.no_seed, headless=not args.no_headless)
