import os

import pytest
from fastapi.testclient import TestClient

from server import app


@pytest.fixture(autouse=True)
def setup_test_env(request):
    """Set up test environment variables"""
    # Skip setting env vars for tests that need missing env vars
    if "missing" in request.node.name:
        return

    # Set default test environment variables
    os.environ.setdefault("GOOGLE_API_KEY", "test_google_api_key")
    os.environ.setdefault("CSE_ID", "test_cse_id")
    os.environ.setdefault("NEWS_API_KEY", "test_news_api_key")
    os.environ.setdefault("GOOGLE_APP_DOMAIN", "test_domain")


@pytest.fixture
def client():
    """FastAPI test client fixture"""
    return TestClient(app)
