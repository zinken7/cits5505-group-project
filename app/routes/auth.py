# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.services.auth_service import register_user, authenticate_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and form handler."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(email, password)
        if user:
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration page and form handler."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user, error = register_user(username, email, password)
        if error:
            flash(error, "error")
        else:
            login_user(user)
            flash("Account created successfully!", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html")


@bp.route("/logout")
@login_required
def logout():
    """Log the user out and redirect to landing page."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
