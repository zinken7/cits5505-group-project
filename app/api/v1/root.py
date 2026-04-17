# -*- coding: utf-8 -*-
from app.api.v1 import bp
from app.api.v1.common import api_response


@bp.route("", methods=["GET"])
@bp.route("/", methods=["GET"])
def api_v1_root():
    return api_response(
        data={"name": "Watchlist Hub API", "version": "1.0.0"},
        message="OK",
    )
