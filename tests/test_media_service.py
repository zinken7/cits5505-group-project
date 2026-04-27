# -*- coding: utf-8 -*-
"""Tests for media service — list, filter, create, update, delete."""
import pytest

from app.models.media import Media
from app.services.media_service import (
    create_media,
    delete_media,
    get_media,
    get_media_by_imdb_id,
    list_media,
    update_media,
)


@pytest.fixture
def seeded_media(db, app):
    with app.app_context():
        items = [
            Media(title="Spirited Away", media_type="anime", year=2001, genres=["Adventure", "Fantasy"], imdb_id="tt0245429"),
            Media(title="Akira", media_type="anime", year=1988, genres=["Sci-Fi", "Action"], imdb_id="tt0094625"),
            Media(title="The Matrix", media_type="movie", year=1999, genres=["Action", "Sci-Fi"]),
        ]
        for m in items:
            db.session.add(m)
        db.session.commit()
        yield items


def test_list_media_by_type(seeded_media, app):
    with app.app_context():
        results, total = list_media("anime")
        assert total == 2


def test_list_media_genre_filter(seeded_media, app):
    with app.app_context():
        results, total = list_media("anime", genre="Fantasy")
        assert total == 1
        assert results[0]["title"] == "Spirited Away"


def test_list_media_genre_no_wildcard_injection(seeded_media, app):
    with app.app_context():
        # "%" should match nothing, not everything
        results, total = list_media("anime", genre="%")
        assert total == 0


def test_list_media_search(seeded_media, app):
    with app.app_context():
        results, total = list_media("anime", q="akira")
        assert total == 1


def test_get_media(seeded_media, app):
    with app.app_context():
        m = seeded_media[0]
        found = get_media(m.id)
        assert found is not None
        assert found.title == "Spirited Away"


def test_get_media_by_imdb_id(seeded_media, app):
    with app.app_context():
        found = get_media_by_imdb_id("tt0245429")
        assert found is not None


def test_create_and_delete_media(db, app):
    with app.app_context():
        m = create_media("New Show", "anime", year=2024)
        assert m.id is not None
        ok = delete_media(m.id)
        assert ok is True
        assert get_media(m.id) is None


def test_update_media(db, app):
    with app.app_context():
        m = create_media("Old Title", "movie")
        updated = update_media(m.id, title="New Title")
        assert updated.title == "New Title"
