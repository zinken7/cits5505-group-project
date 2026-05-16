# -*- coding: utf-8 -*-
from app.models.media import Media


def test_anonymous_users_can_browse_public_media_pages(client, app, db):
    with app.app_context():
        media = Media(
            title="Public Movie",
            media_type="movie",
            year=2024,
            imdb_id="ttpublic001",
            genres=["Drama"],
        )
        db.session.add(media)
        db.session.commit()

    for path in ("/explore", "/categories", "/search?q=Public", "/items/ttpublic001"):
        rv = client.get(path, follow_redirects=False)
        assert rv.status_code == 200


def test_anonymous_app_shell_shows_guest_actions_not_member_only_links(client):
    rv = client.get("/search")
    html = rv.get_data(as_text=True)

    assert rv.status_code == 200
    assert 'href="/login"' in html
    assert 'href="/register"' in html
    assert 'href="/dashboard"' not in html
    assert 'href="/search-users"' not in html


def test_member_only_pages_still_redirect_anonymous_users_to_login(client):
    for path in ("/dashboard", "/search-users", "/profile/me", "/chat"):
        rv = client.get(path, follow_redirects=False)
        assert rv.status_code == 302
        assert "/login" in rv.headers["Location"]
