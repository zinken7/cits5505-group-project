# -*- coding: utf-8 -*-
"""Tests for watchlist service — add, update status, remove, filter."""
import pytest

from app.models.media import Media
from app.services.watchlist_service import (
    add_to_watchlist,
    filter_watchlist,
    patch_watchlist_item,
    remove_from_watchlist,
)
from app.services.auth_service import register_user


@pytest.fixture
def user_and_media(db, app):
    with app.app_context():
        user, _ = register_user("watcher", "watcher@example.com", "password123")
        media = Media(title="Test Anime", media_type="anime", year=2020)
        db.session.add(media)
        db.session.commit()
        yield user, media


def test_add_to_watchlist(user_and_media, app):
    user, media = user_and_media
    with app.app_context():
        item, err = add_to_watchlist(user.id, media.id, status="planned")
        assert err is None
        assert item["status"] == "planned"


def test_add_duplicate_rejected(user_and_media, app):
    user, media = user_and_media
    with app.app_context():
        add_to_watchlist(user.id, media.id, status="planned")
        _, err = add_to_watchlist(user.id, media.id, status="watching")
        assert err is not None


def test_add_invalid_status(user_and_media, app):
    user, media = user_and_media
    with app.app_context():
        _, err = add_to_watchlist(user.id, media.id, status="binge-watching")
        assert err is not None


def test_patch_watchlist_item(user_and_media, app):
    user, media = user_and_media
    with app.app_context():
        item, _ = add_to_watchlist(user.id, media.id, status="planned")
        updated, err = patch_watchlist_item(item["id"], user.id, status="completed")
        assert err is None
        assert updated["status"] == "completed"


def test_remove_from_watchlist(user_and_media, app):
    user, media = user_and_media
    with app.app_context():
        item, _ = add_to_watchlist(user.id, media.id, status="planned")
        ok, err = remove_from_watchlist(item["id"], user.id)
        assert ok is True
        assert err is None


def test_filter_watchlist_by_status():
    items = [
        {"status": "planned", "media": {"media_type": "anime", "title": "Alpha"}, "created_at": "2024-01-01"},
        {"status": "completed", "media": {"media_type": "movie", "title": "Beta"}, "created_at": "2024-01-02"},
    ]
    result, total = filter_watchlist(items, status="planned")
    assert total == 1
    assert result[0]["status"] == "planned"


def test_filter_watchlist_by_media_type():
    items = [
        {"status": "watching", "media": {"media_type": "anime", "title": "Gamma"}, "created_at": ""},
        {"status": "watching", "media": {"media_type": "movie", "title": "Delta"}, "created_at": ""},
    ]
    result, total = filter_watchlist(items, media_type="anime", limit=10)
    assert total == 1
    assert result[0]["media"]["media_type"] == "anime"
