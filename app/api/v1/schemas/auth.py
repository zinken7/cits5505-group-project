# -*- coding: utf-8 -*-


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
