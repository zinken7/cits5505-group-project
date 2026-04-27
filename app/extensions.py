# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
# Default would pick eventlet (see requirements.txt), which monkey-patches the stdlib
# and commonly breaks SQLite writes (OperationalError: attempt to write a readonly database).
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
