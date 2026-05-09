# -*- coding: utf-8 -*-
VALID_MEDIA_TYPES = ("anime", "movie", "tvshow")
VALID_STATUSES = (
    "watching", "planned", "completed",
    "dropped", "on-hold", "rewatching", "replaying",
)


class WatchlistCreateSchema:
    @classmethod
    def validate(cls, data: dict):
        errors = []
        if data.get("mediaType") not in VALID_MEDIA_TYPES:
            errors.append("mediaType must be anime, movie, or tvshow")
        if data.get("mediaId") is None:
            errors.append("mediaId is required")
        else:
            try:
                int(str(data["mediaId"]))
            except (TypeError, ValueError):
                errors.append("mediaId must be numeric")
        status = data.get("status", "planned")
        if status not in VALID_STATUSES:
            errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}")
        if "isLiked" in data and not isinstance(data.get("isLiked"), bool):
            errors.append("isLiked must be a boolean")
        return errors


class WatchlistPatchSchema:
    @classmethod
    def validate(cls, data: dict):
        errors = []
        has_status = "status" in data
        has_like = "isLiked" in data
        if not has_status and not has_like:
            errors.append("status or isLiked is required")
        status = data.get("status")
        if has_status and status not in VALID_STATUSES:
            errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}")
        if has_like and not isinstance(data.get("isLiked"), bool):
            errors.append("isLiked must be true or false")
        return errors
