# -*- coding: utf-8 -*-
"""Download all media poster images to app/static/posters/.

Usage:
    .venv/bin/python scripts/download_posters.py
"""
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.media import Media

POSTER_DIR = os.path.join(
    os.path.dirname(__file__), "..", "app", "static", "posters"
)


def download():
    app = create_app()
    os.makedirs(POSTER_DIR, exist_ok=True)

    with app.app_context():
        items = Media.query.filter(
            Media.image_url.isnot(None), Media.image_url != ""
        ).all()

        total = len(items)
        downloaded = 0
        skipped = 0
        failed = 0

        print(f"📥 Downloading {total} posters to {POSTER_DIR}")

        for i, m in enumerate(items, 1):
            # Use imdb_id as filename (unique, clean)
            ext = ".jpg"
            filename = f"{m.imdb_id}{ext}"
            filepath = os.path.join(POSTER_DIR, filename)

            # Skip if already downloaded
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                skipped += 1
                continue

            try:
                req = urllib.request.Request(
                    m.image_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = resp.read()

                with open(filepath, "wb") as f:
                    f.write(data)

                downloaded += 1
                print(f"  [{i}/{total}] ✅ {m.title} ({len(data)//1024}KB)")

                # Be nice to the CDN
                time.sleep(0.1)

            except Exception as e:
                failed += 1
                print(f"  [{i}/{total}] ❌ {m.title}: {e}")

        print(f"\n📊 Done: {downloaded} downloaded, {skipped} skipped, {failed} failed")
        print(f"📁 Posters directory: {os.path.abspath(POSTER_DIR)}")


if __name__ == "__main__":
    download()
