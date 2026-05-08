# -*- coding: utf-8 -*-
VALID_TYPES = ("anime", "movie", "tvshow")
_VALID_RELEASE = frozenset({"Released", "Ongoing", "Completed"})


class MediaCreateSchema:
    @classmethod
    def validate(cls, data: dict):
        errors = []
        if not (data.get("title") or "").strip():
            errors.append("title is required")
        if len(data.get("title") or "") > 200:
            errors.append("title must be at most 200 characters")
        if data.get("mediaType") not in VALID_TYPES:
            errors.append("mediaType must be anime, movie, or tvshow")

        imdb_key = (data.get("imdbId") or data.get("imdb_id") or "").strip()
        if imdb_key and len(imdb_key) > 20:
            errors.append("imdbId must be at most 20 characters")

        for key, maxlen in (
            ("description", 50_000),
            ("imageUrl", 500),
            ("image_url", 500),
            ("imdbUrl", 500),
            ("imdb_url", 500),
            ("director", 200),
            ("language", 50),
            ("country", 50),
            ("tagline", 300),
            ("awards", 500),
            ("trailerUrl", 500),
            ("trailer_url", 500),
        ):
            val = data.get(key)
            if val is not None and len(str(val)) > maxlen:
                errors.append(f"{key} is too long")

        genres = data.get("genres")
        if genres is not None and not isinstance(genres, list):
            errors.append("genres must be an array of strings")
        elif isinstance(genres, list):
            for g in genres:
                if not isinstance(g, str):
                    errors.append("each genre must be a string")
                    break

        cast = data.get("cast")
        if cast is not None and not isinstance(cast, list):
            errors.append("cast must be an array of strings")
        elif isinstance(cast, list):
            for x in cast:
                if not isinstance(x, str):
                    errors.append("each cast entry must be a string")
                    break

        rs = data.get("releaseStatus") or data.get("release_status")
        if rs is not None and str(rs).strip() and str(rs).strip() not in _VALID_RELEASE:
            errors.append("releaseStatus must be Released, Ongoing, or Completed")

        return errors


class MediaPatchSchema:
    allowed = {"title", "description", "imageUrl", "image_url", "year"}

    @classmethod
    def validate(cls, data: dict):
        errors = []
        title = data.get("title")
        if title is not None and not str(title).strip():
            errors.append("title cannot be blank")
        if title and len(str(title)) > 200:
            errors.append("title must be at most 200 characters")
        return errors
