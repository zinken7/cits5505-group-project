# -*- coding: utf-8 -*-
from flask import request

from app.api.v1 import bp
from app.api.v1.common import api_response, validation_error
from app.services.watchlist_service import get_trending

VALID_TYPES = ("anime", "movie", "tvshow")


def _limit(default=20):
    raw = request.args.get("limit", default, type=int) or default
    return min(max(raw, 1), 100)


@bp.route("/trending", methods=["GET"])
def trending_list():
    media_type = request.args.get("type") or None
    if media_type and media_type not in VALID_TYPES:
        return validation_error("type must be anime, movie, or tvshow")
    limit = _limit(10)
    items = get_trending(media_type=media_type, limit=limit)
    return api_response(data=items, meta={"limit": limit, "type": media_type})


@bp.route("/leaderboards", methods=["GET"])
def leaderboards_root():
    t = request.args.get("type") or "anime"
    if t not in VALID_TYPES:
        return validation_error("type must be anime, movie, or tvshow")
    return _leaderboard(t)


@bp.route("/leaderboards/anime", methods=["GET"])
def leaderboards_anime():
    return _leaderboard("anime")


@bp.route("/leaderboards/tvshows", methods=["GET"])
def leaderboards_tvshows():
    return _leaderboard("tvshow")


@bp.route("/leaderboards/movies", methods=["GET"])
def leaderboards_movies():
    return _leaderboard("movie")


def _leaderboard(media_type):
    limit = _limit(20)
    items = get_trending(media_type=media_type, limit=limit)
    return api_response(data=items, meta={"type": media_type, "limit": limit})
