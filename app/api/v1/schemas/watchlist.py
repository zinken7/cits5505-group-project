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
        status = data.get("status")
        is_liked_present = "isLiked" in data
        if status is None and not is_liked_present:
            errors.append("status or isLiked is required")
        elif status is not None and status not in VALID_STATUSES:
            errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}")
        if is_liked_present and not isinstance(data.get("isLiked"), bool):
            errors.append("isLiked must be a boolean")
        return errors
