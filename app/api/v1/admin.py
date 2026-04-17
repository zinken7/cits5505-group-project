# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import admin_required, api_response, parse_user_id, validation_error
from app.extensions import db
from app.models.user import User
from app.services.media_service import create_media, delete_media, get_media, update_media


@bp.route("/admin/users", methods=["GET"])
@admin_required
def admin_users_list():
    users = User.query.order_by(User.id.asc()).all()
    out = []
    for u in users:
        row = u.to_public_dict()
        row["email"] = u.email
        row["isAdmin"] = u.is_admin
        out.append(row)
    return api_response(data=out)


@bp.route("/admin/users/<user_id>", methods=["PATCH"])
@admin_required
def admin_users_patch(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    user = db.session.get(User, uid)
    if not user:
        return api_response(data=None, message="Not found", success=False, status=404)
    data = request.get_json(silent=True) or {}
    if "isAdmin" in data:
        user.is_admin = bool(data["isAdmin"])
    if "role" in data:
        user.is_admin = data.get("role") == "admin"
    db.session.commit()
    return api_response(data=user.to_dict())


@bp.route("/admin/users/<user_id>", methods=["DELETE"])
@admin_required
def admin_users_delete(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    user = db.session.get(User, uid)
    if not user:
        return api_response(data=None, message="Not found", success=False, status=404)
    if user.id == current_user.id:
        return api_response(data=None, message="Cannot delete yourself", success=False, status=400)
    db.session.delete(user)
    db.session.commit()
    return api_response(data={"deleted": True})


def _pid(raw):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


@bp.route("/admin/anime", methods=["POST"])
@admin_required
def admin_anime_create():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return validation_error("title is required")
    m = create_media(
        title=title,
        media_type="anime",
        description=data.get("description", ""),
        image_url=data.get("imageUrl", data.get("image_url", "")),
        year=data.get("year"),
    )
    return api_response(data=m.to_dict(), message="Created", status=201)


@bp.route("/admin/anime/<anime_id>", methods=["PATCH"])
@admin_required
def admin_anime_patch(anime_id):
    mid = _pid(anime_id)
    if mid is None:
        return validation_error("Invalid id")
    data = request.get_json(silent=True) or {}
    fields = {}
    if "title" in data:
        fields["title"] = data["title"]
    if "description" in data:
        fields["description"] = data["description"]
    if "imageUrl" in data or "image_url" in data:
        fields["image_url"] = data.get("imageUrl", data.get("image_url"))
    if "year" in data:
        fields["year"] = data["year"]
    m = update_media(mid, **fields)
    if not m or m.media_type != "anime":
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())


@bp.route("/admin/anime/<anime_id>", methods=["DELETE"])
@admin_required
def admin_anime_delete(anime_id):
    mid = _pid(anime_id)
    if mid is None:
        return validation_error("Invalid id")
    m = get_media(mid)
    if not m or m.media_type != "anime":
        return api_response(data=None, message="Not found", success=False, status=404)
    delete_media(mid)
    return api_response(data={"deleted": True})


@bp.route("/admin/games", methods=["POST"])
@admin_required
def admin_games_create():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return validation_error("title is required")
    m = create_media(
        title=title,
        media_type="game",
        description=data.get("description", ""),
        image_url=data.get("imageUrl", data.get("image_url", "")),
        year=data.get("year"),
    )
    return api_response(data=m.to_dict(), message="Created", status=201)


@bp.route("/admin/games/<game_id>", methods=["PATCH"])
@admin_required
def admin_games_patch(game_id):
    mid = _pid(game_id)
    if mid is None:
        return validation_error("Invalid id")
    data = request.get_json(silent=True) or {}
    fields = {k: v for k, v in {
        "title": data.get("title"),
        "description": data.get("description"),
        "image_url": data.get("imageUrl", data.get("image_url")),
        "year": data.get("year"),
    }.items() if v is not None}
    m = update_media(mid, **fields)
    if not m or m.media_type != "game":
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())


@bp.route("/admin/games/<game_id>", methods=["DELETE"])
@admin_required
def admin_games_delete(game_id):
    mid = _pid(game_id)
    if mid is None:
        return validation_error("Invalid id")
    m = get_media(mid)
    if not m or m.media_type != "game":
        return api_response(data=None, message="Not found", success=False, status=404)
    delete_media(mid)
    return api_response(data={"deleted": True})


@bp.route("/admin/movies", methods=["POST"])
@admin_required
def admin_movies_create():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return validation_error("title is required")
    m = create_media(
        title=title,
        media_type="movie",
        description=data.get("description", ""),
        image_url=data.get("imageUrl", data.get("image_url", "")),
        year=data.get("year"),
    )
    return api_response(data=m.to_dict(), message="Created", status=201)


@bp.route("/admin/movies/<movie_id>", methods=["PATCH"])
@admin_required
def admin_movies_patch(movie_id):
    mid = _pid(movie_id)
    if mid is None:
        return validation_error("Invalid id")
    data = request.get_json(silent=True) or {}
    fields = {k: v for k, v in {
        "title": data.get("title"),
        "description": data.get("description"),
        "image_url": data.get("imageUrl", data.get("image_url")),
        "year": data.get("year"),
    }.items() if v is not None}
    m = update_media(mid, **fields)
    if not m or m.media_type != "movie":
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())


@bp.route("/admin/movies/<movie_id>", methods=["DELETE"])
@admin_required
def admin_movies_delete(movie_id):
    mid = _pid(movie_id)
    if mid is None:
        return validation_error("Invalid id")
    m = get_media(mid)
    if not m or m.media_type != "movie":
        return api_response(data=None, message="Not found", success=False, status=404)
    delete_media(mid)
    return api_response(data={"deleted": True})


@bp.route("/admin/reviews/pending", methods=["GET"])
@admin_required
def admin_reviews_pending():
    return api_response(data=[], message="No pending review model")


@bp.route("/admin/reviews/<review_id>/approve", methods=["PATCH"])
@admin_required
def admin_reviews_approve(review_id):
    return api_response(
        data=None,
        message="Reviews not implemented",
        success=False,
        status=501,
    )


@bp.route("/admin/reviews/<review_id>", methods=["DELETE"])
@admin_required
def admin_reviews_delete(review_id):
    return api_response(
        data=None,
        message="Reviews not implemented",
        success=False,
        status=501,
    )
