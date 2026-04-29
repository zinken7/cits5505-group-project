# -*- coding: utf-8 -*-
from app.extensions import db


class Media(db.Model):
    """Media item — anime, movie, or tvshow.

    Catalog fields (always populated) are returned by to_dict().
    Detail fields (nullable, populated by seeds.py or admin) are
    returned by to_detail_dict() and used by the /items/<imdb_id> endpoint.
    """

    VALID_TYPES = ("movie", "anime", "tvshow")

    __tablename__ = "media"

    # ------------------------------------------------------------------
    # Catalog fields
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    media_type = db.Column(db.String(20), nullable=False, index=True)  # anime | movie | tvshow
    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(500), default="")
    year = db.Column(db.Integer)

    # IMDB metadata
    imdb_id = db.Column(db.String(20), unique=True, nullable=True, index=True)
    rating = db.Column(db.Float, nullable=True)
    votes = db.Column(db.Integer, nullable=True)
    imdb_url = db.Column(db.String(500), default="")
    rank = db.Column(db.Integer, nullable=True)
    genres = db.Column(db.JSON, nullable=True, default=list)

    # ------------------------------------------------------------------
    # Detail fields (nullable — only populated for seeded / enriched items)
    # anime: episodes relevant; movie: runtime_minutes relevant; both share the rest
    # ------------------------------------------------------------------
    runtime_minutes = db.Column(db.Integer, nullable=True)
    episodes = db.Column(db.Integer, nullable=True)
    release_status = db.Column(db.String(30), nullable=True)   # Released | Ongoing | Completed
    director = db.Column(db.String(200), nullable=True)
    cast = db.Column(db.JSON, nullable=True)
    language = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    tagline = db.Column(db.String(300), nullable=True)
    awards = db.Column(db.String(500), nullable=True)
    trailer_url = db.Column(db.String(500), nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    watchlist_items = db.relationship("WatchlistItem", backref="media", lazy="dynamic")

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def to_dict(self):
        """Catalog / list representation — returned by /anime, /movies, /tvshows."""
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

    def to_detail_dict(self):
        """Full representation for the detail page — superset of to_dict()."""
        base = self.to_dict()
        base.update({
            "runtime_minutes": self.runtime_minutes,
            "episodes": self.episodes,
            "release_status": self.release_status,
            "director": self.director or "",
            "cast": self.cast or [],
            "language": self.language or "",
            "country": self.country or "",
            "tagline": self.tagline or "",
            "awards": self.awards or "",
            "trailer_url": self.trailer_url or "",
        })
        return base

    def __repr__(self):
        return f"<Media {self.title} ({self.media_type})>"
