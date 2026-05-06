# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.api.v1 import bp
from app.api.v1.common import (
    admin_required,
    api_response,
    parse_id,
    parse_pagination,
    parse_user_id,
    validate_body,
    validation_error,
)
from app.api.v1.schemas.media import MediaCreateSchema, MediaPatchSchema
from app.extensions import db
from app.services.imdb_service import lookup_imdb, parse_imdb_id
from app.services.media_service import (
    create_media,
    delete_media,
    get_media,
    get_media_by_imdb_id,
    list_media_admin_page,
    update_media,
)
from app.services.user_service import (
    deactivate_user,
    get_user,
    list_all_users,
    reactivate_user,
    set_admin_role,
)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@bp.route("/management/users", methods=["GET"])
@admin_required
def management_users_list():
    users = list_all_users(include_root=False)
    out = []
    for u in users:
        row = u.to_public_dict()
        row["email"] = u.email
        row["isAdmin"] = u.is_admin
        row["isRoot"] = u.is_root
        row["deactivated"] = u.deactivated
        out.append(row)
    return api_response(data=out)


@bp.route("/management/users/<user_id>", methods=["PATCH"])
@admin_required
def management_users_patch(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    user = get_user(uid, include_deactivated=True)
    if not user:
        return api_response(data=None, message="Not found", success=False, status=404)
    data = request.get_json(silent=True) or {}
    is_admin = bool(data["isAdmin"]) if "isAdmin" in data else None
    if is_admin is None and "role" in data:
        is_admin = data["role"] == "admin"
    if "deactivated" in data:
        if user.id == current_user.id:
            return api_response(data=None, message="Cannot deactivate yourself", success=False, status=400)
        try:
            if bool(data["deactivated"]):
                deactivate_user(user)
            else:
                reactivate_user(user)
        except ValueError as e:
            return api_response(data=None, message=str(e), success=False, status=400)
    if is_admin is not None:
        if not getattr(current_user, "is_root", False):
            return api_response(data=None, message="Root account required", success=False, status=403)
        try:
            set_admin_role(user, is_admin=is_admin)
        except ValueError as e:
            return api_response(data=None, message=str(e), success=False, status=400)
    return api_response(data=user.to_dict())


@bp.route("/management/users/<user_id>", methods=["DELETE"])
@admin_required
def management_users_delete(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    user = get_user(uid, include_deactivated=True)
    if not user:
        return api_response(data=None, message="Not found", success=False, status=404)
    if user.id == current_user.id:
        return api_response(data=None, message="Cannot delete yourself", success=False, status=400)
    try:
        deactivate_user(user)
    except ValueError as e:
        return api_response(data=None, message=str(e), success=False, status=400)
    return api_response(data={"deactivated": True}, message="User deactivated")


# ---------------------------------------------------------------------------
# Media (generic — mediaType in body for create, id in URL for patch/delete)
# ---------------------------------------------------------------------------

@bp.route("/management/media/imdb-lookup", methods=["POST"])
@admin_required
def admin_media_imdb_lookup():
    """Fetch IMDb data for preview — returns fields but does NOT write to the DB."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return validation_error("url is required")

    imdb_id = parse_imdb_id(url)
    if imdb_id:
        existing = get_media_by_imdb_id(imdb_id)
        if existing:
            return api_response(
                data={"already_exists": True, "item": existing.to_dict()},
                message=f"“{existing.title}” is already in the catalogue.",
            )

    fields, err = lookup_imdb(url)
    if err:
        return api_response(data=None, message=err, success=False, status=422)

    return api_response(
        data={"already_exists": False, "fields": fields},
        message=f"Found: {fields['title']}",
    )


@bp.route("/management/media", methods=["GET"])
@admin_required
def admin_media_list():
    limit, offset = parse_pagination(limit_default=15, max_limit=100)
    rows, total = list_media_admin_page(limit=limit, offset=offset)
    return api_response(data={
        "items": [m.to_dict() for m in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


@bp.route("/management/media", methods=["POST"])
@admin_required
@validate_body(MediaCreateSchema)
def admin_media_create():
    data = request.get_json(silent=True) or {}
    genres = data.get("genres")
    if not isinstance(genres, list):
        genres = None
    cast = data.get("cast")
    if not isinstance(cast, list):
        cast = None
    rs = data.get("releaseStatus") or data.get("release_status")
    rs = str(rs).strip() if rs is not None else None
    if not rs:
        rs = None

    try:
        m = create_media(
            title=data["title"].strip(),
            media_type=data["mediaType"],
            description=data.get("description") or "",
            image_url=data.get("imageUrl") or data.get("image_url") or "",
            year=data.get("year"),
            imdb_id=(data.get("imdbId") or data.get("imdb_id") or "").strip() or None,
            imdb_url=data.get("imdbUrl") or data.get("imdb_url") or "",
            rating=data.get("rating"),
            votes=data.get("votes"),
            rank=data.get("rank"),
            genres=genres,
            runtime_minutes=data.get("runtimeMinutes", data.get("runtime_minutes")),
            episodes=data.get("episodes"),
            release_status=rs,
            director=(data.get("director") or "").strip() or None,
            cast=cast,
            language=(data.get("language") or "").strip() or None,
            country=(data.get("country") or "").strip() or None,
            tagline=(data.get("tagline") or "").strip() or None,
            awards=(data.get("awards") or "").strip() or None,
            trailer_url=data.get("trailerUrl") or data.get("trailer_url") or "",
        )
    except ValueError as e:
        return validation_error(str(e))
    except IntegrityError:
        db.session.rollback()
        return validation_error("imdbId already exists or database constraint failed")

    return api_response(data=m.to_dict(), message="Created", status=201)


@bp.route("/management/media/<media_id>", methods=["PATCH"])
@admin_required
@validate_body(MediaPatchSchema)
def admin_media_patch(media_id):
    mid = parse_id(media_id)
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
    if not m:
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())


@bp.route("/management/media/<media_id>", methods=["DELETE"])
@admin_required
def admin_media_delete(media_id):
    mid = parse_id(media_id)
    if mid is None:
        return validation_error("Invalid id")
    if not get_media(mid):
        return api_response(data=None, message="Not found", success=False, status=404)
    delete_media(mid)
    return api_response(data={"deleted": True})
