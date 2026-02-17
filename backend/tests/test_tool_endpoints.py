"""
Integration test for tool agent endpoints.
Tests the /api/tools/* endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_browser_endpoint(app_client):
    """Test /api/tools/browser endpoint"""
    # Test validation error
    response = await app_client.post("/api/tools/browser", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "action" in data["error"]
    
    # Test valid request (may fail if playwright not fully set up, but should not crash)
    response = await app_client.post("/api/tools/browser", json={
        "action": "navigate",
        "url": "https://example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_file_endpoint(app_client):
    """Test /api/tools/file endpoint"""
    # Test validation error
    response = await app_client.post("/api/tools/file", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    
    # Test write operation
    response = await app_client.post("/api/tools/file", json={
        "action": "write",
        "path": "test_integration.txt",
        "content": "Integration test"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Test read operation
    response = await app_client.post("/api/tools/file", json={
        "action": "read",
        "path": "test_integration.txt"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["content"] == "Integration test"


@pytest.mark.asyncio
async def test_api_endpoint(app_client):
    """Test /api/tools/api endpoint"""
    # Test validation error
    response = await app_client.post("/api/tools/api", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    
    # Test valid GET request
    response = await app_client.post("/api/tools/api", json={
        "url": "https://httpbin.org/get",
        "method": "GET"
    })
    assert response.status_code == 200
    data = response.json()
    # May succeed or fail depending on network, but should not crash
    assert "success" in data


@pytest.mark.asyncio
async def test_database_endpoint(app_client):
    """Test /api/tools/database endpoint"""
    # Test validation error
    response = await app_client.post("/api/tools/database", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_deployment_endpoint(app_client):
    """Test /api/tools/deploy endpoint"""
    # Test validation error
    response = await app_client.post("/api/tools/deploy", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "platform" in data["error"]
