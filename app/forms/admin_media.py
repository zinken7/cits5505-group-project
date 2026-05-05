# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class AdminMediaForm(FlaskForm):
    media_type = SelectField(
        "Type",
        choices=[("movie", "Movie"), ("anime", "Anime"), ("tvshow", "TV show")],
        validators=[DataRequired()],
    )
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField("Description", validators=[Optional()])
    image_url = StringField("Poster image URL", validators=[Optional(), Length(max=500)])
    year = IntegerField("Release year", validators=[Optional(), NumberRange(min=1874, max=2100)])

    imdb_id = StringField(
        "IMDb ID",
        validators=[Optional(), Length(max=20)],
        render_kw={
            "placeholder": "e.g. tt0111161 — leave blank to auto-generate",
        },
    )
    imdb_url = StringField("IMDb URL", validators=[Optional(), Length(max=500)])
    rating = FloatField("Rating (0–10)", validators=[Optional(), NumberRange(min=0, max=10)])
    votes = IntegerField("Vote count", validators=[Optional(), NumberRange(min=0)])
    rank = IntegerField("Chart rank (e.g. Top 250)", validators=[Optional(), NumberRange(min=0)])

    genres_raw = TextAreaField(
        "Genres (one per line)",
        validators=[Optional()],
        render_kw={"placeholder": "Action\nDrama", "rows": 3},
    )
    runtime_minutes = IntegerField("Runtime (minutes)", validators=[Optional(), NumberRange(min=0)])
    episodes = IntegerField("Episodes", validators=[Optional(), NumberRange(min=0)])
    release_status = SelectField(
        "Release status",
        choices=[
            ("", "— Optional —"),
            ("Released", "Released"),
            ("Ongoing", "Ongoing"),
            ("Completed", "Completed"),
        ],
        validators=[Optional()],
    )
    director = StringField("Director", validators=[Optional(), Length(max=200)])
    cast_raw = TextAreaField(
        "Cast (one name per line)",
        validators=[Optional()],
        render_kw={"placeholder": "Actor One\nActor Two", "rows": 4},
    )
    language = StringField("Language", validators=[Optional(), Length(max=50)])
    country = StringField("Country", validators=[Optional(), Length(max=50)])
    tagline = StringField("Tagline", validators=[Optional(), Length(max=300)])
    awards = StringField("Awards", validators=[Optional(), Length(max=500)])
    trailer_url = StringField("Trailer URL", validators=[Optional(), Length(max=500)])

    def populate_from_media(self, media):
        """Fill fields from a :class:`~app.models.media.Media` instance (for edit)."""
        self.media_type.data = media.media_type
        self.title.data = media.title
        self.description.data = media.description or ""
        self.image_url.data = media.image_url or ""
        self.year.data = media.year
        self.imdb_id.data = media.imdb_id or ""
        self.imdb_url.data = media.imdb_url or ""
        self.rating.data = media.rating
        self.votes.data = media.votes
        self.rank.data = media.rank
        self.genres_raw.data = "\n".join(media.genres or [])
        self.cast_raw.data = "\n".join(media.cast or []) if media.cast else ""
        self.runtime_minutes.data = media.runtime_minutes
        self.episodes.data = media.episodes
        self.release_status.data = media.release_status or ""
        self.director.data = media.director or ""
        self.language.data = media.language or ""
        self.country.data = media.country or ""
        self.tagline.data = media.tagline or ""
        self.awards.data = media.awards or ""
        self.trailer_url.data = media.trailer_url or ""

    def to_create_kwargs(self):
        """Map form values to keyword arguments for :func:`create_media`."""
        gtxt = (self.genres_raw.data or "").strip()
        genres = [line.strip() for line in gtxt.splitlines() if line.strip()] if gtxt else None

        ctxt = (self.cast_raw.data or "").strip()
        cast = [line.strip() for line in ctxt.splitlines() if line.strip()] if ctxt else None

        imdb_id = (self.imdb_id.data or "").strip() or None
        rs = (self.release_status.data or "").strip() or None

        return {
            "description": (self.description.data or "").strip(),
            "image_url": (self.image_url.data or "").strip(),
            "year": self.year.data,
            "imdb_id": imdb_id,
            "imdb_url": (self.imdb_url.data or "").strip(),
            "rating": self.rating.data,
            "votes": self.votes.data,
            "rank": self.rank.data,
            "genres": genres,
            "runtime_minutes": self.runtime_minutes.data,
            "episodes": self.episodes.data,
            "release_status": rs,
            "director": (self.director.data or "").strip() or None,
            "cast": cast,
            "language": (self.language.data or "").strip() or None,
            "country": (self.country.data or "").strip() or None,
            "tagline": (self.tagline.data or "").strip() or None,
            "awards": (self.awards.data or "").strip() or None,
            "trailer_url": (self.trailer_url.data or "").strip() or None,
        }
