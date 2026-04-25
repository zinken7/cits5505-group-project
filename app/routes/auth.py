# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired

from app.services.auth_service import register_user, authenticate_user

bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    """WTForms login form used by auth/login.html."""

    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and form handler."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(form.email.data.strip(), form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template(
        "auth/login.html",
        form=form,
        url_map={rule.endpoint.rsplit(".", 1)[-1] for rule in current_app.url_map.iter_rules()},
    )


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
