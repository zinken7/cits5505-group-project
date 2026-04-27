# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user
from flask_socketio import join_room, emit
from app.extensions import socketio
from app.services import friend_service, message_service

# user_id -> set of socket session IDs (handles multiple tabs)
_online: dict[int, set[str]] = {}


def _room(a, b):
    return f"chat_{min(a, b)}_{max(a, b)}"


def _auth_required():
    if not current_user.is_authenticated:
        emit("message_error", {"error": "Authentication required"})
        return False
    return True


def is_online(user_id: int) -> bool:
    return bool(_online.get(user_id))


@socketio.on("connect")
def on_connect():
    if not current_user.is_authenticated:
        return False
    uid = current_user.id
    sid = request.sid
    _online.setdefault(uid, set()).add(sid)
    join_room(f"user_{uid}")
    # tell each friend this user just came online
    for friend in friend_service.get_friends(uid):
        emit("presence", {"user_id": uid, "online": True}, to=f"user_{friend['id']}")


@socketio.on("disconnect")
def on_disconnect():
    if not current_user.is_authenticated:
        return
    uid = current_user.id
    sid = request.sid
    sids = _online.get(uid, set())
    sids.discard(sid)
    if not sids:
        _online.pop(uid, None)
        for friend in friend_service.get_friends(uid):
            emit("presence", {"user_id": uid, "online": False}, to=f"user_{friend['id']}")


@socketio.on("join_chat")
def on_join_chat(data):
    if not _auth_required():
        return
    friend_id = int(data.get("friend_id", 0))
    if not friend_service.are_friends(current_user.id, friend_id):
        emit("message_error", {"error": "Not friends"})
        return
    room = _room(current_user.id, friend_id)
    join_room(room)
    history = message_service.get_conversation(current_user.id, friend_id, limit=50)
    message_service.mark_read(current_user.id, friend_id)
    emit("chat_history", {"friend_id": friend_id, "messages": history})


@socketio.on("send_message")
def on_send_message(data):
    if not _auth_required():
        return
    recipient_id = int(data.get("recipient_id", 0))
    body = data.get("body", "")
    msg, err = message_service.send_message(current_user.id, recipient_id, body)
    if err:
        emit("message_error", {"error": err})
        return
    # Deliver via personal rooms only — each user gets exactly one copy
    emit("new_message", msg, to=f"user_{current_user.id}")
    emit("new_message", msg, to=f"user_{recipient_id}")
