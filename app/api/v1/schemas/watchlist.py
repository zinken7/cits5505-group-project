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
        return errors


class WatchlistPatchSchema:
    @classmethod
    def validate(cls, data: dict):
        errors = []
        status = data.get("status")
        if not status:
            errors.append("status is required")
        elif status not in VALID_STATUSES:
            errors.append(f"status must be one of: {', '.join(VALID_STATUSES)}")
        return errors
