# -*- coding: utf-8 -*-
from app.models.media import Media
from app.services.tag_service import resolve_tags


def test_resolve_tags_links_shared_numeric_title(client, app, db):
    with app.app_context():
        media = Media(title="1883", media_type="tvshow", imdb_id="tt13991232")
        db.session.add(media)
        db.session.commit()
        media_id = media.id

        tags = resolve_tags("Check out #1883 on WatchList Hub. It's interesting!")

    assert tags == [{
        "text": "1883",
        "media_id": media_id,
        "imdb_id": "tt13991232",
        "title": "1883",
        "image_url": "",
        "url": "/items/tt13991232",
    }]


def test_resolve_tags_links_shared_multi_word_title_with_apostrophe(client, app, db):
    with app.app_context():
        media = Media(title="The Queen's Gambit", media_type="tvshow", imdb_id="tt10048342")
        db.session.add(media)
        db.session.commit()
        media_id = media.id

        tags = resolve_tags("Check out #The Queen's Gambit on WatchList Hub. It's interesting!")

    assert tags == [{
        "text": "The Queen's Gambit",
        "media_id": media_id,
        "imdb_id": "tt10048342",
        "title": "The Queen's Gambit",
        "image_url": "",
        "url": "/items/tt10048342",
    }]


def test_resolve_tags_links_shared_title_with_symbols(client, app, db):
    with app.app_context():
        title = "Spider-Man: Across the Spider-Verse"
        media = Media(title=title, media_type="movie", imdb_id="tt9362722")
        db.session.add(media)
        db.session.commit()
        media_id = media.id

        tags = resolve_tags(f"Check out #{title} on WatchList Hub. It's interesting!")

    assert tags == [{
        "text": title,
        "media_id": media_id,
        "imdb_id": "tt9362722",
        "title": title,
        "image_url": "",
        "url": "/items/tt9362722",
    }]
