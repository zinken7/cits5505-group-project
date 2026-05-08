# -*- coding: utf-8 -*-
import json

from app.extensions import db
from app.models.media import Media
from app.models.user import User
from app.models.watchlist import WatchlistItem


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def patch_json(client, url, payload):
    return client.patch(url, data=json.dumps(payload), content_type="application/json")


def make_user(username, email, password="password123", *, is_admin=False, is_root=False):
    user = User(username=username, email=email, is_admin=is_admin, is_root=is_root)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, password="password123"):
    return post_json(client, "/api/v1/auth/login", {"login": email, "password": password})


def test_admin_deactivate_user_preserves_data_and_hides_profile(client, app, db):
    with app.app_context():
        admin = make_user("admin", "admin@example.com", is_admin=True)
        user = make_user("target", "target@example.com")
        media = Media(title="Kept Movie", media_type="movie")
        db.session.add(media)
        db.session.commit()
        db.session.add(WatchlistItem(user_id=user.id, media_id=media.id, status="planned"))
        db.session.commit()
        user_id = user.id

    login(client, "admin@example.com")
    rv = patch_json(client, f"/api/v1/management/users/{user_id}", {"deactivated": True})
    assert rv.status_code == 200
    assert rv.get_json()["data"]["deactivated"] is True

    with app.app_context():
        stored = db.session.get(User, user_id)
        assert stored is not None
        assert stored.deactivated is True
        assert WatchlistItem.query.filter_by(user_id=user_id).count() == 1

    rv = client.get("/profile/target")
    assert rv.status_code == 404

    rv = client.get(f"/api/v1/users/{user_id}")
    assert rv.status_code == 404


def test_deactivated_user_cannot_login(client, app, db):
    with app.app_context():
        user = make_user("inactive", "inactive@example.com")
        user.deactivated = True
        db.session.commit()

    rv = login(client, "inactive@example.com")
    assert rv.status_code == 401
    assert rv.get_json()["success"] is False


def test_user_delete_me_soft_deactivates_and_logs_out(client, app, db):
    with app.app_context():
        user = make_user("selfdelete", "selfdelete@example.com")
        user_id = user.id

    login(client, "selfdelete@example.com")
    rv = client.delete("/api/v1/users/me")
    assert rv.status_code == 200
    assert rv.get_json()["data"]["deactivated"] is True

    with app.app_context():
        stored = db.session.get(User, user_id)
        assert stored is not None
        assert stored.deactivated is True

    rv = client.get("/api/v1/users/me")
    assert rv.status_code == 401


def test_manage_users_page_and_post_deactivate(client, app, db):
    with app.app_context():
        make_user("admin", "admin@example.com", is_admin=True)
        target = make_user("member", "member@example.com")
        target_id = target.id

    login(client, "admin@example.com")
    rv = client.get("/management/users")
    assert rv.status_code == 200
    assert "Manage users" in rv.get_data(as_text=True)

    rv = client.post("/management/users", data={"user_id": target_id, "action": "deactivate"})
    assert rv.status_code == 302

    with app.app_context():
        assert db.session.get(User, target_id).deactivated is True


def test_old_admin_management_urls_are_gone(client, app, db):
    with app.app_context():
        make_user("admin", "admin@example.com", is_admin=True, is_root=True)

    login(client, "admin@example.com")
    rv = client.get("/admin/" + "users")
    assert rv.status_code == 404

    rv = client.get("/admin/" + "admins")
    assert rv.status_code == 404
