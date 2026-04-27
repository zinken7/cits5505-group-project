# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import admin_required, api_response, parse_id, parse_user_id, validate_body, validation_error
from app.api.v1.schemas.media import MediaCreateSchema, MediaPatchSchema
from app.services.media_service import create_media, delete_media, get_media, update_media
from app.services.user_service import delete_user, get_user, list_all_users, set_admin_role


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@bp.route("/admin/users", methods=["GET"])
@admin_required
def admin_users_list():
    users = list_all_users()
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
    user = get_user(uid)
    if not user:
        return api_response(data=None, message="Not found", success=False, status=404)
    data = request.get_json(silent=True) or {}
    is_admin = bool(data["isAdmin"]) if "isAdmin" in data else None
    if is_admin is None and "role" in data:
        is_admin = data["role"] == "admin"
    if is_admin is not None:
        set_admin_role(user, is_admin=is_admin)
    return api_response(data=user.to_dict())


@bp.route("/admin/users/<user_id>", methods=["DELETE"])
@admin_required
def admin_users_delete(user_id):
    uid = parse_user_id(user_id)
    if uid is None:
        return validation_error("Invalid user id")
    user = get_user(uid)
    if not user:
        return api_response(data=None, message="Not found", success=False, status=404)
    if user.id == current_user.id:
        return api_response(data=None, message="Cannot delete yourself", success=False, status=400)
    delete_user(user)
    return api_response(data={"deleted": True})


# ---------------------------------------------------------------------------
# Media (generic — mediaType in body for create, id in URL for patch/delete)
# ---------------------------------------------------------------------------

@bp.route("/admin/media", methods=["POST"])
@admin_required
@validate_body(MediaCreateSchema)
def admin_media_create():
    data = request.get_json(silent=True) or {}
    m = create_media(
        title=data["title"].strip(),
        media_type=data["mediaType"],
        description=data.get("description", ""),
        image_url=data.get("imageUrl", data.get("image_url", "")),
        year=data.get("year"),
    )
    return api_response(data=m.to_dict(), message="Created", status=201)


@bp.route("/admin/media/<media_id>", methods=["PATCH"])
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


@bp.route("/admin/media/<media_id>", methods=["DELETE"])
@admin_required
def admin_media_delete(media_id):
    mid = parse_id(media_id)
    if mid is None:
        return validation_error("Invalid id")
    if not get_media(mid):
        return api_response(data=None, message="Not found", success=False, status=404)
    delete_media(mid)
    return api_response(data={"deleted": True})
