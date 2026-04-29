# -*- coding: utf-8 -*-
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from app.models.friendship import Friendship
from app.services.media_service import get_media_by_imdb_id, list_media
from app.services.user_service import get_user_by_username
from app.services.watchlist_service import get_trending, get_user_watchlist

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Landing page — cinematic Three.js experience."""
    return render_template("index.html")


@bp.route("/categories")
@login_required
def categories():
    """Categories page — browse all 3 media types by genre."""
    GENRES = sorted([
        "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime",
        "Documentary", "Drama", "Family", "Fantasy", "History", "Horror",
        "Music", "Mystery", "Romance", "Sci-Fi", "Sport", "Thriller", "War", "Western",
    ])
    genre = request.args.get("genre", "Drama")
    if genre not in GENRES:
        genre = "Drama"

    movies,  movie_total  = list_media("movie",  genre=genre, sort="-rating", limit=16)
    anime,   anime_total  = list_media("anime",  genre=genre, sort="-rating", limit=16)
    tvshows, tvshow_total = list_media("tvshow", genre=genre, sort="-rating", limit=16)
    return render_template(
        "categories.html",
        genres=GENRES,
        selected_genre=genre,
        movies=movies,   movie_total=movie_total,
        anime=anime,     anime_total=anime_total,
        tvshows=tvshows, tvshow_total=tvshow_total,
    )


@bp.route("/explore")
def explore():
    """Explore page — sidebar layout for logged-in users, public layout otherwise."""
    if current_user.is_authenticated:
        return render_template("explore.html")
    return render_template("explore_public.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard — show personal watchlists by status."""
    watchlist = get_user_watchlist(current_user.id)
    return render_template("dashboard.html", watchlist=watchlist)


def _get_friendship(user_a_id, user_b_id):
    return Friendship.query.filter(
        or_(
            and_(Friendship.requester_id == user_a_id, Friendship.addressee_id == user_b_id),
            and_(Friendship.requester_id == user_b_id, Friendship.addressee_id == user_a_id),
        )
    ).first()


@bp.route("/profile/me")
@login_required
def profile_me():
    """Current user's own profile — URL stays /profile/me regardless of username."""
    watchlist = get_user_watchlist(current_user.id)
    return render_template(
        "profile.html",
        profile_user=current_user,
        watchlist=watchlist,
        friendship_status=None,
        friendship_id=None,
        is_friendship_requester=False,
    )


@bp.route("/profile/me/edit")
@login_required
def profile_edit():
    """Edit profile page."""
    return render_template("profile_edit.html")


@bp.route("/profile/<username>")
# @login_required
def profile(username):
    """Public profile — redirect own profile to /profile/me, apply privacy for others."""
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for("main.profile_me"))

    user = get_user_by_username(username)
    if not user:
        abort(404)

    friendship_status = None
    friendship_id = None
    is_friendship_requester = False

    if current_user.is_authenticated:
        f = _get_friendship(current_user.id, user.id)
        if f:
            friendship_status = f.status
            friendship_id = f.id
            is_friendship_requester = f.requester_id == current_user.id

    is_friend = friendship_status == "accepted"

    # Privacy: non-public profile is visible only to logged-in friends
    if not user.profile_public:
        if not current_user.is_authenticated or not is_friend:
            return render_template("profile_private.html", profile_user=user)

    watchlist = get_user_watchlist(user.id)
    return render_template(
        "profile.html",
        profile_user=user,
        watchlist=watchlist,
        friendship_status=friendship_status,
        friendship_id=friendship_id,
        is_friendship_requester=is_friendship_requester,
    )


@bp.route("/chat")
@login_required
def chat():
    """Real-time chat with friends."""
    return render_template("chat.html")


@bp.route("/search")
@login_required
def search():
    """Search results page."""
    q = request.args.get("q", "").strip()
    return render_template("search.html", q=q)


@bp.route("/items/<imdb_id>")
def item_detail(imdb_id):
    """Item detail page — JS hydrates from /api/v1/items/<imdb_id>."""
    if not get_media_by_imdb_id(imdb_id):
        abort(404)
    return render_template("detail.html", imdb_id=imdb_id)
