# -*- coding: utf-8 -*-
import json

from app.models.friendship import Friendship
from app.models.media import Media
from app.models.user import User


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def register(client, username, email):
    post_json(client, "/api/v1/auth/register", {
        "username": username,
        "email": email,
        "password": "password123",
    })


def test_share_media_sends_message_to_friend(client, app, db):
    register(client, "sender", "sender@example.com")
    with app.app_context():
        sender = User.query.filter_by(username="sender").first()
        recipient = User(username="friend", email="friend@example.com")
        recipient.set_password("password123")
        media = Media(title="Shared Movie", media_type="movie", imdb_id="ttshare1")
        db.session.add_all([recipient, media])
        db.session.flush()
        db.session.add(Friendship(requester_id=sender.id, addressee_id=recipient.id, status="accepted"))
        db.session.commit()
        sender_id = sender.id
        media_id = media.id
        recipient_id = recipient.id

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": media_id,
        "recipientId": recipient_id,
    })
    body = rv.get_json()

    assert rv.status_code == 201
    assert body["success"] is True
    assert body["data"]["sender_id"] == sender_id
    assert body["data"]["recipient_id"] == recipient_id
    assert "Shared Movie" in body["data"]["body"]
    assert "/items/ttshare1" in body["data"]["body"]


def test_share_media_rejects_non_friend(client, app, db):
    register(client, "sender2", "sender2@example.com")
    with app.app_context():
        recipient = User(username="notfriend", email="notfriend@example.com")
        recipient.set_password("password123")
        media = Media(title="Private Movie", media_type="movie", imdb_id="ttshare2")
        db.session.add_all([recipient, media])
        db.session.commit()
        media_id = media.id
        recipient_id = recipient.id

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": media_id,
        "recipientId": recipient_id,
    })

    assert rv.status_code == 400
    assert rv.get_json()["message"] == "You can only message friends"
