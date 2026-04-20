# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.services.media_service import list_media
from app.services.watchlist_service import get_user_watchlist, get_trending

bp = Blueprint("main", __name__)


@bp.route("/ui-docs")
def ui_docs_legacy():
    """Old URL — use /docs/ui."""
    return redirect(url_for("docs.ui"), code=301)


@bp.route("/")
def index():
    """Landing page — cinematic Three.js experience."""
    return render_template("index.html")


@bp.route("/movies/categories")
def movie_categories():
    """Movie categories by genre."""
    genre = request.args.get("genre", "Action")
    genres = [
        "Action",
        "Adventure",
        "Animation",
        "Comedy",
        "Crime",
        "Drama",
        "Fantasy",
        "Horror",
        "Romance",
        "Sci-Fi",
        "Thriller",
    ]
    if genre not in genres:
        genre = genres[0]

    movies, total = list_media("movie", genre=genre, sort="-releaseYear", limit=48, offset=0)
    return render_template(
        "categories.html",
        genres=genres,
        selected_genre=genre,
        movies=movies,
        total=total,
    )


@bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard — show personal watchlists by status."""
    watchlist = get_user_watchlist(current_user.id)
    return render_template("dashboard.html", watchlist=watchlist)


@bp.route("/profile/<username>")
def profile(username):
    """Public profile — view another user's watchlists."""
    from app.models.user import User

    user = User.query.filter_by(username=username).first_or_404()
    watchlist = get_user_watchlist(user.id)
    return render_template("profile.html", profile_user=user, watchlist=watchlist)
