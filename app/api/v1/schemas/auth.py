# -*- coding: utf-8 -*-
import re


_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


class RegisterSchema:
    required = ("username", "email", "password")
    max_lengths = {"username": 80, "email": 120, "password": 128, "displayName": 80}

    @classmethod
    def validate(cls, data: dict):
        errors = []
        for field in cls.required:
            if not (data.get(field) or "").strip():
                errors.append(f"{field} is required")
        for field, max_len in cls.max_lengths.items():
            val = data.get(field)
            if val and len(str(val)) > max_len:
                errors.append(f"{field} must be at most {max_len} characters")
        username = (data.get("username") or "").strip()
        if username and len(username) < 3:
            errors.append("username must be at least 3 characters")
        if username and not _USERNAME_RE.fullmatch(username):
            errors.append("username can only contain letters, numbers, and underscores")
        password = data.get("password") or ""
        if password and len(password) < 8:
            errors.append("password must be at least 8 characters")
        return errors


class LoginSchema:
    required = ("login", "password")

    @classmethod
    def validate(cls, data: dict):
        errors = []
        for field in cls.required:
            if not (data.get(field) or ""):
                errors.append(f"{field} is required")
        return errors
