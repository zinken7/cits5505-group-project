# -*- coding: utf-8 -*-
"""Ensure a bootstrap *root* account exists (``User.is_root``)."""
from flask import current_app

from app.extensions import db
from app.models.user import User


def ensure_root_user():
    """Create the root user if no row has ``is_root``.

    Called on app startup. Skips when ``TESTING`` is true or ``ROOT_PASSWORD`` is empty.
    """
    if current_app.config.get("TESTING"):
        return

    # Allow `flask db upgrade` (and first boot before migrate): ORM expects ``is_root``.
    try:
        from sqlalchemy import inspect

        insp = inspect(db.engine)
        if not insp.has_table("users"):
            current_app.logger.warning(
                "Database has no users table yet; run `flask db upgrade` then restart."
            )
            return
        columns = {c["name"] for c in insp.get_columns("users")}
        if "is_root" not in columns:
            current_app.logger.warning(
                "Column users.is_root missing — run `flask db upgrade` then restart. "
                "Root bootstrap will run on the next app start."
            )
            return
        if "deactivated" not in columns:
            current_app.logger.warning(
                "Column users.deactivated missing — run `flask db upgrade` then restart. "
                "Root bootstrap will run on the next app start."
            )
            return
    except Exception as exc:
        current_app.logger.warning("Could not inspect database; skipping root bootstrap (%s).", exc)
        return

    if User.query.filter_by(is_root=True).first():
        return

    password = (current_app.config.get("ROOT_PASSWORD") or "").strip()
    if not password:
        current_app.logger.warning(
            "No root user exists and ROOT_PASSWORD is not set; skipping root bootstrap."
        )
        return

    username = (current_app.config.get("ROOT_USERNAME") or "root").strip()
    email = (current_app.config.get("ROOT_EMAIL") or "root@localhost").strip()

    if User.query.filter((User.username == username) | (User.email == email)).first():
        current_app.logger.error(
            "Root bootstrap skipped: ROOT_USERNAME or ROOT_EMAIL already taken. "
            "Set is_root on an account via SQL or free those credentials."
        )
        return

    if len(password) < 8:
        current_app.logger.error(
            "Root bootstrap skipped: ROOT_PASSWORD must be at least 8 characters."
        )
        return

    user = User(
        username=username,
        email=email,
        display_name="Root",
        is_root=True,
        is_admin=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    current_app.logger.info("Bootstrap root user %r created.", username)
