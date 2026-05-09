# -*- coding: utf-8 -*-
from app.models.user import User


def _page_text(response):
    return response.get_data(as_text=True)


def test_register_page_uses_auth_layout_and_login_link(client):
    rv = client.get("/register")

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "lg:grid-cols-2" in html
    assert "hidden lg:flex" in html
    assert "Create your account" in html
    assert 'href="/login"' in html


def test_register_page_shows_required_field_errors(client, db):
    rv = client.post("/register", data={}, follow_redirects=False)

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "Username is required." in html
    assert "Email is required." in html
    assert "Password is required." in html


def test_register_page_enforces_backend_password_minimum(client, db):
    rv = client.post(
        "/register",
        data={
            "username": "shortpw",
            "email": "shortpw@example.com",
            "password": "short",
        },
        follow_redirects=False,
    )

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "Password must be between 8 and 128 characters." in html


def test_register_page_enforces_username_rules(client, db):
    rv = client.post(
        "/register",
        data={
            "username": "se",
            "email": "shortname@example.com",
            "password": "password123",
        },
        follow_redirects=False,
    )

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "Username must be between 3 and 80 characters." in html

    rv = client.post(
        "/register",
        data={
            "username": "bad name!",
            "email": "badname@example.com",
            "password": "password123",
        },
        follow_redirects=False,
    )

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "Username can only contain letters, numbers, and underscores." in html


def test_register_page_success_redirects_to_dashboard(client, app, db):
    rv = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
        follow_redirects=False,
    )

    assert rv.status_code == 302
    assert rv.headers["Location"].endswith("/dashboard")

    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.email == "newuser@example.com"
