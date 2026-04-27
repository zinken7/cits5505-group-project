# -*- coding: utf-8 -*-
import re
from datetime import date

VALID_VISIBILITY = ("public", "followers", "private")
_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_]{3,30}$')


class UserMePatchSchema:
    @classmethod
    def validate(cls, data: dict):
        errors = []

        display_name = data.get("displayName")
        if display_name is not None and len(str(display_name)) > 80:
            errors.append("displayName must be at most 80 characters")

        bio = data.get("bio")
        if bio is not None and len(str(bio)) > 500:
            errors.append("bio must be at most 500 characters")

        username = data.get("username")
        if username is not None:
            if not _USERNAME_RE.match(str(username)):
                errors.append("username must be 3–30 characters: letters, numbers, underscores only")

        dob = data.get("dateOfBirth")
        if dob is not None and dob != "":
            try:
                date.fromisoformat(str(dob))
            except ValueError:
                errors.append("dateOfBirth must be a valid date (YYYY-MM-DD)")

        visibility = data.get("visibility")
        if visibility is not None:
            if not isinstance(visibility, dict):
                errors.append("visibility must be an object")
            else:
                w = visibility.get("watchlist")
                if w is not None and w not in VALID_VISIBILITY:
                    errors.append(f"visibility.watchlist must be one of: {', '.join(VALID_VISIBILITY)}")

        return errors
