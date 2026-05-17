# -*- coding: utf-8 -*-
"""Fetch and parse IMDb title data from the page's embedded __NEXT_DATA__ JSON."""
import json
import re
import urllib.parse
import urllib.request

_IMDB_ID_RE = re.compile(r'\b(tt\d{7,10})\b')
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# IMDb titleType.id → our media_type
_TYPE_MAP = {
    "movie": "movie",
    "tvMovie": "movie",
    "tvSpecial": "movie",
    "tvShort": "movie",
    "short": "movie",
    "video": "movie",
    "tvSeries": "tvshow",
    "tvMiniSeries": "tvshow",
}

# Normalise whatever IMDb returns in productionStatus to our three choices
_STATUS_NORM = {
    "released": "Released",
    "completed": "Completed",
    "ongoing": "Ongoing",
}


def parse_imdb_id(raw):
    """Extract a tt-ID from a URL or bare string. Returns the ID or None."""
    m = _IMDB_ID_RE.search(raw or "")
    return m.group(1) if m else None


def _make_driver():
    """Create a headless Chrome WebDriver with the same options as enrich_media.py."""
    import os
    import shutil

    from selenium import webdriver as wd
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument(f"--user-agent={_UA}")

    # In Docker/Linux, Chromium may be at /usr/bin/chromium instead of google-chrome
    for binary in ("/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if os.path.exists(binary):
            opts.binary_location = binary
            break

    # Resolve chromedriver: prefer chromium-driver location used by Debian packages
    driver_path = shutil.which("chromedriver") or shutil.which("chromium-driver")
    service = Service(executable_path=driver_path) if driver_path else None
    return wd.Chrome(options=opts, service=service) if service else wd.Chrome(options=opts)


def _fetch_next_data(imdb_id):
    """Fetch IMDb title page via headless Chrome and return the __NEXT_DATA__ dict, or {}."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    url = f"https://www.imdb.com/title/{imdb_id}/"
    driver = None
    try:
        driver = _make_driver()
        driver.get(url)
        el = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
        )
        return json.loads(el.get_attribute("innerHTML"))
    except Exception:
        return {}
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _get(obj, *keys, default=None):
    """Walk a nested dict path safely. Returns default if any key is missing."""
    for key in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key)
        if obj is None:
            return default
    return obj


def _extract_fields(nd, imdb_id):
    """Parse __NEXT_DATA__ into a flat dict of Media fields. Returns {} on failure."""
    page_props = _get(nd, "props", "pageProps") or {}
    above = page_props.get("aboveTheFoldData") or {}
    main_data = page_props.get("mainColumnData") or {}

    if not above:
        return {}

    # Title
    title = _get(above, "titleText", "text") or ""
    if not title:
        return {}

    # Year
    year = _get(above, "releaseYear", "year")

    # Media type
    title_type_id = _get(above, "titleType", "id") or "movie"
    media_type = _TYPE_MAP.get(title_type_id, "movie")

    # Genres
    genres_data = _get(above, "genres", "genres") or []
    genres = [g["text"] for g in genres_data if isinstance(g, dict) and g.get("text")]

    # Anime detection: country of origin is Japan + genre includes Animation
    countries_list = _get(above, "countriesOfOrigin", "countries") or []
    country_ids = set()
    if isinstance(countries_list, list):
        for c in countries_list:
            if isinstance(c, dict):
                country_ids.add(c.get("id") or "")
    if {"JP"} & country_ids and "Animation" in genres:
        media_type = "anime"

    # Description
    description = _get(above, "plot", "plotText", "plainText") or ""

    # Poster image
    image_url = _get(above, "primaryImage", "url") or ""

    # Rating / votes
    rating = _get(above, "ratingsSummary", "aggregateRating")
    votes = _get(above, "ratingsSummary", "voteCount")

    # Country (first)
    country = None
    if isinstance(countries_list, list) and countries_list:
        c0 = countries_list[0]
        if isinstance(c0, dict):
            country = c0.get("text") or c0.get("id")

    # Language (first spoken)
    language = None
    langs = _get(main_data, "spokenLanguages", "spokenLanguages") or []
    if isinstance(langs, list) and langs:
        l0 = langs[0]
        if isinstance(l0, dict):
            language = l0.get("text") or l0.get("id")

    # Director / creator
    director = None
    pc = above.get("principalCreditsV2") or []
    if isinstance(pc, list):
        for group in pc:
            if not isinstance(group, dict):
                continue
            label = (_get(group, "grouping", "text") or "").lower()
            if label in ("director", "directors", "creator", "creators"):
                credits = group.get("credits") or []
                names = [
                    _get(c, "name", "nameText", "text")
                    for c in credits if isinstance(c, dict)
                ]
                director = ", ".join(n for n in names if n)[:200] or None
                break

    # Cast (top billed)
    cast = []
    cast_v2 = main_data.get("castV2") or []
    if isinstance(cast_v2, list):
        for group in cast_v2:
            if not isinstance(group, dict):
                continue
            credits = group.get("credits") or []
            names = [_get(c, "name", "nameText", "text") for c in credits[:8] if isinstance(c, dict)]
            cast = [n for n in names if n]
            if cast:
                break
    if not cast and isinstance(pc, list):
        for group in pc:
            if not isinstance(group, dict):
                continue
            if (_get(group, "grouping", "text") or "").lower() == "stars":
                credits = group.get("credits") or []
                names = [_get(c, "name", "nameText", "text") for c in credits[:8] if isinstance(c, dict)]
                cast = [n for n in names if n]
                break

    # Runtime
    runtime_minutes = None
    for section in (above, main_data):
        secs = _get(section, "runtime", "seconds")
        if secs:
            runtime_minutes = secs // 60
            break

    # Episode count (TV / anime)
    episodes = None
    ep_section = main_data.get("episodes") or {}
    if isinstance(ep_section, dict):
        te = ep_section.get("totalEpisodes")
        if isinstance(te, dict):
            episodes = te.get("total")
        elif isinstance(te, int):
            episodes = te
    if episodes is None:
        episodes = _get(above, "series", "episodeCount")

    # Release status — normalise to our three choices
    release_status = None
    for section in (above, main_data):
        s = _get(section, "productionStatus", "currentProductionStage", "text") or ""
        if s:
            release_status = _STATUS_NORM.get(s.lower())
            break

    # Tagline
    tagline = None
    edges = _get(main_data, "taglines", "edges") or []
    if isinstance(edges, list) and edges:
        tagline = _get(edges[0], "node", "text")

    # Awards summary
    awards = None
    wins = (_get(main_data, "wins", "total") or 0)
    noms = (_get(main_data, "nominationsExcludeWins", "total") or 0)
    if wins or noms:
        awards = f"{wins} wins & {noms} nominations total"

    return {
        "title": title,
        "media_type": media_type,
        "year": year,
        "description": description,
        "image_url": image_url,
        "imdb_id": imdb_id,
        "imdb_url": f"https://www.imdb.com/title/{imdb_id}/",
        "rating": rating,
        "votes": votes,
        "genres": genres,
        "country": country,
        "language": language,
        "director": director,
        "cast": cast,
        "runtime_minutes": runtime_minutes,
        "episodes": episodes,
        "release_status": release_status,
        "tagline": tagline,
        "awards": awards,
    }


def _fetch_youtube_trailer(title, year, media_type):
    """Search YouTube and return the first matching video URL, or ''."""
    suffix = "anime trailer" if media_type == "anime" else "official trailer"
    query = f"{title} {year or ''} {suffix}".strip()
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": _UA,
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        ids = re.findall(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"', html)
        if ids:
            return f"https://www.youtube.com/watch?v={ids[0]}"
    except Exception:
        pass
    return ""


def lookup_imdb(url_or_id):
    """
    Parse URL/ID, fetch IMDb, extract fields, search for a YouTube trailer.
    Returns (fields_dict, None) on success or (None, error_str) on failure.
    """
    imdb_id = parse_imdb_id(url_or_id)
    if not imdb_id:
        return None, (
            "Invalid IMDb URL — expected format: "
            "https://www.imdb.com/title/tt0111161/"
        )

    nd = _fetch_next_data(imdb_id)
    if not nd:
        return None, "Could not reach IMDb. Please check the URL and try again."

    fields = _extract_fields(nd, imdb_id)
    if not fields:
        return None, "Could not find title information for that IMDb ID."

    fields["trailer_url"] = _fetch_youtube_trailer(
        fields["title"], fields.get("year"), fields["media_type"]
    )

    return fields, None
