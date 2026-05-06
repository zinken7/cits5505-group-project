# -*- coding: utf-8 -*-
"""View decorators for server-rendered (HTML) routes.

For JSON API endpoints under ``/api/v1``, use:

- ``admin_required`` or ``root_required`` from ``app.api.v1.common`` — JSON 401/403 envelopes.
"""
from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user


def admin_required(view_func):
    """Require an authenticated user with ``User.is_admin`` set.

    - Not logged in → redirect to login, preserving ``next`` (same idea as
      ``@login_required``).
    - Logged in but not admin → flash error and redirect to Explore.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.url))
        if not getattr(current_user, "is_admin", False):
            flash("Administrator privileges are required to access this page.", "error")
            return redirect(url_for("main.explore"))
        return view_func(*args, **kwargs)

    return wrapped


def root_required(view_func):
    """Require the bootstrap root account (``User.is_root``)."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.url))
        if not getattr(current_user, "is_root", False):
            flash("Only the root account can access this page.", "error")
            return redirect(url_for("main.explore"))
        return view_func(*args, **kwargs)

    return wrapped
