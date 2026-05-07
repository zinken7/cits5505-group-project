# -*- coding: utf-8 -*-
from flask import request, url_for
from flask_login import current_user

from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, validation_error
from app.services.friend_service import are_friends
from app.services.media_service import get_media
from app.services.message_service import send_message


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

    media = get_media(media_id)
    if not media:
        return api_response(data=None, message="Media not found", success=False, status=404)

    for recipient_id in recipient_ids:
        if not are_friends(current_user.id, recipient_id):
            return api_response(
                data=None,
                message="You can only message friends",
                success=False,
                status=400,
            )

    detail_url = url_for("main.item_detail", imdb_id=media.imdb_id, _external=False) if media.imdb_id else ""
    body = f"Check out {media.title} on WatchList Hub"
    if detail_url:
        body = f"{body}: {detail_url}"

    messages = []
    for recipient_id in recipient_ids:
        message, err = send_message(current_user.id, recipient_id, body)
        if err:
            return api_response(data=None, message=err, success=False, status=400)
        messages.append(message)

    if single_recipient:
        return api_response(data=messages[0], message="Shared", status=201)

    return api_response(
        data={"messages": messages, "count": len(messages)},
        message="Shared",
        status=201,
    )
