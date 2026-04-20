# -*- coding: utf-8 -*-
from app.extensions import db


class Item(db.Model):
    """Detail-page extension of a Media row.

    One-to-one with Media via `imdb_id`. Stores editorial fields that are
    specific to the /items/<imdb_id> detail page (genres, cast, runtime,
    community counts, etc.) and are not present on the base Media record.
    """

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    imdb_id = db.Column(
        db.String(20),
        db.ForeignKey("media.imdb_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Editorial / detail metadata
    genres = db.Column(db.JSON, default=list)          # e.g. ["Drama", "Crime"]
    runtime_minutes = db.Column(db.Integer, nullable=True)
    episodes = db.Column(db.Integer, nullable=True)    # anime / TV only
    status = db.Column(db.String(30), default="Released")  # Released / Ongoing / Completed
    director = db.Column(db.String(200), default="")
    cast = db.Column(db.JSON, default=list)            # list[str]
    language = db.Column(db.String(50), default="")
    country = db.Column(db.String(50), default="")
    tagline = db.Column(db.String(300), default="")
    awards = db.Column(db.String(500), default="")
    trailer_url = db.Column(db.String(500), default="")

    # Static demo community counts (seed-time; not derived from watchlist_items)
    watching_count = db.Column(db.Integer, default=0)
    completed_count = db.Column(db.Integer, default=0)
    planned_count = db.Column(db.Integer, default=0)

    media = db.relationship(
        "Media",
        primaryjoin="Item.imdb_id == Media.imdb_id",
        foreign_keys=[imdb_id],
        uselist=False,
        backref=db.backref("item_detail", uselist=False),
    )

    @property
    def watchlist_count(self):
        return (self.watching_count or 0) + (self.completed_count or 0) + (self.planned_count or 0)

    def to_dict(self):
        return {
            "imdb_id": self.imdb_id,
            "genres": self.genres or [],
            "runtime_minutes": self.runtime_minutes,
            "episodes": self.episodes,
            "status": self.status,
            "director": self.director,
            "cast": self.cast or [],
            "language": self.language,
            "country": self.country,
            "tagline": self.tagline,
            "awards": self.awards,
            "trailer_url": self.trailer_url,
            "watching_count": self.watching_count or 0,
            "completed_count": self.completed_count or 0,
            "planned_count": self.planned_count or 0,
            "watchlist_count": self.watchlist_count,
        }

    def __repr__(self):
        return f"<Item imdb={self.imdb_id}>"
