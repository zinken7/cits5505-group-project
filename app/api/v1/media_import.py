# -*- coding: utf-8 -*-
"""POST /api/v1/media/import — any authenticated user can add a title via IMDb URL."""
from flask import request
from sqlalchemy.exc import IntegrityError

from app.api.v1 import bp
from app.api.v1.common import api_login_required, api_response, validation_error
from app.extensions import db
from app.services.imdb_service import lookup_imdb, parse_imdb_id
from app.services.media_service import create_media, get_media_by_imdb_id


@bp.route("/media/import", methods=["POST"])
@api_login_required
def media_import():
    """Add a catalogue item from an IMDb URL. Available to any authenticated user."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not url:
        return validation_error("url is required")

    # Return the existing entry if the title is already catalogued
    imdb_id = parse_imdb_id(url)
    if imdb_id:
        existing = get_media_by_imdb_id(imdb_id)
        if existing:
            return api_response(
                data={"item": existing.to_dict(), "already_existed": True},
                message=f"“{existing.title}” is already in the catalogue.",
            )

    fields, err = lookup_imdb(url)
    if err:
        return api_response(data=None, message=err, success=False, status=422)

    try:
        m = create_media(
            title=fields["title"],
            media_type=fields["media_type"],
            description=fields.get("description") or "",
            image_url=fields.get("image_url") or "",
            year=fields.get("year"),
            imdb_id=fields.get("imdb_id"),
            imdb_url=fields.get("imdb_url") or "",
            rating=fields.get("rating"),
            votes=fields.get("votes"),
            genres=fields.get("genres"),
            country=fields.get("country"),
            language=fields.get("language"),
            director=fields.get("director"),
            cast=fields.get("cast"),
            runtime_minutes=fields.get("runtime_minutes"),
            episodes=fields.get("episodes"),
            release_status=fields.get("release_status"),
            tagline=fields.get("tagline"),
            awards=fields.get("awards"),
            trailer_url=fields.get("trailer_url"),
        )
    except ValueError as e:
        return api_response(data=None, message=str(e), success=False, status=422)
    except IntegrityError:
        db.session.rollback()
        return api_response(
            data=None,
            message="This title is already in the catalogue.",
            success=False,
            status=409,
        )

    return api_response(
        data={"item": m.to_dict(), "already_existed": False},
        message=f"Added “{m.title}” to the catalogue.",
        status=201,
    )
