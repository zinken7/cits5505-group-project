# -*- coding: utf-8 -*-
"""Tests for watchlist API behavior."""
import json

from app.models.media import Media


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def patch_json(client, url, payload):
    return client.patch(url, data=json.dumps(payload), content_type="application/json")


def login_user(client):
    post_json(client, "/api/v1/auth/register", {
        "username": "liker",
        "email": "liker@example.com",
        "password": "password123",
    })


def test_watchlist_create_and_patch_is_liked(client, db, app):
    login_user(client)
    with app.app_context():
        media = Media(title="Liked Movie", media_type="movie", year=2025)
        db.session.add(media)
        db.session.commit()
        media_id = media.id

    created = post_json(client, "/api/v1/watchlist", {
        "mediaType": "movie",
        "mediaId": media_id,
        "status": "planned",
        "isLiked": True,
    })
    assert created.status_code == 201
    created_body = created.get_json()
    assert created_body["data"]["is_liked"] is True

    entry_id = created_body["data"]["id"]
    updated = patch_json(client, f"/api/v1/watchlist/{entry_id}", {"isLiked": False})
    assert updated.status_code == 200
    assert updated.get_json()["data"]["is_liked"] is False
