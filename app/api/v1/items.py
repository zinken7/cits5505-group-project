# -*- coding: utf-8 -*-
import os

from app.api.v1 import bp
from app.api.v1.common import api_response
from app.services.media_service import get_media_by_imdb_id
from app.services.watchlist_service import counts_for_imdb_id

_POSTER_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "posters")


def _resolve_image(media):
    """Prefer a locally-downloaded poster; fall back to the stored URL."""
    if media.imdb_id:
        local = os.path.join(_POSTER_DIR, f"{media.imdb_id}.jpg")
        if os.path.exists(local):
            return f"/static/posters/{media.imdb_id}.jpg"
    return media.image_url or ""


@bp.route("/items/<imdb_id>", methods=["GET"])
def get_item(imdb_id):
    media = get_media_by_imdb_id(imdb_id)
    if not media:
        return api_response(data=None, message="Item not found", success=False, status=404)

    counts = counts_for_imdb_id(imdb_id)
    data = media.to_detail_dict()
    data["image_url"] = _resolve_image(media)
    data["watching_count"] = counts["watching"]
    data["completed_count"] = counts["completed"]
    data["planned_count"] = counts["planned"]
    data["watchlist_count"] = counts["total"]

    return api_response(data=data)
