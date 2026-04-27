# -*- coding: utf-8 -*-
from app.extensions import db
from app.models.user import User


def get_user(user_id):
    return db.session.get(User, user_id)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def list_all_users():
    return User.query.order_by(User.id.asc()).all()


def set_admin_role(user, *, is_admin):
    user.is_admin = is_admin
    db.session.commit()
    return user


def delete_user(user):
    db.session.delete(user)
    db.session.commit()


def update_user(user, **fields):
    """Apply only the keys present in fields to user, then commit."""
    for attr in ("display_name", "bio", "favorite_genres", "watchlist_visibility",
                 "username", "date_of_birth", "profile_public", "allow_friend_requests"):
        if attr in fields:
            setattr(user, attr, fields[attr])
    db.session.commit()
    return user
