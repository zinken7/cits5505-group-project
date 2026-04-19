# -*- coding: utf-8 -*-
"""Landing page endpoints — lightweight, public, no auth needed."""
import os

from flask import jsonify, url_for
from sqlalchemy.sql.expression import func

from app.api.v1 import bp
from app.extensions import db
from app.models.media import Media

# Absolute path to downloaded posters
_POSTER_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "static", "posters"
)


def _local_poster_url(media):
    """Return local poster URL if file exists, else fall back to remote CDN."""
    if media.imdb_id:
        filename = f"{media.imdb_id}.jpg"
        filepath = os.path.join(_POSTER_DIR, filename)
        if os.path.exists(filepath):
            return f"/static/posters/{filename}"
    return media.image_url or ""


@bp.route("/landing/posters", methods=["GET"])
def landing_posters():
    """Return a shuffled list of image URLs for the Three.js landing scene.

    Response is a flat JSON array of objects with id, title, image_url, year, rating.
    Limited to 80 items (enough for ~8‑10 columns × ~8‑10 rows).
    Prefers local poster files; falls back to CDN URLs.
    """
    rows = (
        Media.query
        .filter(Media.image_url.isnot(None), Media.image_url != "")
        .order_by(func.random())
        .limit(80)
        .all()
    )
    data = [
        {
            "id": m.id,
            "title": m.title,
            "image_url": _local_poster_url(m),
            "year": m.year,
            "rating": m.rating,
        }
        for m in rows
    ]
    return jsonify(data)
