import os

import pytest

from flight_search import create_app

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")


@pytest.fixture
def app():
    application = create_app(testing=True)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()
