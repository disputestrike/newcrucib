"""
Pytest fixtures and config for CrucibAI backend tests.
Sets MONGO_URL/DB_NAME so the real app can be imported for TestClient-based tests.
"""
import asyncio
import os
import pytest

# Must set before server is ever imported (server uses os.environ["MONGO_URL"])
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "crucibai")

# Enable async tests (test_orchestration_e2e)
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    """Single session-scoped event loop so Motor and app share one loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Base URL for tests that still use requests (e.g. test_smoke when hitting live server)
BASE_URL = os.environ.get("CRUCIBAI_API_URL", os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8000"))


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def api_url(base_url):
    return f"{base_url}/api"


@pytest.fixture
async def app_client():
    """Real FastAPI app via AsyncClient (same event loop as tests via session-scoped event_loop)."""
    from httpx import ASGITransport, AsyncClient
    from server import app
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
        timeout=60.0,
    ) as client:
        yield client
