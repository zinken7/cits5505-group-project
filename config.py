# -*- coding: utf-8 -*-
import os
import warnings

basedir = os.path.abspath(os.path.dirname(__file__))

_DEV_SECRET = "dev-secret-key-change-me"


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

    # Vite integration
    VITE_DEV_MODE = False
    VITE_DEV_SERVER_URL = "http://localhost:5173"
    VITE_MANIFEST_PATH = os.path.join(
        basedir, "app", "static", "dist", ".vite", "manifest.json"
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    VITE_DEV_MODE = True
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
