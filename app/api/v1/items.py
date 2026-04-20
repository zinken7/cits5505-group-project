# -*- coding: utf-8 -*-
"""Item detail endpoint — merges Media + Item rows for the /items/<imdb_id> page."""
import os

from app.api.v1 import bp
from app.api.v1.common import api_response
from app.models.items import Item
from app.models.media import Media

_POSTER_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "static", "posters"
)


def _local_poster_url(media):
    """Prefer a locally-downloaded poster file; fall back to the remote CDN URL."""
    if media.imdb_id:
        filename = f"{media.imdb_id}.jpg"
        if os.path.exists(os.path.join(_POSTER_DIR, filename)):
            return f"/static/posters/{filename}"
    return media.image_url or ""


@bp.route("/items/<imdb_id>", methods=["GET"])
def get_item(imdb_id):
    media = Media.query.filter_by(imdb_id=imdb_id).first()
    if not media:
        return api_response(
            data=None, message="Item not found", success=False, status=404
        )

    item = Item.query.filter_by(imdb_id=imdb_id).first()
    detail = item.to_dict() if item else {
        "imdb_id": imdb_id,
        "genres": [],
        "runtime_minutes": None,
        "episodes": None,
        "status": None,
        "director": "",
        "cast": [],
        "language": "",
        "country": "",
        "tagline": "",
        "awards": "",
        "trailer_url": "",
        "watching_count": 0,
        "completed_count": 0,
        "planned_count": 0,
        "watchlist_count": 0,
    }

    merged = {
        # Media-side fields
        "media_id": media.id,
        "imdb_id": media.imdb_id,
        "title": media.title,
        "media_type": media.media_type,
        "description": media.description,
        "image_url": _local_poster_url(media),
        "year": media.year,
        "rating": media.rating,
        "votes": media.votes,
        "imdb_url": media.imdb_url,
        "rank": media.rank,
        # Item-side fields (override any collisions, but there shouldn't be any)
        **{k: v for k, v in detail.items() if k != "imdb_id"},
    }
    return api_response(data=merged)
