# -*- coding: utf-8 -*-
from app.extensions import db
from app.models.user import User
from app.services.auth_service import register_user
from app.services.password_reset_service import create_reset_token, verify_reset_token


def test_verify_reset_token_invalid(app):
    with app.app_context():
        assert verify_reset_token("not-a-real-token") is None


def test_reset_password_updates_password_and_allows_login(client, app, db):
    with app.app_context():
        user, err = register_user("pwreset", "pwreset@example.com", "oldpassword12")
        assert err is None
        token = create_reset_token(user.id)
        assert verify_reset_token(token) == user.id

    rv = client.post(
        f"/reset-password/{token}",
        data={
            "password": "newpassword12",
            "password_confirm": "newpassword12",
        },
        follow_redirects=False,
    )
    assert rv.status_code == 302
    assert "/login" in rv.headers.get("Location", "")

    rv2 = client.post(
        "/login",
        data={"email": "pwreset@example.com", "password": "newpassword12"},
        follow_redirects=False,
    )
    assert rv2.status_code == 302

    with app.app_context():
        u = User.query.filter_by(email="pwreset@example.com").first()
        assert u is not None
        assert u.check_password("newpassword12")


def test_forgot_password_redirects_for_unknown_email(client, db):
    rv = client.post(
        "/forgot-password",
        data={"email": "nobody-here@example.com"},
        follow_redirects=False,
    )
    assert rv.status_code == 302
    assert "/login" in rv.headers.get("Location", "")
