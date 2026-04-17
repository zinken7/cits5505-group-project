# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///watchlist.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    VITE_DEV_MODE = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
