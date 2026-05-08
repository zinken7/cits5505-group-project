# -*- coding: utf-8 -*-
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.watchlist import WatchlistItem
from app.models.media import Media


VALID_STATUSES = {
    "watching",
    "planned",
    "completed",
    "dropped",
    "on-hold",
    "rewatching",
    "replaying",
}


def get_user_watchlist(user_id, status=None):
    """Get a user's watchlist items, optionally filtered by status.

    Returns a list of dicts ready for JSON serialization.
    """
    query = WatchlistItem.query.filter_by(user_id=user_id)
    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)

    items = query.order_by(WatchlistItem.created_at.desc()).all()
    return [item.to_dict() for item in items]


def get_watchlist_item_by_media(user_id, media_id):
    """Return the current user's watchlist item for one media item, if any."""
    media = db.session.get(Media, media_id)
    if not media:
        return None, "Media not found"

    item = WatchlistItem.query.filter_by(user_id=user_id, media_id=media_id).first()
    return item.to_dict() if item else None, None


def add_to_watchlist(user_id, media_id, status="planned"):
    """Add a media item to a user's watchlist.

    Returns (item_dict, None) on success or (None, error_message) on failure.
    """
    if status not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

    # Check if media exists
    media = db.session.get(Media, media_id)
    if not media:
        return None, "Media not found"

    # Check for duplicate
    existing = WatchlistItem.query.filter_by(
        user_id=user_id, media_id=media_id
    ).first()
    if existing:
        return None, "Item already in your watchlist"

    item = WatchlistItem(user_id=user_id, media_id=media_id, status=status)
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, "Item already in your watchlist"
    return item.to_dict(), None


def set_watchlist_status(user_id, media_id, status="planned"):
    """Create or update the current user's watchlist status for a media item."""
    if status not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

    media = db.session.get(Media, media_id)
    if not media:
        return None, "Media not found"

    item = WatchlistItem.query.filter_by(user_id=user_id, media_id=media_id).first()
    if item:
        if item.status != status:
            item.status = status
            db.session.commit()
        return item.to_dict(), None

    item = WatchlistItem(user_id=user_id, media_id=media_id, status=status)
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        item = WatchlistItem.query.filter_by(user_id=user_id, media_id=media_id).first()
        if not item:
            return None, "Could not update watchlist"
        if item.status != status:
            item.status = status
            db.session.commit()
    return item.to_dict(), None


def update_status(item_id, new_status, user_id):
    """Update the status of a watchlist item.

    Returns (item_dict, None) on success or (None, error_message) on failure.
    """
    if new_status not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

    item = db.session.get(WatchlistItem, item_id)
    if not item:
        return None, "Item not found"
    if item.user_id != user_id:
        return None, "Unauthorized"

    item.status = new_status
    db.session.commit()
    return item.to_dict(), None


def get_watchlist_item(item_id, user_id):
    """Return one item for the owner."""
    item = db.session.get(WatchlistItem, item_id)
    if not item:
        return None, "Item not found"
    if item.user_id != user_id:
        return None, "Unauthorized"
    return item.to_dict(), None


def patch_watchlist_item(item_id, user_id, status=None):
    """Update status (other fields reserved for future columns)."""
    if status is None:
        return None, "status is required"
    return update_status(item_id, status, user_id)


def remove_from_watchlist(item_id, user_id):
    """Remove an item from the user's watchlist.

    Returns (True, None) on success or (False, error_message) on failure.
    """
    item = db.session.get(WatchlistItem, item_id)
    if not item:
        return False, "Item not found"
    if item.user_id != user_id:
        return False, "Unauthorized"

    db.session.delete(item)
    db.session.commit()
    return True, None


def remove_from_watchlist_by_media(user_id, media_id):
    """Remove the current user's watchlist item for a media item.

    The operation is idempotent: removing an item that is already absent
    still succeeds and reports deleted=False.
    """
    item = WatchlistItem.query.filter_by(user_id=user_id, media_id=media_id).first()
    if not item:
        return False

    db.session.delete(item)
    db.session.commit()
    return True


def filter_watchlist(items, status=None, media_type=None, q=None, sort="-updatedAt", limit=12, offset=0):
    """Filter, sort, and paginate a list of watchlist item dicts."""
    out = list(items)
    if status:
        out = [i for i in out if i.get("status") == status]
    if media_type:
        out = [i for i in out if (i.get("media") or {}).get("media_type") == media_type]
    if q:
        ql = q.lower()
        out = [i for i in out if ql in (i.get("media") or {}).get("title", "").lower()]
    reverse = sort.startswith("-")
    sk = sort.lstrip("-")
    if sk in ("updatedAt", "createdAt", "created_at"):
        key = "created_at"
        out = sorted(out, key=lambda x: x.get(key) or "", reverse=reverse)
    total = len(out)
    return out[offset: offset + limit], total


def counts_for_imdb_id(imdb_id):
    """Return live watchlist counts for a media item identified by imdb_id."""
    media = Media.query.filter_by(imdb_id=imdb_id).first()
    if not media:
        return {"watching": 0, "completed": 0, "planned": 0, "total": 0}
    rows = (
        db.session.query(WatchlistItem.status, func.count(WatchlistItem.id))
        .filter(WatchlistItem.media_id == media.id)
        .group_by(WatchlistItem.status)
        .all()
    )
    counts = {status: count for status, count in rows}
    watching = counts.get("watching", 0) + counts.get("rewatching", 0) + counts.get("replaying", 0)
    completed = counts.get("completed", 0)
    planned = counts.get("planned", 0)
    total = sum(counts.values())
    return {"watching": watching, "completed": completed, "planned": planned, "total": total}


def get_trending(media_type=None, limit=10):
    """Get the most popular media items across all users.

    Popularity = number of users who have the item in any watchlist.
    Returns a list of dicts with media info + count.
    """
    query = (
        db.session.query(Media, func.count(WatchlistItem.id).label("count"))
        .join(WatchlistItem, WatchlistItem.media_id == Media.id)
        .group_by(Media.id)
        .order_by(func.count(WatchlistItem.id).desc())
    )

    if media_type:
        query = query.filter(Media.media_type == media_type)

    results = query.limit(limit).all()

    return [
        {**media.to_dict(), "watchlist_count": count}
        for media, count in results
    ]
