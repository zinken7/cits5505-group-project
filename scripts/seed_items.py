# -*- coding: utf-8 -*-
"""Seed the Item table from app/items.json.

Each entry is keyed by `imdb_id` and only inserted if a matching Media
row already exists (run `python scripts/seed_media.py` first).

Usage:
    python scripts/seed_items.py          # upsert all entries
    python scripts/seed_items.py --clear  # wipe existing items, then import
"""
import json
import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.items import Item
from app.models.media import Media


def seed(clear: bool = False):
    app = create_app()

    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "items.json")
    with open(json_path, encoding="utf-8") as f:
        entries = json.load(f)

    with app.app_context():
        if clear:
            deleted = Item.query.delete()
            db.session.commit()
            print(f"[clear] Removed {deleted} existing item rows.")

        added = 0
        updated = 0
        orphaned = 0

        for entry in entries:
            imdb_id = entry.get("imdb_id")
            if not imdb_id:
                continue

            # Item rows must have a matching Media row (FK constraint)
            if not Media.query.filter_by(imdb_id=imdb_id).first():
                orphaned += 1
                continue

            existing = Item.query.filter_by(imdb_id=imdb_id).first()
            if existing:
                for key in (
                    "genres", "runtime_minutes", "episodes", "status",
                    "director", "cast", "language", "country", "tagline",
                    "awards", "trailer_url", "watching_count",
                    "completed_count", "planned_count",
                ):
                    if key in entry:
                        setattr(existing, key, entry[key])
                updated += 1
            else:
                db.session.add(Item(
                    imdb_id=imdb_id,
                    genres=entry.get("genres", []),
                    runtime_minutes=entry.get("runtime_minutes"),
                    episodes=entry.get("episodes"),
                    status=entry.get("status", "Released"),
                    director=entry.get("director", ""),
                    cast=entry.get("cast", []),
                    language=entry.get("language", ""),
                    country=entry.get("country", ""),
                    tagline=entry.get("tagline", ""),
                    awards=entry.get("awards", ""),
                    trailer_url=entry.get("trailer_url", ""),
                    watching_count=entry.get("watching_count", 0),
                    completed_count=entry.get("completed_count", 0),
                    planned_count=entry.get("planned_count", 0),
                ))
                added += 1

        db.session.commit()
        print(f"[ok] Added {added}, updated {updated} items. Skipped {orphaned} with no matching Media.")
        print(f"[db] Total items in DB: {Item.query.count()}")


if __name__ == "__main__":
    clear_flag = "--clear" in sys.argv
    seed(clear=clear_flag)
