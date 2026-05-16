# -*- coding: utf-8 -*-
from app.validation import USERNAME_MAX_LENGTH, validate_username


class RegisterSchema:
    required = ("username", "email", "password")
    max_lengths = {"username": USERNAME_MAX_LENGTH, "email": 120, "password": 128, "displayName": 80}

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
        if username:
            username_error = validate_username(username)
            if username_error:
                errors.append(username_error)
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
