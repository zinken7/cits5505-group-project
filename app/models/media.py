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

    # IMDB metadata
    imdb_id = db.Column(db.String(20), unique=True, nullable=True, index=True)
    rating = db.Column(db.Float, nullable=True)
    votes = db.Column(db.Integer, nullable=True)
    imdb_url = db.Column(db.String(500), default="")
    rank = db.Column(db.Integer, nullable=True)
    genres = db.Column(db.JSON, nullable=True, default=[])  # List of genre strings

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
            "imdb_id": self.imdb_id,
            "rating": self.rating,
            "votes": self.votes,
            "imdb_url": self.imdb_url,
            "rank": self.rank,
            "genres": self.genres or [],
        }

    def __repr__(self):
        return f"<Media {self.title} ({self.media_type})>"
