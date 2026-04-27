# -*- coding: utf-8 -*-
from flask import Blueprint

bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Import route modules for side-effect registration on bp
from app.api.v1 import root  # noqa: E402, F401
from app.api.v1 import auth  # noqa: E402, F401
from app.api.v1 import users  # noqa: E402, F401
from app.api.v1 import catalog  # noqa: E402, F401
from app.api.v1 import watchlist  # noqa: E402, F401
from app.api.v1 import trending  # noqa: E402, F401
from app.api.v1 import search  # noqa: E402, F401
from app.api.v1 import admin  # noqa: E402, F401
from app.api.v1 import landing  # noqa: E402, F401
from app.api.v1 import items  # noqa: E402, F401
from app.api.v1 import friends  # noqa: E402, F401
from app.api.v1 import messages  # noqa: E402, F401
