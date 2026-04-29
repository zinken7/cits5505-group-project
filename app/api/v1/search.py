# -*- coding: utf-8 -*-
from flask import request

from app.api.v1 import bp
from app.api.v1.common import api_response, parse_pagination, validation_error
from app.models.media import Media


@bp.route("/search", methods=["GET"])
def search_media():
    q = (request.args.get("q") or "").strip()
    if not q:
        return validation_error("q is required", loc=("query", "q"))
    mtype = request.args.get("type")
    limit, offset = parse_pagination(limit_default=12, max_limit=100)

    query = Media.query.filter(Media.title.ilike(f"%{q}%"))
    if mtype in ("anime", "movie", "tvshow"):
        query = query.filter_by(media_type=mtype)

    total = query.count()
    rows = query.order_by(Media.title.asc()).offset(offset).limit(limit).all()
    return api_response(
        data=[m.to_dict() for m in rows],
        meta={"limit": limit, "offset": offset, "total": total},
    )
