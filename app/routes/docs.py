# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, jsonify, redirect, render_template, url_for

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


_ROUTE_DESCRIPTIONS = {
    # Pages
    "main.index":           "Landing page — Three.js canvas + hero; entry to Explore / auth.",
    "main.categories":    "Browse movies, anime, and TV by genre (login required).",
    "main.dashboard":       "Signed-in dashboard — watchlists grouped by Watching / Planned / Completed.",
    "main.profile_me":      "Your own profile at /profile/me (watchlist + actions).",
    "main.profile_edit":    "Edit display name, bio, genres, privacy, friend-request settings.",
    "main.profile":         "Public profile by username; private profiles show a friends-only gate.",
    "main.explore":         "Explore — app shell when logged in, lightweight public view when not.",
    "main.search":          "Search results page (query string q; login required).",
    "main.chat":            "Real-time DM UI with friends (Flask-SocketIO + REST messages API).",
    "main.item_detail":     "Title detail page — hydrates from GET /api/v1/items/<imdb_id>.",
    "main.ui_docs_legacy":  "Legacy redirect → /docs/ui.",
    # Auth
    "auth.login":           "Login form (GET) and session handler (POST).",
    "auth.register":        "Registration (GET/POST).",
    "auth.forgot_password": "Request password reset (signed token; link in flash when dev exposes it).",
    "auth.reset_password":  "POST new password with token from forgot-password flow.",
    "auth.logout":          "Clears session; redirects to landing.",
    # Docs
    "docs.hub":             "Documentation home — UI Kit vs REST vs site routes.",
    "docs.ui":              "Interactive UI Kit (data-ui components).",
    "docs.apis":            "Swagger UI — OpenAPI matches live /api/v1 Flask routes.",
    "docs.apis_redoc":      "ReDoc — same spec as Swagger, narrative layout.",
    "docs.routes":          "All registered HTML blueprint routes (excludes /api/v1 and static).",
    "docs.openapi_json":    "OpenAPI 3.1 JSON — source for Swagger and ReDoc.",
    "docs.future":          "Roadmap / design notes (e.g. chat tagging); friends & DMs are implemented.",
    "docs.redoc_legacy":    "301 → /docs/apis/redoc.",
    # Admin / management pages
    "management.add_media":      "Admin form for creating catalogue items.",
    "management.manage_media":   "Admin catalogue table for editing/deleting media.",
    "management.edit_media":     "Admin form for editing a catalogue item.",
    "management.remove_media":   "POST endpoint for deleting a catalogue item.",
    "management.manage_users": "Admin user management; deactivate accounts without deleting data.",
    "management.manage_admins": "Root-only administrator role management.",
}

_BLUEPRINT_LABELS = {
    "main": "Pages",
    "auth": "Authentication",
    "admin": "Admin",
    "management": "Management",
    "docs": "Documentation",
}


@bp.route("/docs/routes")
def routes():
    """All registered URL rules rendered as an HTML page."""
    import re
    skip_blueprints = {"static", "api_v1"}
    order = ["main", "auth", "admin", "management", "docs"]
    groups = {}
    for rule in sorted(current_app.url_map.iter_rules(), key=lambda r: r.rule):
        endpoint = rule.endpoint
        blueprint = endpoint.split(".")[0] if "." in endpoint else "_app"
        if blueprint in skip_blueprints:
            continue
        methods = sorted(m for m in rule.methods if m not in ("HEAD", "OPTIONS"))
        parts = re.split(r"(<[^>]+>)", rule.rule)
        groups.setdefault(blueprint, []).append({
            "url": rule.rule,
            "url_parts": parts,
            "methods": methods,
            "endpoint": endpoint,
            "description": _ROUTE_DESCRIPTIONS.get(endpoint, ""),
        })
    ordered = {k: groups[k] for k in order if k in groups}
    ordered.update({k: v for k, v in sorted(groups.items()) if k not in ordered})
    return render_template("docs/routes.html", route_groups=ordered, blueprint_labels=_BLUEPRINT_LABELS)


@bp.route("/docs/future")
def future():
    """Roadmap and design notes (e.g. chat tagging); friends + messaging already ship."""
    return render_template("docs/future.html")


@bp.route("/redoc")
def redoc_legacy():
    """Backwards compatibility: old ReDoc URL."""
    return redirect(url_for("docs.apis_redoc"), code=301)
