# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user
from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, parse_pagination
from app.services import message_service


@bp.route("/messages/<int:user_id>", methods=["GET"])
@api_login_required
def get_conversation(user_id):
    limit, offset = parse_pagination(limit_default=50, max_limit=200)
    msgs = message_service.get_conversation(current_user.id, user_id, limit, offset)
    return api_response(data=msgs)


@bp.route("/messages/<int:user_id>/read", methods=["PATCH"])
@api_login_required
def mark_read(user_id):
    updated = message_service.mark_read(current_user.id, user_id)
    return api_response(data={"updated": updated})


@bp.route("/messages/unread", methods=["GET"])
@api_login_required
def unread_count():
    count = message_service.unread_count(current_user.id)
    return api_response(data={"count": count})
