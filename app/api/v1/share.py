# -*- coding: utf-8 -*-
from flask import request, url_for
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, validation_error
from app.services.media_service import get_media
from app.services.message_service import send_message


@bp.route("/share/media", methods=["POST"])
@api_login_required
def share_media():
    data = request.get_json(silent=True) or {}
    media_id = data.get("mediaId")
    recipient_id = data.get("recipientId")

    if media_id is None:
        return validation_error("mediaId is required")
    if recipient_id is None:
        return validation_error("recipientId is required")

    try:
        media_id = int(media_id)
        recipient_id = int(recipient_id)
    except (TypeError, ValueError):
        return validation_error("mediaId and recipientId must be numeric")

    media = get_media(media_id)
    if not media:
        return api_response(data=None, message="Media not found", success=False, status=404)

    detail_url = url_for("main.item_detail", imdb_id=media.imdb_id, _external=False) if media.imdb_id else ""
    body = f"Check out {media.title} on WatchList Hub"
    if detail_url:
        body = f"{body}: {detail_url}"

    message, err = send_message(current_user.id, recipient_id, body)
    if err:
        return api_response(data=None, message=err, success=False, status=400)

    return api_response(data=message, message="Shared", status=201)
