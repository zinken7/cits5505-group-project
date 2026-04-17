# -*- coding: utf-8 -*-
from app.extensions import db


class Media(db.Model):
    """Media item model (anime, game, or movie)."""

    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    media_type = db.Column(db.String(20), nullable=False, index=True)  # anime | game | movie
    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(500), default="")
    year = db.Column(db.Integer)

    # Relationship
    watchlist_items = db.relationship("WatchlistItem", backref="media", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "media_type": self.media_type,
            "description": self.description,
            "image_url": self.image_url,
            "year": self.year,
        }

    def __repr__(self):
        return f"<Media {self.title} ({self.media_type})>"
