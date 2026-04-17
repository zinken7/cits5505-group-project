# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import (
    api_login_required,
    api_response,
    parse_pagination,
    parse_user_id,
    validation_error,
)
from app.extensions import db
from app.models.user import User
from app.services.watchlist_service import get_user_watchlist


def _can_view_watchlist(profile: User, viewer) -> bool:
    vis = profile.watchlist_visibility or "public"
    if vis == "public":
        return True
    if vis == "private":
        return viewer.is_authenticated and viewer.id == profile.id
    # followers — not implemented; treat as public for demo
    return True


def _filter_watchlist(
    items,
    status=None,
    media_type=None,
    q=None,
    sort="-updatedAt",
    limit=12,
    offset=0,
):
    out = list(items)
    if status:
        out = [i for i in out if i.get("status") == status]
    if media_type:
        out = [
            i
            for i in out
            if (i.get("media") or {}).get("media_type") == media_type
        ]
    if q:
        ql = q.lower()
        out = [
            i
            for i in out
            if ql in (i.get("media") or {}).get("title", "").lower()
        ]
    reverse = sort.startswith("-")
    sk = sort.lstrip("-")
    if sk in ("updatedAt", "createdAt", "created_at"):
        key = "created_at"

        def sort_key(x):
            return x.get(key) or ""

        out = sorted(out, key=sort_key, reverse=reverse)
    total = len(out)
    return out[offset : offset + limit], total


@bp.route("/users/me", methods=["GET"])
@api_login_required
def users_me_get():
    return api_response(data=current_user.to_dict())


@bp.route("/users/me", methods=["PATCH"])
@api_login_required
def users_me_patch():
    data = request.get_json(silent=True) or {}
    if "displayName" in data and data["displayName"] is not None:
        current_user.display_name = (data["displayName"] or "").strip() or None
    if "bio" in data:
        current_user.bio = data.get("bio")
    if "favoriteGenres" in data:
        current_user.favorite_genres = data.get("favoriteGenres")
    if "visibility" in data and isinstance(data["visibility"], dict):
        w = data["visibility"].get("watchlist")
        if w in ("public", "followers", "private"):
            current_user.watchlist_visibility = w
    db.session.commit()
    return api_response(data=current_user.to_dict(), message="Updated")


@bp.route("/users/<user_id>", methods=["GET"])
def users_public_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return api_response(data=None, message="Invalid user id", success=False, status=400)
    user = db.session.get(User, uid)
    if not user:
        return api_response(data=None, message="User not found", success=False, status=404)
    return api_response(data=user.to_public_dict())


@bp.route("/users/<user_id>/watchlist", methods=["GET"])
def users_watchlist_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return api_response(data=None, message="Invalid user id", success=False, status=400)
    profile = db.session.get(User, uid)
    if not profile:
        return api_response(data=None, message="User not found", success=False, status=404)
    if not _can_view_watchlist(profile, current_user):
        return api_response(data=None, message="Forbidden", success=False, status=403)

    status = request.args.get("status")
    media_type = request.args.get("mediaType")
    q = request.args.get("q")
    sort = request.args.get("sort") or "-updatedAt"
    limit, offset = parse_pagination(limit_default=12, max_limit=100)

    raw = get_user_watchlist(uid, status=None)
    items, total = _filter_watchlist(
        raw,
        status=status,
        media_type=media_type,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return api_response(
        data=items,
        meta={"limit": limit, "offset": offset, "total": total},
    )


@bp.route("/users/<user_id>/reviews", methods=["GET"])
def users_reviews_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    if not db.session.get(User, uid):
        return api_response(data=None, message="User not found", success=False, status=404)
    return api_response(
        data=[],
        meta={"limit": 0, "offset": 0, "total": 0},
        message="Reviews not implemented yet",
    )


@bp.route("/users/<user_id>/followers", methods=["GET"])
def users_followers_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    if not db.session.get(User, uid):
        return api_response(data=None, message="User not found", success=False, status=404)
    return api_response(data=[], message="Followers not implemented yet")


@bp.route("/users/<user_id>/following", methods=["GET"])
def users_following_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    if not db.session.get(User, uid):
        return api_response(data=None, message="User not found", success=False, status=404)
    return api_response(data=[], message="Following not implemented yet")


@bp.route("/users/me/watchlist", methods=["GET"])
@api_login_required
def users_me_watchlist_get():
    items = get_user_watchlist(current_user.id)
    return api_response(data=items)


@bp.route("/users/me/reviews", methods=["GET"])
@api_login_required
def users_me_reviews_get():
    return api_response(data=[], message="Reviews not implemented yet")


@bp.route("/users/me/notifications", methods=["GET"])
@api_login_required
def users_me_notifications_get():
    return api_response(data=[], message="Notifications not implemented yet")
