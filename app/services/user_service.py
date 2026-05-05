# -*- coding: utf-8 -*-
from app.extensions import db
from app.models.user import User


def get_user(user_id, *, include_deactivated=False):
    user = db.session.get(User, user_id)
    if user and user.deactivated and not include_deactivated:
        return None
    return user


def get_user_by_username(username, *, include_deactivated=False):
    query = User.query.filter_by(username=username)
    if not include_deactivated:
        query = query.filter_by(deactivated=False)
    return query.first()


def list_all_users(*, include_deactivated=True, include_root=True):
    query = User.query
    if not include_deactivated:
        query = query.filter_by(deactivated=False)
    if not include_root:
        query = query.filter_by(is_root=False)
    return query.order_by(User.id.asc()).all()


def set_admin_role(user, *, is_admin):
    if user.deactivated:
        raise ValueError("Deactivated accounts cannot be administrators.")
    if user.is_root and not is_admin:
        raise ValueError("The root account must remain an administrator.")
    user.is_admin = bool(is_admin)
    db.session.commit()
    return user


def delete_user(user):
    return deactivate_user(user)


def deactivate_user(user):
    if user.is_root:
        raise ValueError("The root account cannot be deactivated.")
    user.deactivated = True
    user.is_admin = False
    user.profile_public = False
    user.allow_friend_requests = False
    db.session.commit()
    return user


def reactivate_user(user):
    user.deactivated = False
    db.session.commit()
    return user


def update_user(user, **fields):
    """Apply only the keys present in fields to user, then commit."""
    for attr in ("display_name", "bio", "favorite_genres", "watchlist_visibility",
                 "username", "date_of_birth", "profile_public", "allow_friend_requests"):
        if attr in fields:
            setattr(user, attr, fields[attr])
    db.session.commit()
    return user
