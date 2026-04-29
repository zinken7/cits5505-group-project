# -*- coding: utf-8 -*-
"""Signed, time-limited tokens for password reset (no extra DB columns)."""

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from flask import current_app

_SALT = "wh-password-reset"
_DEFAULT_MAX_AGE = 60 * 60 * 24  # 24 hours


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt=_SALT,
    )


def create_reset_token(user_id: int) -> str:
    return _serializer().dumps({"u": int(user_id)})


def verify_reset_token(token: str, max_age: int = _DEFAULT_MAX_AGE) -> int | None:
    try:
        data = _serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    uid = data.get("u")
    if isinstance(uid, int):
        return uid
    return None
