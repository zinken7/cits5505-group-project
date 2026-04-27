#!/usr/bin/env python3
from __future__ import annotations
"""
IMDb Scraper
------------
Crawl IMDB chart/list pages and save structured JSON.
Supports Top 250 Movies, Top TV Shows, and user-curated lists (e.g. anime).

Uses Selenium to load pages → parse <script id="__NEXT_DATA__"> for structured
data, falling back to HTML scraping if needed.

Usage:
    python scripts/imdb_top250.py
    python scripts/imdb_top250.py --url "https://www.imdb.com/chart/toptv/" --type tvshow -o app/data/tvshow.json
    python scripts/imdb_top250.py --url "https://www.imdb.com/list/ls088526366/" --type anime -o app/data/anime.json
    python scripts/imdb_top250.py --no-headless  # show browser window
"""

import argparse
import json
import sys
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Config ────────────────────────────────────────────────────────────────────

IMDB_TOP250_URL = "https://www.imdb.com/chart/top/?ref_=chtmvm_ql_3&view=detailed"
DEFAULT_OUTPUT = "./imdb.json"
WAIT_TIMEOUT = 15  # seconds
VALID_TYPES = ("movie", "anime", "tvshow")


# ── Driver setup ──────────────────────────────────────────────────────────────

def setup_driver(headless: bool = True) -> webdriver.Chrome:
    """Khởi tạo Chrome WebDriver (giống repo DAN3002)."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    return driver


# ── Data extraction ───────────────────────────────────────────────────────────

def extract_from_next_data(driver: webdriver.Chrome, is_list_page: bool = False) -> list[dict]:
    """
    Parse <script id="__NEXT_DATA__">.
    Supports both /chart/ pages and /list/ pages.
    """
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    script_el = wait.until(
        EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
    )
    raw_json = script_el.get_attribute("innerHTML")
    data = json.loads(raw_json)

    page_props = data.get("props", {}).get("pageProps", {})

    # Try list-specific paths first for /list/ pages, then chart paths
    if is_list_page:
        titles = _find_list_titles(page_props)
        if not titles:
            titles = _find_chart_titles(page_props)
    else:
        titles = _find_chart_titles(page_props)
        if not titles:
            titles = _find_list_titles(page_props)

    if not titles:
        print("⚠️  Không tìm thấy dữ liệu trong __NEXT_DATA__")
        print("    Đang thử phương pháp fallback: scrape trực tiếp từ HTML...")
        # Dump keys for debugging
        print(f"    pageProps keys: {list(page_props.keys())}")
        page_data = page_props.get("pageData", {})
        if page_data:
            print(f"    pageData keys: {list(page_data.keys())}")
        return []

    movies = []
    for idx, item in enumerate(titles, start=1):
        movie = _extract_movie_item(item, idx)
        if movie:
            movies.append(movie)

    return movies


def _find_chart_titles(page_props: dict) -> list:
    """
    Tìm danh sách phim trong cấu trúc __NEXT_DATA__ cho /chart/ pages.
    IMDb thay đổi cấu trúc thường xuyên, nên thử nhiều path.
    """
    # Path 1: pageProps.pageData.chartTitles.edges
    chart_data = (
        page_props
        .get("pageData", {})
        .get("chartTitles", {})
        .get("edges", [])
    )
    if chart_data:
        return chart_data

    # Path 2: Tìm recursive key "edges" trong pageProps
    result = _deep_find_key(page_props, "edges")
    if result and isinstance(result, list) and len(result) > 20:
        return result

    return []


def _find_list_titles(page_props: dict) -> list:
    """
    Tìm danh sách trong cấu trúc __NEXT_DATA__ cho /list/ pages.
    User-curated lists use a different structure than chart pages.
    """
    # Path 1: pageProps.listData.items or similar
    list_data = page_props.get("listData", {})
    if list_data:
        items = list_data.get("items", [])
        if items:
            return items
        titles = list_data.get("titles", {}).get("edges", [])
        if titles:
            return titles

    # Path 2: pageProps.pageData.predefinedList.titleListItemSearch.edges
    predefined = (
        page_props
        .get("pageData", {})
        .get("predefinedList", {})
    )
    if predefined:
        search = predefined.get("titleListItemSearch", {})
        edges = search.get("edges", [])
        if edges:
            return edges

    # Path 3: deep search for "edges" with a lower threshold for lists
    result = _deep_find_key(page_props, "edges", min_length=10)
    if result:
        return result

    # Path 4: deep search for "items"
    result = _deep_find_key(page_props, "items", min_length=10)
    if result:
        return result

    return []


def _deep_find_key(obj, target_key, max_depth=6, _depth=0, min_length=20):
    """Tìm kiếm đệ quy một key trong nested dict/list."""
    if _depth > max_depth:
        return None

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target_key and isinstance(value, list) and len(value) >= min_length:
                return value
            found = _deep_find_key(value, target_key, max_depth, _depth + 1, min_length)
            if found:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = _deep_find_key(item, target_key, max_depth, _depth + 1, min_length)
            if found:
                return found

    return None


import re

def _upgrade_image_url(url: str) -> str:
    """Convert IMDB thumbnail URL to full-resolution.

    IMDB URLs look like:
      ...@._V1_QL75_UX90_CR0,1,90,133_.jpg   (90px thumb)
    We strip the resize params to get the original:
      ...@._V1_.jpg
    """
    if not url or "._V1_" not in url:
        return url
    return re.sub(r'\._V1_.+\.(jpg|jpeg|png|webp)$', '._V1_.jpg', url, flags=re.IGNORECASE)


def _extract_movie_item(edge: dict, rank: int) -> dict | None:
    """
    Trích xuất thông tin phim từ 1 edge item.
    Giống cách _extract_movie_data() trong DAN3002 repo.
    """
    try:
        node = edge.get("node", edge)  # có thể node nằm trực tiếp

        # Tìm title object — cấu trúc có thể là node trực tiếp hoặc node.title
        title_obj = node if "titleText" in node else node.get("title", node)

        # Title
        title_text = title_obj.get("titleText", {})
        title = title_text.get("text", "") if isinstance(title_text, dict) else str(title_text)

        # Original title
        original_title_text = title_obj.get("originalTitleText", {})
        original_title = original_title_text.get("text", "") if isinstance(original_title_text, dict) else ""

        # Year
        release_year = title_obj.get("releaseYear", {})
        year = release_year.get("year", "") if isinstance(release_year, dict) else ""

        # Rating
        ratings = title_obj.get("ratingsSummary", {})
        rating = ratings.get("aggregateRating") if isinstance(ratings, dict) else None
        votes = ratings.get("voteCount", 0) if isinstance(ratings, dict) else 0

        # Plot / Description
        plot_data = title_obj.get("plot", {})
        description = ""
        if isinstance(plot_data, dict):
            plot_text = plot_data.get("plotText", {})
            if isinstance(plot_text, dict):
                description = plot_text.get("plainText", "")
            elif isinstance(plot_text, str):
                description = plot_text

        # Image — upgrade to full resolution
        primary_image = title_obj.get("primaryImage", {})
        image_url = ""
        if isinstance(primary_image, dict):
            image_url = _upgrade_image_url(primary_image.get("url", ""))

        # IMDb ID
        imdb_id = title_obj.get("id", "")

        if not title:
            return None

        return {
            "rank": rank,
            "imdb_id": imdb_id,
            "title": title,
            "original_title": original_title or title,
            "year": year,
            "rating": rating,
            "votes": votes,
            "description": description,
            "image_url": image_url,
            "imdb_url": f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "",
        }

    except Exception as e:
        print(f"  ⚠️  Lỗi parse phim rank #{rank}: {e}")
        return None


# ── Fallback: scrape HTML trực tiếp ──────────────────────────────────────────

def extract_from_html(driver: webdriver.Chrome) -> list[dict]:
    """
    Phương pháp dự phòng: scrape trực tiếp từ HTML nếu __NEXT_DATA__ không có.
    """
    movies = []

    # Tìm tất cả list item trong chart
    items = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")

    if not items:
        # Thử selector khác
        items = driver.find_elements(By.CSS_SELECTOR, "[data-testid='chart-layout-main-column'] li")

    print(f"  ↳ Tìm thấy {len(items)} phim từ HTML")

    for idx, item in enumerate(items, start=1):
        try:
            # Title
            title_el = item.find_elements(By.CSS_SELECTOR, "h3.ipc-title__text")
            if not title_el:
                title_el = item.find_elements(By.CSS_SELECTOR, "[class*='title']")
            title_raw = title_el[0].text if title_el else ""

            # Bỏ số thứ tự ở đầu (e.g., "1. The Shawshank Redemption")
            title = title_raw.split(". ", 1)[-1] if ". " in title_raw else title_raw

            # Image
            img_el = item.find_elements(By.TAG_NAME, "img")
            raw_img = img_el[0].get_attribute("src") if img_el else ""
            image_url = _upgrade_image_url(raw_img)

            # Year + rating từ metadata spans
            metadata_items = item.find_elements(By.CSS_SELECTOR, "span.cli-title-metadata-item")
            year = metadata_items[0].text if len(metadata_items) > 0 else ""

            # Rating
            rating_el = item.find_elements(By.CSS_SELECTOR, "span.ipc-rating-star--rating")
            rating = float(rating_el[0].text) if rating_el else None

            # Description (trong view=detailed, mô tả hiển thị dưới title)
            desc_el = item.find_elements(By.CSS_SELECTOR, ".ipc-html-content-inner-div")
            if not desc_el:
                desc_el = item.find_elements(By.CSS_SELECTOR, "[class*='plot'], [class*='description']")
            description = desc_el[0].text if desc_el else ""

            if not title:
                continue

            # Lấy link IMDb
            link_el = item.find_elements(By.CSS_SELECTOR, "a.ipc-title-link-wrapper")
            href = link_el[0].get_attribute("href") if link_el else ""
            imdb_id = ""
            if "/title/" in href:
                imdb_id = href.split("/title/")[1].split("/")[0]

            movies.append({
                "rank": idx,
                "imdb_id": imdb_id,
                "title": title,
                "original_title": title,
                "year": year,
                "rating": rating,
                "votes": 0,
                "description": description,
                "image_url": image_url,
                "imdb_url": f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else href,
            })

        except Exception as e:
            print(f"  ⚠️  Lỗi parse item #{idx}: {e}")
            continue

    return movies


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Crawl IMDB chart/list pages → JSON"
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"File output JSON (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--url",
        default=IMDB_TOP250_URL,
        help="IMDB URL to scrape (chart or list page)",
    )
    parser.add_argument(
        "--type",
        default="movie",
        choices=VALID_TYPES,
        help="Media type to tag each record with (default: movie)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show browser window",
    )
    args = parser.parse_args()

    is_list_page = "/list/" in args.url

    print("=" * 60)
    print("🎬 IMDB Scraper")
    print("=" * 60)
    print(f"🌐 URL:    {args.url}")
    print(f"🏷️  Type:   {args.type}")
    print(f"📁 Output: {args.output}")
    print(f"📄 Mode:   {'list' if is_list_page else 'chart'} page")
    print("=" * 60)

    # 1. Setup driver
    print("\n🚀 Starting browser...")
    driver = setup_driver(headless=not args.no_headless)

    try:
        # 2. Load page
        print(f"🌐 Loading page...")
        driver.get(args.url)
        time.sleep(3)

        # 3. Try __NEXT_DATA__ first
        print("\n🔍 Parsing __NEXT_DATA__...")
        movies = extract_from_next_data(driver, is_list_page=is_list_page)

        # 4. Fallback to HTML scraping
        if not movies:
            print("\n🔍 Falling back to HTML scraping...")
            movies = extract_from_html(driver)

        if not movies:
            print("\n❌ No data found! IMDB may have changed their structure.")
            print("   Try running with --no-headless to inspect.")
            sys.exit(1)

        # 5. Inject media_type
        for m in movies:
            m["media_type"] = args.type

        # 6. Save output
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        print(f"\n💾 Saving {len(movies)} items to {args.output}...")
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)

        # 7. Summary
        print("\n" + "=" * 60)
        print(f"✨ Done! Scraped {len(movies)} {args.type} items")
        print(f"📁 Saved to: {args.output}")
        print("=" * 60)

        # Preview
        print(f"\n📋 Preview (first 5):")
        for m in movies[:5]:
            desc_preview = m["description"][:60] + "..." if len(m.get("description", "")) > 60 else m.get("description", "")
            print(f"  {m['rank']}. {m['title']} ({m.get('year','?')}) ⭐ {m.get('rating','?')}")
            print(f"     📝 {desc_preview}")

    finally:
        driver.quit()
        print("\n🔒 Browser closed.")


if __name__ == "__main__":
    main()
