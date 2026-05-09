# -*- coding: utf-8 -*-
import json

from app.models.friendship import Friendship
from app.models.media import Media
from app.models.message import Message
from app.models.user import User
from app.extensions import socketio


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
    assert body["data"]["body"] == "Check out #Shared Movie on WatchList Hub. It's interesting!"
    assert body["data"]["tags"][0]["text"] == "Shared Movie"
    assert body["data"]["tags"][0]["url"] == "/items/ttshare1"


def test_share_media_api_emits_realtime_message(client, app, db):
    register(client, "api_socket_sender", "api_socket_sender@example.com")
    with app.app_context():
        sender = User.query.filter_by(username="api_socket_sender").first()
        recipient = User(username="api_socket_friend", email="api_socket_friend@example.com")
        recipient.set_password("password123")
        media = Media(title="API Socket Share", media_type="movie", imdb_id="ttapisocket1")
        db.session.add_all([recipient, media])
        db.session.flush()
        db.session.add(Friendship(requester_id=sender.id, addressee_id=recipient.id, status="accepted"))
        db.session.commit()
        media_id = media.id
        recipient_id = recipient.id

    socket_client = socketio.test_client(app, flask_test_client=client)
    assert socket_client.is_connected()

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": media_id,
        "recipientId": recipient_id,
    })

    assert rv.status_code == 201
    received = socket_client.get_received()
    new_messages = [event for event in received if event["name"] == "new_message"]
    assert len(new_messages) == 1
    assert new_messages[0]["args"][0]["body"] == "Check out #API Socket Share on WatchList Hub. It's interesting!"


def test_share_media_sends_to_multiple_friends(client, app, db):
    register(client, "sender_multi", "sender_multi@example.com")
    with app.app_context():
        sender = User.query.filter_by(username="sender_multi").first()
        friend_one = User(username="friendone", email="friendone@example.com")
        friend_one.set_password("password123")
        friend_two = User(username="friendtwo", email="friendtwo@example.com")
        friend_two.set_password("password123")
        media = Media(title="Group Share", media_type="tvshow", imdb_id="ttgroup1")
        db.session.add_all([friend_one, friend_two, media])
        db.session.flush()
        db.session.add_all([
            Friendship(requester_id=sender.id, addressee_id=friend_one.id, status="accepted"),
            Friendship(requester_id=sender.id, addressee_id=friend_two.id, status="accepted"),
        ])
        db.session.commit()
        media_id = media.id
        recipient_ids = [friend_one.id, friend_two.id]

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": media_id,
        "recipientIds": recipient_ids,
    })
    body = rv.get_json()

    assert rv.status_code == 201
    assert body["success"] is True
    assert body["data"]["count"] == 2
    assert sorted(message["recipient_id"] for message in body["data"]["messages"]) == sorted(recipient_ids)

    with app.app_context():
        rows = Message.query.order_by(Message.id).all()
        assert len(rows) == 2
        assert {row.recipient_id for row in rows} == set(recipient_ids)
        assert all(row.body == "Check out #Group Share on WatchList Hub. It's interesting!" for row in rows)


def test_share_media_uses_exact_media_for_duplicate_titles(client, app, db):
    register(client, "duplicate_sender", "duplicate_sender@example.com")
    with app.app_context():
        sender = User.query.filter_by(username="duplicate_sender").first()
        recipient = User(username="duplicate_friend", email="duplicate_friend@example.com")
        recipient.set_password("password123")
        first = Media(title="The Office", media_type="tvshow", imdb_id="tt0386676")
        second = Media(title="The Office", media_type="tvshow", imdb_id="tt0290978")
        db.session.add_all([recipient, first, second])
        db.session.flush()
        db.session.add(Friendship(requester_id=sender.id, addressee_id=recipient.id, status="accepted"))
        db.session.commit()
        second_id = second.id
        recipient_id = recipient.id

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": second_id,
        "recipientId": recipient_id,
    })
    body = rv.get_json()

    assert rv.status_code == 201
    assert body["data"]["body"] == "Check out #The Office on WatchList Hub. It's interesting!"
    assert body["data"]["tags"][0]["imdb_id"] == "tt0290978"
    assert body["data"]["tags"][0]["url"] == "/items/tt0290978"


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


def test_share_media_requires_login(client, db):
    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": 1,
        "recipientId": 2,
    })

    body = rv.get_json()
    assert rv.status_code == 401
    assert body["success"] is False
    assert body["message"] == "Authentication required"


def test_share_media_validates_required_fields(client, db):
    register(client, "sender3", "sender3@example.com")

    rv = post_json(client, "/api/v1/share/media", {"mediaId": 1})
    body = rv.get_json()

    assert rv.status_code == 422
    assert body["detail"][0]["msg"] == "recipientId is required"


def test_share_media_validates_empty_recipient_list(client, db):
    register(client, "sender_empty", "sender_empty@example.com")

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": 1,
        "recipientIds": [],
    })
    body = rv.get_json()

    assert rv.status_code == 422
    assert body["detail"][0]["msg"] == "At least one recipient is required"


def test_share_media_returns_not_found_for_missing_media(client, db):
    register(client, "sender4", "sender4@example.com")

    rv = post_json(client, "/api/v1/share/media", {
        "mediaId": 9999,
        "recipientId": 1,
    })
    body = rv.get_json()

    assert rv.status_code == 404
    assert body["success"] is False
    assert body["message"] == "Media not found"
