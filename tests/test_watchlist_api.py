# -*- coding: utf-8 -*-
"""Tests for watchlist API behavior."""
import json

from app.models.media import Media


def post_json(client, url, payload):
    return client.post(url, json=payload)


def register_and_login(client):
    post_json(
        client,
        "/api/v1/auth/register",
        {"username": "liker", "email": "liker@example.com", "password": "password123"},
    )
    post_json(client, "/api/v1/auth/login", {"login": "liker@example.com", "password": "password123"})


def test_watchlist_status_endpoint_can_toggle_like(client, app, db):
    register_and_login(client)

    with app.app_context():
        media = Media(title="Liked Movie", media_type="movie", year=2024)
        db.session.add(media)
        db.session.commit()
        media_id = media.id

    rv = client.put(f"/api/v1/watchlist/status/{media_id}", json={"isLiked": True})
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["data"]["status"] is None
    assert body["data"]["is_liked"] is True

    rv = client.get("/api/v1/watchlist")
    assert rv.status_code == 200
    assert rv.get_json()["data"] == []

    rv = client.put(f"/api/v1/watchlist/status/{media_id}", json={"status": "completed"})
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["data"]["status"] == "completed"
    assert body["data"]["is_liked"] is True

    rv = client.delete(f"/api/v1/watchlist/status/{media_id}")
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["data"]["deleted"] is True
    assert body["data"]["item"]["status"] is None
    assert body["data"]["item"]["is_liked"] is True
