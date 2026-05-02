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
    cfg = config[config_name]
    app.config.from_object(cfg)
    if hasattr(cfg, "init_app"):
        cfg.init_app(app)

    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    from app.extensions import db, login_manager, csrf, migrate, limiter, socketio

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)
    socketio.init_app(app, manage_session=False)

    @app.after_request
    def _no_cache_html(response):
        if response.content_type and response.content_type.startswith("text/html"):
            response.headers["Cache-Control"] = "no-store"
        return response

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

        def vite_page_entry(entry_path):
            """Return full HTML markup for a page-specific Vite entry.

            In dev  → <link> for CSS + <script> for JS from dev server
            In prod → <link>(s) from manifest CSS + <script> for hashed JS
            """
            from markupsafe import Markup

            parts = []
            if vite_dev_mode:
                # Dev: load the entry's CSS and JS from the Vite dev server
                # The CSS is inlined by Vite HMR via the JS module, but we
                # also add a <link> for the source CSS for instant first-paint.
                parts.append(
                    f'<script type="module" src="{vite_dev_url}/{entry_path}"></script>'
                )
            else:
                for css_url in vite_asset_css(entry_path):
                    parts.append(f'<link rel="stylesheet" href="{css_url}">')
                js_url = vite_asset(entry_path)
                parts.append(
                    f'<script type="module" src="{js_url}"></script>'
                )
            return Markup("\n    ".join(parts))

        return {
            "vite_dev_mode": vite_dev_mode,
            "vite_dev_url": vite_dev_url,
            "vite_asset": vite_asset,
            "vite_asset_css": vite_asset_css,
            "vite_page_entry": vite_page_entry,
        }

    # ------------------------------------------------------------------
    # Ticker context processor — feeds live stats to app_layout.html
    # ------------------------------------------------------------------
    @app.context_processor
    def inject_ticker():
        """Build ticker items from live DB data; used by app_layout.html."""
        try:
            from app.models.media import Media
            from app.models.watchlist import WatchlistItem
            from app.services.watchlist_service import get_trending
            from sqlalchemy import func

            total_media = Media.query.count()
            total_watchlists = WatchlistItem.query.count()
            trending = get_trending(limit=4)

            items = []
            if total_media:
                items.append(f"Tracking {total_media:,} titles in the catalogue")
            if total_watchlists:
                items.append(f"{total_watchlists:,} watchlist entries across all users")
            for t in trending:
                wc = t.get("watchlist_count", 0)
                rating = t.get("rating")
                rating_str = f" · ★{rating:.1f}" if rating else ""
                if wc:
                    items.append(f"Trending — {t['title']}{rating_str} · {wc} tracking")
                else:
                    items.append(f"Popular — {t['title']}{rating_str}")
            items += [
                "Rate everything after you finish",
                "New titles added weekly — check Explore",
                "Track movies, anime, and games in one place",
            ]
        except Exception:
            items = [
                "WatchList Hub — Track everything you love",
                "Movies · Anime · Games",
                "Rate everything after you finish",
            ]
        return dict(ticker_items=items)

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
    # Import models so Alembic can detect them; schema is managed via
    # `flask db upgrade` (Flask-Migrate / Alembic).
    # ------------------------------------------------------------------
    with app.app_context():
        from app.models import user, media, watchlist, friendship, message  # noqa: F401

        os.makedirs(app.instance_path, exist_ok=True)

    from app.sockets import chat  # noqa: F401 — registers socket event handlers

    return app
