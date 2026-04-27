# -*- coding: utf-8 -*-
from flask import request
from flask_login import current_user, login_user, logout_user

from app.api.v1 import bp
from app.api.v1.common import api_response, validate_body, validation_error
from app.api.v1.schemas.auth import LoginSchema, RegisterSchema
from app.extensions import limiter
from app.services.auth_service import authenticate_user, register_user


@bp.route("/auth/register", methods=["POST"])
@limiter.limit("3 per minute")
@validate_body(RegisterSchema)
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    display_name = (data.get("displayName") or "").strip() or None

    user, err = register_user(username, email, password, display_name=display_name)
    if err:
        return api_response(data=None, message=err, success=False, status=400)
    login_user(user)
    return api_response(data=user.to_dict(), message="Registered", status=201)


@bp.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
@validate_body(LoginSchema)
def api_login():
    data = request.get_json(silent=True) or {}
    login = (data.get("login") or "").strip()
    password = data.get("password") or ""

    user = authenticate_user(login, password)
    if not user:
        return api_response(
            data=None,
            message="Invalid credentials",
            success=False,
            status=401,
        )
    login_user(user)
    return api_response(data=user.to_dict(), message="Logged in")


@bp.route("/auth/logout", methods=["POST"])
def api_logout():
    logout_user()
    return api_response(message="Logged out")


@bp.route("/auth/session", methods=["GET"])
def api_session():
    if not current_user.is_authenticated:
        return api_response(data={"user": None}, message="Not authenticated")
    return api_response(data={"user": current_user.to_dict()})
