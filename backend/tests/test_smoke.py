"""
Layer 9 – Post-deployment / smoke tests.
Verifies app is up and critical endpoints respond (in-process via app_client).
"""
import time
import pytest


async def test_smoke_health_returns_200(app_client):
    """App starts and /api/health returns 200."""
    r = await app_client.get("/api/health", timeout=10)
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


async def test_smoke_root_returns_200(app_client):
    """GET /api/ returns 200."""
    r = await app_client.get("/api/", timeout=10)
    assert r.status_code == 200


async def test_smoke_critical_endpoints_respond(app_client):
    """Critical read-only endpoints respond (no 500)."""
    endpoints = [
        ("/api/build/phases", "GET"),
        ("/api/tokens/bundles", "GET"),
        ("/api/agents", "GET"),
        ("/api/templates", "GET"),
        ("/api/patterns", "GET"),
        ("/api/examples", "GET"),  # Landing + ExamplesGallery
    ]
    for path, method in endpoints:
        if method == "GET":
            r = await app_client.get(path, timeout=10)
        else:
            r = await app_client.post(path, json={}, timeout=10)
        assert r.status_code != 500, f"{path} returned 500"


async def test_smoke_examples_returns_200(app_client):
    """GET /api/examples returns 200 and examples array (Landing + ExamplesGallery)."""
    r = await app_client.get("/api/examples", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "examples" in data
    assert isinstance(data["examples"], list)


async def test_smoke_health_with_retries(app_client):
    """Health responds (retries not needed in-process)."""
    r = await app_client.get("/api/health", timeout=5)
    assert r.status_code == 200


async def test_smoke_health_response_time(app_client):
    """Health endpoint responds within acceptable time (e.g. 2s for CI variability)."""
    start = time.perf_counter()
    r = await app_client.get("/api/health", timeout=10)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert r.status_code == 200
    assert elapsed_ms < 5000, f"/api/health took {elapsed_ms:.0f}ms (target < 5000ms)"
