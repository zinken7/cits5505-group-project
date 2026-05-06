# -*- coding: utf-8 -*-
import os
import warnings
from datetime import timedelta

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# Must run before class bodies read os.environ (so `flask db upgrade` and CLI match `run.py`).
load_dotenv(os.path.join(basedir, ".env"), override=False)

_DEV_SECRET = "dev-secret-key-change-me"
_DEFAULT_ROOT_PW = "root-root-change-me"


class Config:
    """Base configuration."""

    # When True, forgot-password shows the reset URL in flash (for dev/demo). Turn off when email is wired.
    PASSWORD_RESET_EXPOSE_LINK = False

    SECRET_KEY = os.environ.get("SECRET_KEY", _DEV_SECRET)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///watchlist.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API pagination defaults
    API_PAGE_DEFAULT = 20
    API_PAGE_MAX = 100

    # Flask-Login — "remember me" cookie duration
    REMEMBER_COOKIE_DURATION = timedelta(days=60)

    # Vite integration
    VITE_DEV_MODE = False
    VITE_DEV_SERVER_URL = "http://localhost:5173"
    VITE_MANIFEST_PATH = os.path.join(
        basedir, "app", "static", "dist", ".vite", "manifest.json"
    )

    # Bootstrap root account (see ``app.services.root_bootstrap``). Set all in production.
    ROOT_USERNAME = os.environ.get("ROOT_USERNAME", "root")
    ROOT_EMAIL = os.environ.get("ROOT_EMAIL", "root@localhost.com")
    ROOT_PASSWORD = os.environ.get("ROOT_PASSWORD", _DEFAULT_ROOT_PW)


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    VITE_DEV_MODE = False
    PASSWORD_RESET_EXPOSE_LINK = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    VITE_DEV_MODE = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    @classmethod
    def init_app(cls, app):
        if app.config.get("SECRET_KEY") == _DEV_SECRET:
            warnings.warn(
                "SECRET_KEY is set to the development default. Set a strong SECRET_KEY in production.",
                stacklevel=2,
            )
        if app.config.get("ROOT_PASSWORD") == _DEFAULT_ROOT_PW:
            warnings.warn(
                "ROOT_PASSWORD is still the default. Set ROOT_USERNAME, ROOT_EMAIL, and ROOT_PASSWORD in the environment.",
                stacklevel=2,
            )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
