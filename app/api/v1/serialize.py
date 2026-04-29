# -*- coding: utf-8 -*-
"""Helpers for converting between camelCase (wire) and snake_case (DB)."""
import re


def _to_camel(key: str) -> str:
    parts = key.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _to_snake(key: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()


def to_camel(d: dict) -> dict:
    """Recursively rename dict keys from snake_case to camelCase."""
    out = {}
    for k, v in d.items():
        new_k = _to_camel(k)
        out[new_k] = to_camel(v) if isinstance(v, dict) else v
    return out


def from_camel(d: dict) -> dict:
    """Recursively rename dict keys from camelCase to snake_case."""
    out = {}
    for k, v in d.items():
        new_k = _to_snake(k)
        out[new_k] = from_camel(v) if isinstance(v, dict) else v
    return out
