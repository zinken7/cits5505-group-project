# -*- coding: utf-8 -*-
from flask import request

from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, parse_pagination, validation_error
from app.services.watchlist_service import get_trending


@bp.route("/reviews", methods=["POST"])
@api_login_required
def reviews_create():
    return api_response(
        data=None,
        message="Review storage not implemented yet",
        success=False,
        status=501,
    )


@bp.route("/reviews/<review_id>", methods=["PATCH"])
@api_login_required
def reviews_patch(review_id):
    return api_response(
        data=None,
        message="Review storage not implemented yet",
        success=False,
        status=501,
    )


@bp.route("/reviews/<review_id>", methods=["DELETE"])
@api_login_required
def reviews_delete(review_id):
    return api_response(
        data=None,
        message="Review storage not implemented yet",
        success=False,
        status=501,
    )


@bp.route("/follows", methods=["POST"])
@api_login_required
def follows_create():
    return api_response(
        data=None,
        message="Follows not implemented yet",
        success=False,
        status=501,
    )


@bp.route("/follows/<follow_id>", methods=["DELETE"])
@api_login_required
def follows_delete(follow_id):
    return api_response(
        data=None,
        message="Follows not implemented yet",
        success=False,
        status=501,
    )


@bp.route("/notifications", methods=["GET"])
@api_login_required
def notifications_list():
    limit, offset = parse_pagination(limit_default=20, max_limit=100)
    return api_response(
        data=[],
        meta={"limit": limit, "offset": offset, "total": 0},
        message="Notifications not implemented yet",
    )


@bp.route("/notifications/<notification_id>", methods=["PATCH"])
@api_login_required
def notifications_patch(notification_id):
    return api_response(
        data=None,
        message="Notifications not implemented yet",
        success=False,
        status=501,
    )


@bp.route("/notifications/read-all", methods=["PATCH"])
@api_login_required
def notifications_read_all():
    return api_response(data={"updated": 0}, message="Notifications not implemented yet")


@bp.route("/trending", methods=["GET"])
def trending_list():
    """Popular media across the catalog; optional filter by type (matches legacy GET /api/trending)."""
    media_type = request.args.get("type")
    if media_type and media_type not in ("anime", "game", "movie"):
        return validation_error("type must be anime, game, or movie")
    limit = _leaderboard_limit(10)
    items = get_trending(media_type=media_type or None, limit=limit)
    return api_response(
        data=items,
        meta={"limit": limit, "type": media_type},
    )


def _leaderboard_limit(default=20):
    raw = request.args.get("limit", default, type=int)
    if raw is None:
        raw = default
    return min(max(raw, 1), 100)


def _lb(media_type, status):
    limit = _leaderboard_limit(20)
    items = get_trending(media_type=media_type, limit=limit)
    return api_response(
        data=items,
        meta={
            "type": media_type,
            "status": status,
            "window": "monthly",
            "limit": limit,
        },
    )


@bp.route("/leaderboards", methods=["GET"])
def leaderboards_root():
    t = request.args.get("type") or "anime"
    status = request.args.get("status") or "watching"
    if t not in ("anime", "game", "movie"):
        return validation_error("type must be anime, game, or movie")
    return _lb(t, status)


@bp.route("/leaderboards/anime", methods=["GET"])
def leaderboards_anime():
    status = request.args.get("status") or "watching"
    return _lb("anime", status)


@bp.route("/leaderboards/games", methods=["GET"])
def leaderboards_games():
    status = request.args.get("status") or "watching"
    return _lb("game", status)


@bp.route("/leaderboards/movies", methods=["GET"])
def leaderboards_movies():
    status = request.args.get("status") or "watching"
    return _lb("movie", status)
