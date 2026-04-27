# -*- coding: utf-8 -*-
VALID_TYPES = ("anime", "movie", "tvshow")


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
