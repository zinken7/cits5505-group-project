# -*- coding: utf-8 -*-
"""Tests for /api/v1/auth endpoints — envelope shape, register/login flow, CSRF."""
import json
import pytest


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


class TestRegister:
    def test_register_success(self, client, db):
        rv = post_json(client, "/api/v1/auth/register", {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        })
        assert rv.status_code == 201
        body = rv.get_json()
        assert body["success"] is True
        assert body["data"]["username"] == "alice"

    def test_register_missing_fields(self, client, db):
        rv = post_json(client, "/api/v1/auth/register", {"username": "bob"})
        assert rv.status_code == 422

    def test_register_duplicate_email(self, client, db):
        payload = {"username": "carol", "email": "carol@example.com", "password": "password123"}
        post_json(client, "/api/v1/auth/register", payload)
        payload["username"] = "carol2"
        rv = post_json(client, "/api/v1/auth/register", payload)
        assert rv.status_code == 400
        assert rv.get_json()["success"] is False

    def test_register_display_name_too_long(self, client, db):
        rv = post_json(client, "/api/v1/auth/register", {
            "username": "dave",
            "email": "dave@example.com",
            "password": "password123",
            "displayName": "x" * 81,
        })
        assert rv.status_code == 422


class TestLogin:
    def test_login_success(self, client, db):
        post_json(client, "/api/v1/auth/register", {
            "username": "eve", "email": "eve@example.com", "password": "password123",
        })
        rv = post_json(client, "/api/v1/auth/login", {"login": "eve@example.com", "password": "password123"})
        assert rv.status_code == 200
        assert rv.get_json()["success"] is True

    def test_login_bad_credentials(self, client, db):
        rv = post_json(client, "/api/v1/auth/login", {"login": "nobody@example.com", "password": "wrong"})
        assert rv.status_code == 401
        assert rv.get_json()["success"] is False

    def test_login_missing_fields(self, client, db):
        rv = post_json(client, "/api/v1/auth/login", {"login": "someone"})
        assert rv.status_code == 422


class TestSession:
    def test_session_unauthenticated(self, client):
        rv = client.get("/api/v1/auth/session")
        assert rv.status_code == 200
        assert rv.get_json()["data"]["user"] is None

    def test_session_authenticated(self, client, db):
        post_json(client, "/api/v1/auth/register", {
            "username": "frank", "email": "frank@example.com", "password": "password123",
        })
        post_json(client, "/api/v1/auth/login", {"login": "frank@example.com", "password": "password123"})
        rv = client.get("/api/v1/auth/session")
        assert rv.get_json()["data"]["user"]["username"] == "frank"


class TestEnvelopeShape:
    def test_success_envelope_fields(self, client, db):
        rv = post_json(client, "/api/v1/auth/register", {
            "username": "grace", "email": "grace@example.com", "password": "password123",
        })
        body = rv.get_json()
        assert "success" in body
        assert "message" in body
        assert "data" in body
        assert "meta" in body
        assert "links" in body

    def test_error_envelope_fields(self, client):
        rv = post_json(client, "/api/v1/auth/login", {})
        body = rv.get_json()
        # validation_error returns detail array (FastAPI-style)
        assert "detail" in body
