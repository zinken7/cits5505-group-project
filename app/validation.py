# -*- coding: utf-8 -*-
import re

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 80
USERNAME_PATTERN = r"^[A-Za-z0-9_]+$"
USERNAME_RE = re.compile(USERNAME_PATTERN)
USERNAME_LENGTH_MESSAGE = (
    f"Username must be between {USERNAME_MIN_LENGTH} and {USERNAME_MAX_LENGTH} characters"
)
USERNAME_CHARACTERS_MESSAGE = "Username can only contain letters, numbers, and underscores"


def validate_username(username):
    if len(username) < USERNAME_MIN_LENGTH or len(username) > USERNAME_MAX_LENGTH:
        return USERNAME_LENGTH_MESSAGE
    if not USERNAME_RE.fullmatch(username):
        return USERNAME_CHARACTERS_MESSAGE
    return None
