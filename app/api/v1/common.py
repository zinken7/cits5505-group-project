# -*- coding: utf-8 -*-
"""Shared helpers for /api/v1 JSON responses."""
from functools import wraps

from flask import jsonify, request
from flask_login import current_user


def api_response(data=None, message=None, success=True, meta=None, links=None, status=200):
    """Envelope matching OpenAPI APIResponse schema."""
    payload = {
        "success": success,
        "message": message,
        "data": data,
        "meta": meta,
        "links": links,
    }
    return jsonify(payload), status


def validation_error(msg, loc=("body",)):
    """FastAPI-style 422 body."""
    body = {
        "detail": [
            {
                "loc": list(loc),
                "msg": msg,
                "type": "value_error",
            }
        ]
    }
    return jsonify(body), 422


def parse_pagination(limit_default=20, max_limit=100):
    raw_limit = request.args.get("limit", limit_default, type=int)
    raw_offset = request.args.get("offset", 0, type=int)
    if raw_limit is None:
        raw_limit = limit_default
    if raw_offset is None:
        raw_offset = 0
    limit = min(max(raw_limit, 1), max_limit)
    offset = max(raw_offset, 0)
    return limit, offset


def parse_user_id(user_id_str):
    """Path user_id is string in spec; our DB uses integer PK."""
    try:
        return int(user_id_str)
    except (TypeError, ValueError):
        return None


def api_login_required(fn):
    """Return JSON 401 instead of redirecting to HTML login."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return api_response(
                data=None,
                message="Authentication required",
                success=False,
                status=401,
            )
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return api_response(
                data=None,
                message="Authentication required",
                success=False,
                status=401,
            )
        if not getattr(current_user, "is_admin", False):
            return api_response(
                data=None,
                message="Admin privileges required",
                success=False,
                status=403,
            )
        return fn(*args, **kwargs)

    return wrapper
