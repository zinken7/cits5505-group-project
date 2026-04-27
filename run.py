# -*- coding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    # Flask-SocketIO refuses Werkzeug when DEBUG is False (e.g. FLASK_ENV=production in .env
    # or run_pro.sh). This file is the local convenience server only — use gunicorn/uwsgi
    # (or another worker) for real production deployments.
    socketio.run(
        app,
        debug=app.config.get("DEBUG", False),
        host="0.0.0.0",
        port=5002,
        allow_unsafe_werkzeug=True,
    )
