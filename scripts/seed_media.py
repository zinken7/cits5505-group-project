# -*- coding: utf-8 -*-
"""Seed the Media table from app/imdb.json.

Usage:
    python scripts/seed_media.py          # import all 250 movies
    python scripts/seed_media.py --clear  # wipe existing media, then import
"""
import json
import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.media import Media


def seed(clear: bool = False):
    app = create_app()

    json_path = os.path.join(os.path.dirname(__file__), "..", "app", "imdb.json")
    with open(json_path, encoding="utf-8") as f:
        items = json.load(f)

    with app.app_context():
        if clear:
            deleted = Media.query.delete()
            db.session.commit()
            print(f"🗑  Cleared {deleted} existing media rows.")

        added = 0
        skipped = 0

        for item in items:
            # Skip if this imdb_id already exists
            if Media.query.filter_by(imdb_id=item["imdb_id"]).first():
                skipped += 1
                continue

            media = Media(
                title=item["title"],
                media_type="movie",  # IMDB Top 250 are all movies
                description=item.get("description", ""),
                image_url=item.get("image_url", ""),
                year=item.get("year"),
                imdb_id=item.get("imdb_id"),
                rating=item.get("rating"),
                votes=item.get("votes"),
                imdb_url=item.get("imdb_url", ""),
                rank=item.get("rank"),
            )
            db.session.add(media)
            added += 1

        db.session.commit()
        print(f"✅ Seeded {added} media items. Skipped {skipped} duplicates.")
        print(f"📊 Total media in DB: {Media.query.count()}")


if __name__ == "__main__":
    clear_flag = "--clear" in sys.argv
    seed(clear=clear_flag)
