# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.forms.auth import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from app.models.user import User
from app.services.auth_service import register_user, authenticate_user
from app.services.password_reset_service import create_reset_token, verify_reset_token

bp = Blueprint("auth", __name__)

_GENERIC_FORGOT_FLASH = (
    "If an account exists for that email, you can use the reset link we sent. "
    "The link expires in 24 hours."
)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and form handler."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user = authenticate_user(email, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration page and form handler."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        user, error = register_user(username, email, form.password.data)
        if error:
            flash(error, "error")
        else:
            login_user(user)
            flash("Account created successfully!", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form=form)


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Request a password reset link (email delivery not configured — see flash in DEBUG)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user = User.query.filter_by(email=email).first()
        expose = current_app.debug or current_app.config.get(
            "PASSWORD_RESET_EXPOSE_LINK", False
        )
        if user:
            token = create_reset_token(user.id)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            if expose:
                flash(
                    "Open this one-time link to choose a new password (valid 24 hours). "
                    "Email is not configured — link shown here for development only.",
                    "info",
                )
                flash(reset_url, "success")
            else:
                flash(_GENERIC_FORGOT_FLASH, "info")
        else:
            flash(_GENERIC_FORGOT_FLASH, "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Set a new password using a signed token from the forgot-password flow."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    user_id = verify_reset_token(token)
    if user_id is None:
        flash("This reset link is invalid or has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = db.session.get(User, user_id)
    if user is None:
        flash("This reset link is invalid or has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated. You can log in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, token=token)


@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Confirm logout on GET, then log the user out on POST."""
    if request.method == "GET":
        return render_template("auth/logout.html")

    logout_user()
    return redirect(url_for("main.explore"))
