# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from app.extensions import db


class WatchlistItem(db.Model):
    """Junction model linking a user to a media item with a status."""

    __tablename__ = "watchlist_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False, index=True)
    status = db.Column(
        db.String(20), nullable=False, default="planned", index=True
    )  # watching | planned | completed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Prevent duplicate entries for the same user + media
    __table_args__ = (
        db.UniqueConstraint("user_id", "media_id", name="uq_user_media"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "media_id": self.media_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "media": self.media.to_dict() if self.media else None,
        }

    def __repr__(self):
        return f"<WatchlistItem user={self.user_id} media={self.media_id} status={self.status}>"
