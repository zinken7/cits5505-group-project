# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user
from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, validation_error
from app.extensions import db, socketio
from app.models.friendship import Friendship
from app.services import friend_service
from app.sockets.chat import is_online


@bp.route("/friends", methods=["GET"])
@api_login_required
def list_friends():
    friends = friend_service.get_friends(current_user.id)
    for f in friends:
        f["online"] = is_online(f["id"])
    return api_response(data=friends)


@bp.route("/friends/requests", methods=["GET"])
@api_login_required
def list_friend_requests():
    received = [fs.to_dict() for fs in friend_service.get_pending_received(current_user.id)]
    sent = [fs.to_dict() for fs in friend_service.get_pending_sent(current_user.id)]
    return api_response(data={"received": received, "sent": sent})


@bp.route("/friends/requests", methods=["POST"])
@api_login_required
def send_friend_request():
    data = request.get_json(silent=True) or {}
    target_id = data.get("targetUserId")
    if not target_id:
        return validation_error("targetUserId is required")
    fs, err = friend_service.send_request(current_user.id, int(target_id))
    if err:
        return api_response(data=None, message=err, success=False, status=400)
    try:
        socketio.emit('friend_request', {'friendship_id': fs.id}, room=f'user_{int(target_id)}')
    except Exception:
        pass
    return api_response(data=fs.to_dict(), status=201)


@bp.route("/friends/requests/<int:friendship_id>", methods=["PATCH"])
@api_login_required
def respond_friend_request(friendship_id):
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    if action not in ("accept", "reject"):
        return validation_error("action must be 'accept' or 'reject'")
    fs, err = friend_service.respond_to_request(friendship_id, current_user.id, action)
    if err:
        return api_response(data=None, message=err, success=False, status=400)
    if action == 'accept':
        try:
            socketio.emit('friend_accepted', {
                'friendship_id': fs.id,
                'accepter_id': current_user.id,
            }, room=f'user_{fs.requester_id}')
        except Exception:
            pass
    return api_response(data=fs.to_dict())


@bp.route("/friends/<int:friendship_id>", methods=["DELETE"])
@api_login_required
def remove_friend(friendship_id):
    fs = db.session.get(Friendship, friendship_id)

    # Idempotent: already gone is still a success
    if not fs:
        return api_response(data=None, message="Friendship removed")

    if fs.requester_id != current_user.id and fs.addressee_id != current_user.id:
        return api_response(data=None, message="Not authorised", success=False, status=403)

    other_id = fs.addressee_id if fs.requester_id == current_user.id else fs.requester_id

    ok, err = friend_service.remove_friend(friendship_id, current_user.id)
    if not ok:
        return api_response(data=None, message=err, success=False, status=400)

    try:
        socketio.emit('friend_removed', {'other_id': other_id}, room=f'user_{current_user.id}')
        socketio.emit('friend_removed', {'other_id': current_user.id}, room=f'user_{other_id}')
    except Exception:
        pass
    return api_response(data=None, message="Friendship removed")


@bp.route("/friends/status/<int:user_id>", methods=["GET"])
@api_login_required
def friendship_status(user_id):
    fs = friend_service.get_friendship(current_user.id, user_id)
    if not fs:
        return api_response(data={"status": "none"})
    return api_response(data={"status": fs.status, "friendship_id": fs.id,
                               "is_requester": fs.requester_id == current_user.id})
