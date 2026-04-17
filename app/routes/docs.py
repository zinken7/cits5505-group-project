# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, redirect, render_template, url_for

from app.openapi import build_openapi_spec

bp = Blueprint("docs", __name__)


@bp.route("/docs")
def hub():
    """Documentation landing: UI Kit vs REST APIs."""
    return render_template("docs/hub.html")


@bp.route("/docs/ui")
def ui():
    """Interactive UI Kit (data-ui components)."""
    return render_template("ui_docs.html")


@bp.route("/docs/apis")
def apis():
    """Swagger UI for OpenAPI."""
    return render_template("docs/swagger.html")


@bp.route("/docs/apis/redoc")
def apis_redoc():
    """ReDoc view of the same OpenAPI document."""
    return render_template("docs/redoc.html")


@bp.route("/openapi.json")
def openapi_json():
    """Machine-readable OpenAPI document."""
    return jsonify(build_openapi_spec())


@bp.route("/redoc")
def redoc_legacy():
    """Backwards compatibility: old ReDoc URL."""
    return redirect(url_for("docs.apis_redoc"), code=301)
