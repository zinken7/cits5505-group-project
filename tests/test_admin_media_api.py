# -*- coding: utf-8 -*-
import json
import re

from app.extensions import db
from app.models.media import Media
from app.models.user import User


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def login_admin(client, app):
    with app.app_context():
        admin = User(username="admin", email="admin@example.com", is_admin=True)
        admin.set_password("password123")
        db.session.add(admin)
        db.session.commit()
    return post_json(client, "/api/v1/auth/login", {
        "login": "admin@example.com",
        "password": "password123",
    })


def seed_media(app, count=20):
    with app.app_context():
        for i in range(count):
            db.session.add(Media(title=f"Title {i:02d}", media_type="movie"))
        db.session.commit()


def test_admin_media_list_requires_admin(client):
    rv = client.get("/api/v1/management/media?limit=15&offset=0")
    assert rv.status_code == 401
    assert rv.get_json()["success"] is False


def test_admin_media_list_is_paginated(client, app, db):
    login_admin(client, app)
    seed_media(app, count=20)

    rv = client.get("/api/v1/management/media?limit=15&offset=0")
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["success"] is True
    assert body["data"]["total"] == 20
    assert body["data"]["limit"] == 15
    assert body["data"]["offset"] == 0
    assert len(body["data"]["items"]) == 15
    assert body["data"]["items"][0]["title"] == "Title 00"

    rv = client.get("/api/v1/management/media?limit=15&offset=15")
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["data"]["total"] == 20
    assert body["data"]["offset"] == 15
    assert len(body["data"]["items"]) == 5


def test_manage_media_page_renders_first_page(client, app, db):
    login_admin(client, app)
    seed_media(app, count=20)

    rv = client.get("/management/media")
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'data-api-url="/api/v1/management/media"' in html
    tbody = re.search(r'<tbody id="media-table-body">(.*?)</tbody>', html, re.S)
    assert tbody is not None
    assert len(re.findall(r"<tr[^>]+data-media-row>", tbody.group(1))) == 15


def test_manage_media_page_preserves_page_from_query(client, app, db):
    login_admin(client, app)
    seed_media(app, count=20)

    rv = client.get("/management/media?page=2")
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert "Page 2 of 2" in html
    tbody = re.search(r'<tbody id="media-table-body">(.*?)</tbody>', html, re.S)
    assert tbody is not None
    assert len(re.findall(r"<tr[^>]+data-media-row>", tbody.group(1))) == 5
    assert "Title 15" in tbody.group(1)
