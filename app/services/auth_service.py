# -*- coding: utf-8 -*-
from sqlalchemy import or_

from app.extensions import db
from app.models.user import User


def register_user(username, email, password, display_name=None):
    """Register a new user.

    Returns (user, None) on success or (None, error_message) on failure.
    """
    if not username or not email or not password:
        return None, "All fields are required"

    if len(password) < 8:
        return None, "Password must be at least 8 characters"

    if User.query.filter_by(email=email).first():
        return None, "Email already registered"

    if User.query.filter_by(username=username).first():
        return None, "Username already taken"

    user = User(
        username=username,
        email=email,
        display_name=display_name or username,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None


def authenticate_user(login, password):
    """Authenticate by email or username and password.

    Returns the User object if valid, else None.
    """
    if not login or not password:
        return None
    user = User.query.filter(
        or_(User.email == login, User.username == login)
    ).first()
    if user and user.check_password(password):
        return user
    return None
