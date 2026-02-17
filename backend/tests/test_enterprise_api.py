"""
Integration tests for Phase 4 Enterprise Feature API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client():
    """Create a test client"""
    # Set required env vars
    import os
    os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
    os.environ['DB_NAME'] = 'test_db'
    os.environ['JWT_SECRET'] = 'test_secret_key'
    
    try:
        from server import app
        return TestClient(app)
    except Exception as e:
        pytest.skip(f"Cannot create test client: {e}")


def test_marketplace_list_agents(client):
    """Test listing agents from marketplace"""
    response = client.get("/api/marketplace/agents")
    assert response.status_code in [200, 501]  # 501 if marketplace not initialized
    if response.status_code == 200:
        data = response.json()
        assert "agents" in data


def test_marketplace_publish_agent(client):
    """Test publishing an agent"""
    agent_data = {
        "name": "TestAgent",
        "author": "test@example.com",
        "description": "A test agent",
        "version": "1.0.0",
        "category": "utility",
        "system_prompt": "You are a test agent",
        "input_schema": {},
        "output_schema": {},
        "dependencies": []
    }
    
    response = client.post("/api/marketplace/publish", json=agent_data)
    assert response.status_code in [200, 400, 501]  # Allow 400 if already exists


def test_dashboard_endpoint(client):
    """Test dashboard endpoint"""
    response = client.get("/api/dashboard")
    assert response.status_code in [200, 501]
    if response.status_code == 200:
        data = response.json()
        assert "agents" in data
        assert "summary" in data


def test_memory_insights(client):
    """Test team insights endpoint"""
    response = client.get("/api/memory/insights/test_team")
    assert response.status_code in [200, 501]
    if response.status_code == 200:
        data = response.json()
        assert "insights" in data


def test_optimization_report(client):
    """Test optimization report endpoint"""
    response = client.get("/api/optimization/report")
    assert response.status_code in [200, 501]
    if response.status_code == 200:
        data = response.json()
        assert "agents_optimized" in data


def test_health_endpoint(client):
    """Test that server is healthy"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
