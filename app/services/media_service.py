# -*- coding: utf-8 -*-
from sqlalchemy import cast, String
from app.extensions import db
from app.models.media import Media
from app.models.watchlist import WatchlistItem


def list_media(media_type, q=None, genre=None, sort=None, limit=24, offset=0):
    """Paginated media list with optional genre filtering."""
    query = Media.query.filter_by(media_type=media_type)
    if q:
        like = f"%{q}%"
        query = query.filter(Media.title.ilike(like))
    if genre:
        # Escape LIKE wildcards so a genre string like "%" can't match arbitrary values.
        # Wrapping with quotes ensures only exact array-element matches (["Action"] not ["ActionHero"]).
        safe = genre.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(cast(Media.genres, String).like(f'%"{safe}"%', escape="\\"))

    total = query.count()

    order = sort or "title"
    if order in ("-releaseYear", "-year"):
        query = query.order_by(Media.year.desc().nulls_last(), Media.title)
    elif order in ("releaseYear", "year"):
        query = query.order_by(Media.year.asc().nulls_last(), Media.title)
    elif order == "-rating":
        query = query.order_by(Media.rating.desc().nulls_last(), Media.title)
    elif order == "rating":
        query = query.order_by(Media.rating.asc().nulls_last(), Media.title)
    else:
        query = query.order_by(Media.title.asc())

    rows = query.offset(offset).limit(limit).all()
    return [m.to_dict() for m in rows], total


def get_media(media_id):
    return db.session.get(Media, media_id)


def get_media_by_imdb_id(imdb_id):
    return Media.query.filter_by(imdb_id=imdb_id).first()


def create_media(
    title,
    media_type,
    *,
    description="",
    image_url="",
    year=None,
    imdb_id=None,
    imdb_url="",
    rating=None,
    votes=None,
    rank=None,
    genres=None,
    runtime_minutes=None,
    episodes=None,
    release_status=None,
    director=None,
    cast=None,
    language=None,
    country=None,
    tagline=None,
    awards=None,
    trailer_url=None,
):
    """Insert a catalogue row. Empty ``imdb_id`` becomes ``manual-<pk>`` after flush.

    :raises ValueError: if ``imdb_id`` is already used
    """
    title = (title or "").strip()
    if not title:
        raise ValueError("Title is required.")

    imdb_key = (imdb_id or "").strip() or None
    if imdb_key and get_media_by_imdb_id(imdb_key):
        raise ValueError("This IMDb ID is already in the catalogue.")

    g = genres if genres else []
    c = cast if cast else []

    m = Media(
        title=title,
        media_type=media_type,
        description=description or "",
        image_url=image_url or "",
        year=year,
        imdb_id=imdb_key,
        imdb_url=(imdb_url or "").strip(),
        rating=rating,
        votes=votes,
        rank=rank,
        genres=g,
        runtime_minutes=runtime_minutes,
        episodes=episodes,
        release_status=release_status,
        director=director,
        cast=c,
        language=language,
        country=country,
        tagline=(tagline or "")[:300] if tagline else None,
        awards=(awards or "")[:500] if awards else None,
        trailer_url=(trailer_url or "").strip(),
    )
    db.session.add(m)
    db.session.flush()
    if not (m.imdb_id and str(m.imdb_id).strip()):
        m.imdb_id = f"manual-{m.id}"
    db.session.commit()
    return m


_UPDATE_KEYS = frozenset(
    {
        "title",
        "description",
        "image_url",
        "year",
        "media_type",
        "imdb_id",
        "imdb_url",
        "rating",
        "votes",
        "rank",
        "genres",
        "runtime_minutes",
        "episodes",
        "release_status",
        "director",
        "cast",
        "language",
        "country",
        "tagline",
        "awards",
        "trailer_url",
    }
)


def list_media_admin_page(limit=15, offset=0):
    """Paginated media rows for admin tables."""
    query = Media.query.order_by(Media.title.asc())
    total = query.count()
    rows = query.offset(offset).limit(limit).all()
    return rows, total


def list_all_media_admin(limit=2000):
    """All media rows for admin tables (bounded)."""
    rows, _ = list_media_admin_page(limit=limit, offset=0)
    return rows


def update_media(media_id, **fields):
    """Patch fields on a media row. Raises ``ValueError`` on duplicate ``imdb_id``.

    When ``imdb_id`` is set empty, it becomes ``manual-<pk>``.
    """
    m = db.session.get(Media, media_id)
    if not m:
        return None

    if "imdb_id" in fields:
        raw = fields["imdb_id"]
        new_key = (raw or "").strip() if raw is not None else None
        if not new_key:
            new_key = f"manual-{m.id}"
        elif new_key != m.imdb_id:
            other = get_media_by_imdb_id(new_key)
            if other and other.id != m.id:
                raise ValueError("This IMDb ID is already in the catalogue.")
        fields["imdb_id"] = new_key

    for key in _UPDATE_KEYS:
        if key not in fields or key == "imdb_id":
            continue
        val = fields[key]
        if key == "genres":
            m.genres = val if val is not None else []
            continue
        if key == "cast":
            m.cast = val if val is not None else []
            continue
        if key == "title":
            m.title = (val or "").strip() if val is not None else m.title
            continue
        if key in ("description", "image_url", "imdb_url", "trailer_url"):
            setattr(m, key, (val or "").strip() if val is not None else "")
            continue
        if key in ("director", "language", "country"):
            s = (val or "").strip() if val is not None else None
            setattr(m, key, s or None)
            continue
        if key in ("tagline", "awards"):
            if val is None:
                setattr(m, key, None)
            else:
                cap = 300 if key == "tagline" else 500
                setattr(m, key, (str(val).strip()[:cap] or None))
            continue
        setattr(m, key, val)

    if "imdb_id" in fields:
        m.imdb_id = fields["imdb_id"]

    db.session.commit()
    return m


def delete_media(media_id):
    m = db.session.get(Media, media_id)
    if not m:
        return False
    WatchlistItem.query.filter_by(media_id=m.id).delete()
    db.session.delete(m)
    db.session.commit()
    return True
