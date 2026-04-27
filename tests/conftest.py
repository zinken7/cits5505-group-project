# -*- coding: utf-8 -*-
import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    """Yield the db session; roll back after each test."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clear all tables between tests for isolation
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
