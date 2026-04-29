# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, parse_id, parse_pagination, validate_body, validation_error
from app.api.v1.schemas.watchlist import WatchlistCreateSchema, WatchlistPatchSchema
from app.services.media_service import get_media
from app.services.watchlist_service import (
    add_to_watchlist,
    filter_watchlist,
    get_user_watchlist,
    get_watchlist_item,
    patch_watchlist_item,
    remove_from_watchlist,
)


@bp.route("/watchlist", methods=["GET"])
@api_login_required
def watchlist_list():
    status = request.args.get("status")
    media_type = request.args.get("mediaType")
    q = request.args.get("q")
    sort = request.args.get("sort") or "-updatedAt"
    limit, offset = parse_pagination(limit_default=20, max_limit=100)
    raw = get_user_watchlist(current_user.id, status=None)
    items, total = filter_watchlist(
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


@bp.route("/watchlist", methods=["POST"])
@api_login_required
@validate_body(WatchlistCreateSchema)
def watchlist_create():
    data = request.get_json(silent=True) or {}
    media_type = data.get("mediaType")
    media_id_raw = data.get("mediaId")
    status = data.get("status") or "planned"
    media_id = int(str(media_id_raw))

    media = get_media(media_id)
    if not media or media.media_type != media_type:
        return api_response(
            data=None,
            message="mediaId and mediaType do not match a catalog item",
            success=False,
            status=400,
        )

    item, err = add_to_watchlist(current_user.id, media_id, status=status)
    if err:
        return api_response(data=None, message=err, success=False, status=400)
    return api_response(data=item, message="Created", status=201)


@bp.route("/watchlist/<entry_id>", methods=["GET"])
@api_login_required
def watchlist_one_get(entry_id):
    eid = parse_id(entry_id)
    if eid is None:
        return validation_error("Invalid entry id")
    item, err = get_watchlist_item(eid, current_user.id)
    if err:
        return api_response(data=None, message=err, success=False, status=404)
    return api_response(data=item)


@bp.route("/watchlist/<entry_id>", methods=["PATCH"])
@api_login_required
@validate_body(WatchlistPatchSchema)
def watchlist_one_patch(entry_id):
    eid = parse_id(entry_id)
    if eid is None:
        return validation_error("Invalid entry id")
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    item, err = patch_watchlist_item(eid, current_user.id, status=status)
    if err:
        code = 404 if "not found" in err.lower() else 400
        return api_response(data=None, message=err, success=False, status=code)
    return api_response(data=item)


@bp.route("/watchlist/<entry_id>", methods=["DELETE"])
@api_login_required
def watchlist_one_delete(entry_id):
    eid = parse_id(entry_id)
    if eid is None:
        return validation_error("Invalid entry id")
    ok, err = remove_from_watchlist(eid, current_user.id)
    if not ok:
        return api_response(data=None, message=err, success=False, status=400)
    return api_response(data={"deleted": True}, message="Removed")
