# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from sqlalchemy import or_, and_
from app.extensions import db
from app.models.message import Message
from app.services.friend_service import are_friends
from app.services import tag_service


def send_message(sender_id, recipient_id, body):
    body = (body or "").strip()
    if not body:
        return None, "Message body cannot be empty"
    if not are_friends(sender_id, recipient_id):
        return None, "You can only message friends"
    msg = Message(sender_id=sender_id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()
    tags = tag_service.resolve_tags(body)
    return msg.to_dict(tags=tags), None


def get_conversation(user_a, user_b, limit=50, offset=0):
    rows = Message.query.filter(
        or_(
            and_(Message.sender_id == user_a, Message.recipient_id == user_b),
            and_(Message.sender_id == user_b, Message.recipient_id == user_a),
        )
    ).order_by(Message.created_at.asc()).offset(offset).limit(limit).all()
    results = []
    for msg in rows:
        tags = tag_service.resolve_tags(msg.body)
        results.append(msg.to_dict(tags=tags))
    return results


def mark_read(reader_id, sender_id):
    now = datetime.now(timezone.utc)
    updated = Message.query.filter_by(
        sender_id=sender_id, recipient_id=reader_id, read_at=None
    ).update({"read_at": now})
    db.session.commit()
    return updated


def unread_count(user_id):
    return Message.query.filter_by(recipient_id=user_id, read_at=None).count()
