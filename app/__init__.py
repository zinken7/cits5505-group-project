# -*- coding: utf-8 -*-
import json
import os

from flask import Flask, redirect, request, url_for

from config import config


def create_app(config_name=None):
    """Application factory."""

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config[config_name])

    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    from app.extensions import db, login_manager

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.unauthorized_handler
    def _unauthorized_api():
        if request.path.startswith("/api"):
            from app.api.v1.common import api_response

            return api_response(
                data=None,
                message="Authentication required",
                success=False,
                status=401,
            )
        return redirect(url_for("auth.login", next=request.url))

    # ------------------------------------------------------------------
    # Vite asset helper (manifest-based in prod, dev server in dev)
    # ------------------------------------------------------------------
    _manifest_cache = {}

    def _load_manifest():
        """Load and cache the Vite manifest.json for production builds."""
        if _manifest_cache:
            return _manifest_cache

        manifest_path = app.config.get("VITE_MANIFEST_PATH", "")
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                _manifest_cache.update(json.load(f))
        return _manifest_cache

    @app.context_processor
    def inject_vite_helpers():
        """Make vite_asset() and vite_dev_mode available in all templates."""

        vite_dev_mode = app.config.get("VITE_DEV_MODE", False)
        vite_dev_url = app.config.get("VITE_DEV_SERVER_URL", "http://localhost:5173")

        def vite_asset(entry_path):
            """Resolve a Vite source path to the correct URL.

            In dev mode  → http://localhost:5173/<entry_path>
            In prod mode → /static/dist/<hashed filename from manifest>
            """
            if vite_dev_mode:
                return f"{vite_dev_url}/{entry_path}"

            manifest = _load_manifest()
            entry = manifest.get(entry_path, {})
            file_path = entry.get("file", entry_path)
            return f"/static/dist/{file_path}"

        def vite_asset_css(entry_path):
            """Return list of CSS file URLs associated with an entry in prod."""
            if vite_dev_mode:
                return []

            manifest = _load_manifest()
            entry = manifest.get(entry_path, {})
            css_files = entry.get("css", [])
            return [f"/static/dist/{css}" for css in css_files]

        return {
            "vite_dev_mode": vite_dev_mode,
            "vite_dev_url": vite_dev_url,
            "vite_asset": vite_asset,
            "vite_asset_css": vite_asset_css,
        }

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.docs import bp as docs_bp
    from app.api.v1 import bp as api_v1_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(api_v1_bp)

    # ------------------------------------------------------------------
    # Create DB tables (dev convenience)
    # ------------------------------------------------------------------
    with app.app_context():
        from app.models import user, media, watchlist, items  # noqa: F401

        # Ensure Flask's instance folder exists for SQLite
        os.makedirs(app.instance_path, exist_ok=True)

        db.create_all()

    return app
