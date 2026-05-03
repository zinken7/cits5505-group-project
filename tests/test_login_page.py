# -*- coding: utf-8 -*-
from app.services.auth_service import register_user


def _page_text(response):
    return response.get_data(as_text=True)


def test_login_page_shows_field_errors_for_missing_fields(client, db):
    rv = client.post("/login", data={}, follow_redirects=False)

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "Email is required." in html
    assert "Password is required." in html


def test_login_page_shows_invalid_credentials_and_keeps_email(client, db):
    rv = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "wrongpassword"},
        follow_redirects=False,
    )

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "Invalid email or password." in html
    assert 'value="nobody@example.com"' in html


def test_login_page_remember_me_sets_persistent_cookie(client, db):
    user, error = register_user("rememberme", "rememberme@example.com", "password123")
    assert user is not None
    assert error is None

    rv = client.post(
        "/login",
        data={
            "email": "rememberme@example.com",
            "password": "password123",
            "remember": "y",
        },
        follow_redirects=False,
    )

    cookies = rv.headers.getlist("Set-Cookie")
    assert rv.status_code == 302
    assert any(cookie.startswith("remember_token=") for cookie in cookies)


def test_login_page_without_remember_me_uses_session_only(client, db):
    user, error = register_user("sessiononly", "sessiononly@example.com", "password123")
    assert user is not None
    assert error is None

    rv = client.post(
        "/login",
        data={"email": "sessiononly@example.com", "password": "password123"},
        follow_redirects=False,
    )

    cookies = rv.headers.getlist("Set-Cookie")
    assert rv.status_code == 302
    assert not any(cookie.startswith("remember_token=") for cookie in cookies)


def test_login_page_has_desktop_layout_markup(client):
    rv = client.get("/login")

    html = _page_text(rv)
    assert rv.status_code == 200
    assert "lg:grid-cols-2" in html
    assert "hidden lg:flex" in html


def test_login_page_has_mobile_friendly_markup(client):
    rv = client.get("/login")

    html = _page_text(rv)
    assert rv.status_code == 200
    assert 'name="viewport" content="width=device-width, initial-scale=1.0"' in html
    assert "max-w-sm" in html
    assert "px-8 py-12" in html
