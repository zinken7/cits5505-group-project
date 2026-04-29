# -*- coding: utf-8 -*-
from flask import request

from app.api.v1 import bp
from app.api.v1.common import api_response, parse_id, parse_pagination, validation_error
from app.services.media_service import get_media, list_media


@bp.route("/anime", methods=["GET"])
def list_anime():
    q = request.args.get("q")
    genre = request.args.get("genre")
    sort = request.args.get("sort") or "title"
    limit, offset = parse_pagination(limit_default=24, max_limit=100)
    items, total = list_media("anime", q=q, genre=genre, sort=sort, limit=limit, offset=offset)
    return api_response(data=items, meta={"limit": limit, "offset": offset, "total": total})


@bp.route("/anime/<anime_id>", methods=["GET"])
def get_anime(anime_id):
    mid = parse_id(anime_id)
    if mid is None:
        return validation_error("Invalid anime id")
    m = get_media(mid)
    if not m or m.media_type != "anime":
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())


@bp.route("/tvshows", methods=["GET"])
def list_tvshows():
    q = request.args.get("q")
    genre = request.args.get("genre")
    sort = request.args.get("sort") or "-releaseYear"
    limit, offset = parse_pagination(limit_default=24, max_limit=100)
    items, total = list_media("tvshow", q=q, genre=genre, sort=sort, limit=limit, offset=offset)
    return api_response(data=items, meta={"limit": limit, "offset": offset, "total": total})


@bp.route("/tvshows/<tvshow_id>", methods=["GET"])
def get_tvshow(tvshow_id):
    mid = parse_id(tvshow_id)
    if mid is None:
        return validation_error("Invalid TV show id")
    m = get_media(mid)
    if not m or m.media_type != "tvshow":
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())


@bp.route("/movies", methods=["GET"])
def list_movies():
    q = request.args.get("q")
    genre = request.args.get("genre")
    sort = request.args.get("sort") or "-releaseYear"
    limit, offset = parse_pagination(limit_default=24, max_limit=100)
    items, total = list_media("movie", q=q, genre=genre, sort=sort, limit=limit, offset=offset)
    return api_response(data=items, meta={"limit": limit, "offset": offset, "total": total})


@bp.route("/movies/<movie_id>", methods=["GET"])
def get_movie(movie_id):
    mid = parse_id(movie_id)
    if mid is None:
        return validation_error("Invalid movie id")
    m = get_media(mid)
    if not m or m.media_type != "movie":
        return api_response(data=None, message="Not found", success=False, status=404)
    return api_response(data=m.to_dict())
