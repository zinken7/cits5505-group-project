# -*- coding: utf-8 -*-
"""One envelope-shape smoke test per API module."""
import json
import pytest


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def _register_and_login(client, username, email):
    post_json(client, "/api/v1/auth/register", {
        "username": username, "email": email, "password": "password123",
    })
    post_json(client, "/api/v1/auth/login", {"login": email, "password": "password123"})


ENVELOPE_KEYS = {"success", "message", "data", "meta", "links"}


def _assert_envelope(body):
    assert ENVELOPE_KEYS.issubset(body.keys()), f"Missing keys: {ENVELOPE_KEYS - body.keys()}"


def test_root_envelope(client):
    rv = client.get("/api/v1")
    _assert_envelope(rv.get_json())


def test_catalog_anime_envelope(client, db):
    rv = client.get("/api/v1/anime")
    body = rv.get_json()
    _assert_envelope(body)
    assert isinstance(body["data"], list)


def test_catalog_movies_envelope(client, db):
    rv = client.get("/api/v1/movies")
    _assert_envelope(rv.get_json())


def test_catalog_games_envelope(client, db):
    rv = client.get("/api/v1/games")
    _assert_envelope(rv.get_json())


def test_search_envelope(client, db):
    rv = client.get("/api/v1/search?q=test")
    _assert_envelope(rv.get_json())


def test_watchlist_requires_auth(client, db):
    rv = client.get("/api/v1/watchlist")
    assert rv.status_code == 401
    _assert_envelope(rv.get_json())


def test_users_me_requires_auth(client):
    rv = client.get("/api/v1/users/me")
    assert rv.status_code == 401
    _assert_envelope(rv.get_json())


def test_users_public_get(client, db):
    _register_and_login(client, "pubuser", "pubuser@example.com")
    rv = client.get("/api/v1/users/me")
    body = rv.get_json()
    _assert_envelope(body)
    assert body["data"]["username"] == "pubuser"
