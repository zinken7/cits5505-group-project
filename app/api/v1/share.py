# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, validation_error
from app.extensions import socketio
from app.services.share_service import share_media_with_friends


@bp.route("/share/media", methods=["POST"])
@api_login_required
def share_media():
    data = request.get_json(silent=True) or {}
    media_id = data.get("mediaId")
    raw_recipient_ids = data.get("recipientIds")
    single_recipient_id = data.get("recipientId")

    if media_id is None:
        return validation_error("mediaId is required")
    if raw_recipient_ids is None and single_recipient_id is None:
        return validation_error("recipientId is required")

    try:
        media_id = int(media_id)
    except (TypeError, ValueError):
        return validation_error("mediaId must be numeric")

    if raw_recipient_ids is None:
        raw_recipient_ids = [single_recipient_id]
        single_recipient = True
    elif isinstance(raw_recipient_ids, list):
        single_recipient = False
    else:
        return validation_error("recipientIds must be a list")

    if not raw_recipient_ids:
        return validation_error("At least one recipient is required")

    try:
        recipient_ids = [int(recipient_id) for recipient_id in raw_recipient_ids]
    except (TypeError, ValueError):
        return validation_error("recipientId must be numeric")

    recipient_ids = list(dict.fromkeys(recipient_ids))

    messages, err = share_media_with_friends(current_user.id, media_id, recipient_ids)
    if err == "Media not found":
        return api_response(data=None, message=err, success=False, status=404)
    if err:
        return api_response(data=None, message=err, success=False, status=400)

    for message in messages:
        socketio.emit("new_message", message, to=f"user_{message['sender_id']}")
        socketio.emit("new_message", message, to=f"user_{message['recipient_id']}")

    if single_recipient:
        return api_response(data=messages[0], message="Shared", status=201)

    return api_response(
        data={"messages": messages, "count": len(messages)},
        message="Shared",
        status=201,
    )
