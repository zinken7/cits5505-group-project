# -*- coding: utf-8 -*-
from app.extensions import db
from app.models.media import Media
from app.models.watchlist import WatchlistItem


def list_media(media_type, q=None, genre=None, sort=None, limit=24, offset=0):
    """Paginated media list. `genre` is reserved for future schema."""
    query = Media.query.filter_by(media_type=media_type)
    if q:
        like = f"%{q}%"
        query = query.filter(Media.title.ilike(like))
    if genre:
        query = query.filter(Media.description.ilike(f"%{genre}%"))

    total = query.count()

    order = sort or "title"
    if order in ("-releaseYear", "-year"):
        query = query.order_by(Media.year.desc().nulls_last(), Media.title)
    elif order in ("releaseYear", "year"):
        query = query.order_by(Media.year.asc().nulls_last(), Media.title)
    else:
        query = query.order_by(Media.title.asc())

    rows = query.offset(offset).limit(limit).all()
    return [m.to_dict() for m in rows], total


def get_media(media_id):
    return db.session.get(Media, media_id)


def create_media(title, media_type, description="", image_url="", year=None):
    m = Media(
        title=title,
        media_type=media_type,
        description=description or "",
        image_url=image_url or "",
        year=year,
    )
    db.session.add(m)
    db.session.commit()
    return m


def update_media(media_id, **fields):
    m = db.session.get(Media, media_id)
    if not m:
        return None
    for key in ("title", "description", "image_url", "year", "media_type"):
        if key in fields and fields[key] is not None:
            setattr(m, key, fields[key])
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
