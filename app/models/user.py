# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    favorite_genres = db.Column(db.JSON, nullable=True)
    watchlist_visibility = db.Column(db.String(20), nullable=False, default="public")
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship
    watchlist_items = db.relationship(
        "WatchlistItem", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "displayName": self.display_name or self.username,
            "bio": self.bio,
            "favoriteGenres": self.favorite_genres or [],
            "visibility": {"watchlist": self.watchlist_visibility},
            "isAdmin": self.is_admin,
        }

    def to_public_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name or self.username,
            "bio": self.bio,
        }

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
