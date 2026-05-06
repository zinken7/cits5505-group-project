# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user, logout_user

from app.api.v1 import bp
from app.api.v1.common import (
    api_login_required,
    api_response,
    parse_pagination,
    parse_user_id,
    validate_body,
)
from app.api.v1.schemas.users import UserMePatchSchema
from app.services.user_service import deactivate_user, get_user, update_user
from app.services.watchlist_service import filter_watchlist, get_user_watchlist


def _can_view_watchlist(profile, viewer) -> bool:
    vis = profile.watchlist_visibility or "public"
    if vis == "public":
        return True
    if vis == "private":
        return viewer.is_authenticated and viewer.id == profile.id
    return True


@bp.route("/users/me", methods=["GET"])
@api_login_required
def users_me_get():
    return api_response(data=current_user.to_dict())


@bp.route("/users/me", methods=["PATCH"])
@api_login_required
@validate_body(UserMePatchSchema)
def users_me_patch():
    from datetime import date as _date
    from app.models.user import User as _User

    data = request.get_json(silent=True) or {}
    kwargs = {}

    if "displayName" in data:
        kwargs["display_name"] = (data["displayName"] or "").strip() or None
    if "bio" in data:
        kwargs["bio"] = data["bio"]
    if "favoriteGenres" in data:
        kwargs["favorite_genres"] = data["favoriteGenres"]
    if "visibility" in data and isinstance(data["visibility"], dict):
        w = data["visibility"].get("watchlist")
        if w in ("public", "followers", "private"):
            kwargs["watchlist_visibility"] = w

    if "username" in data:
        new_username = str(data["username"]).strip().lower()
        if new_username != current_user.username:
            if _User.query.filter_by(username=new_username).first():
                return api_response(data=None, message="Username already taken", success=False, status=409)
            kwargs["username"] = new_username

    if "dateOfBirth" in data:
        dob = data["dateOfBirth"]
        kwargs["date_of_birth"] = _date.fromisoformat(str(dob)) if dob else None

    if "profilePublic" in data:
        kwargs["profile_public"] = bool(data["profilePublic"])

    if "allowFriendRequests" in data:
        kwargs["allow_friend_requests"] = bool(data["allowFriendRequests"])

    update_user(current_user, **kwargs)
    return api_response(data=current_user.to_dict(), message="Updated")


@bp.route("/users/me", methods=["DELETE"])
@api_login_required
def users_me_delete():
    try:
        deactivate_user(current_user)
    except ValueError as e:
        return api_response(data=None, message=str(e), success=False, status=400)
    logout_user()
    return api_response(data={"deactivated": True}, message="Account deactivated")


@bp.route("/users/me/watchlist", methods=["GET"])
@api_login_required
def users_me_watchlist_get():
    items = get_user_watchlist(current_user.id)
    return api_response(data=items)


@bp.route("/users/<user_id>", methods=["GET"])
def users_public_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return api_response(data=None, message="Invalid user id", success=False, status=400)
    user = get_user(uid)
    if not user:
        return api_response(data=None, message="User not found", success=False, status=404)
    return api_response(data=user.to_public_dict())


@bp.route("/users/<user_id>/watchlist", methods=["GET"])
def users_watchlist_get(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return api_response(data=None, message="Invalid user id", success=False, status=400)
    profile = get_user(uid)
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
    items, total = filter_watchlist(raw, status=status, media_type=media_type, q=q, sort=sort, limit=limit, offset=offset)
    return api_response(data=items, meta={"limit": limit, "offset": offset, "total": total})
