#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge imdb.json + items.json → app/data/movies.json.

Left-joins on imdb_id: all 250 records from imdb.json are kept,
enriched with detail fields from items.json where available.

Usage:
    python scripts/merge_movie_data.py
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")

IMDB_PATH = os.path.join(PROJECT_ROOT, "app", "imdb.json")
ITEMS_PATH = os.path.join(PROJECT_ROOT, "app", "items.json")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "app", "data", "movies.json")

# Detail fields to pull from items.json
DETAIL_FIELDS = (
    "runtime_minutes", "episodes", "release_status",
    "director", "cast", "language", "country",
    "tagline", "awards", "trailer_url",
)

# items.json uses "status" instead of "release_status"
JSON_FIELD_MAP = {"status": "release_status"}

# Fake stats to drop
DROP_FIELDS = {"watching_count", "completed_count", "planned_count"}


def merge():
    with open(IMDB_PATH, encoding="utf-8") as f:
        movies = json.load(f)

    with open(ITEMS_PATH, encoding="utf-8") as f:
        items = json.load(f)

    # Build lookup: imdb_id → detail record
    detail_map = {}
    for item in items:
        iid = item.get("imdb_id")
        if iid:
            detail_map[iid] = item

    enriched_count = 0
    merged = []

    for movie in movies:
        record = dict(movie)  # copy base fields
        record["media_type"] = "movie"

        # Initialize detail fields as null
        for field in DETAIL_FIELDS:
            record[field] = None

        # Enrich from items.json if matched
        iid = record.get("imdb_id")
        detail = detail_map.get(iid)
        if detail:
            enriched_count += 1
            for json_key in list(DETAIL_FIELDS) + list(JSON_FIELD_MAP.keys()):
                if json_key in detail:
                    model_key = JSON_FIELD_MAP.get(json_key, json_key)
                    if model_key in DETAIL_FIELDS:
                        record[model_key] = detail[json_key]

            # Prefer items.json genres if richer
            items_genres = detail.get("genres", [])
            base_genres = record.get("genres", [])
            if len(items_genres) > len(base_genres):
                record["genres"] = items_genres

        # Remove fake stats
        for key in DROP_FIELDS:
            record.pop(key, None)

        merged.append(record)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"✅ Merged {len(merged)} movies → {OUTPUT_PATH}")
    print(f"   Enriched with detail data: {enriched_count}/{len(merged)}")
    print(f"   Fields per record: {list(merged[0].keys())}")


if __name__ == "__main__":
    merge()
