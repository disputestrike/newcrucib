"""
API Integration Tests for Phase 4 Enterprise Features
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_marketplace_create_agent(app_client):
    """Test creating a custom agent via API"""
    response = await app_client.post(
        "/api/marketplace/create-agent",
        json={
            "name": "Test API Agent",
            "description": "Test agent via API",
            "author": "test_user",
            "category": "frontend",
            "system_prompt": "You are a test agent",
            "input_schema": {"type": "object"},
            "output_schema": {"type": "object"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "agent_id" in data


@pytest.mark.asyncio
async def test_marketplace_search(app_client):
    """Test searching marketplace agents via API"""
    # First create an agent
    await app_client.post(
        "/api/marketplace/create-agent",
        json={
            "name": "Searchable Agent",
            "description": "Test searchable agent",
            "author": "test_user",
            "category": "backend",
            "system_prompt": "Test prompt",
            "input_schema": {},
            "output_schema": {}
        }
    )
    
    # Search for it
    response = await app_client.get(
        "/api/marketplace/search",
        params={"query": "Searchable"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) > 0


@pytest.mark.asyncio
async def test_marketplace_install_agent(app_client):
    """Test installing an agent via API"""
    # First create an agent
    create_response = await app_client.post(
        "/api/marketplace/create-agent",
        json={
            "name": "Installable API Agent",
            "description": "Test agent",
            "author": "test_user",
            "category": "frontend",
            "system_prompt": "Test",
            "input_schema": {},
            "output_schema": {}
        }
    )
    
    agent_id = create_response.json()["agent_id"]
    
    # Install it
    response = await app_client.post(
        f"/api/marketplace/install/{agent_id}",
        params={"user_id": "test_user"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_marketplace_rate_agent(app_client):
    """Test rating an agent via API"""
    # First create an agent
    create_response = await app_client.post(
        "/api/marketplace/create-agent",
        json={
            "name": "Rateable API Agent",
            "description": "Test agent",
            "author": "test_user",
            "category": "frontend",
            "system_prompt": "Test",
            "input_schema": {},
            "output_schema": {}
        }
    )
    
    agent_id = create_response.json()["agent_id"]
    
    # Rate it
    response = await app_client.post(
        f"/api/marketplace/rate/{agent_id}",
        params={"rating": 4.5, "user_id": "test_user"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "new_rating" in data


@pytest.mark.asyncio
async def test_team_insights(app_client):
    """Test getting team insights via API"""
    response = await app_client.get("/api/team/insights/team-test-1")
    
    assert response.status_code == 200
    data = response.json()
    # Should return "No build history yet" for new team
    assert "message" in data or "total_builds" in data


@pytest.mark.asyncio
async def test_team_suggest_stack(app_client):
    """Test suggesting tech stack via API"""
    response = await app_client.post(
        "/api/team/suggest-stack/team-test-1",
        params={"prompt": "Build a web application"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert data["suggestion"] == "default"  # No history yet


@pytest.mark.asyncio
async def test_team_recommendations(app_client):
    """Test getting team recommendations via API"""
    response = await app_client.get("/api/team/recommendations/team-test-1")
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


@pytest.mark.asyncio
async def test_agent_dashboard(app_client):
    """Test getting agent dashboard data via API"""
    response = await app_client.get("/api/dashboard/agents", params={"hours": 24})
    
    assert response.status_code == 200
    data = response.json()
    # Should have message "No recent data" or actual data
    assert "message" in data or "overall" in data


@pytest.mark.asyncio
async def test_improve_test_variant(app_client):
    """Test creating a prompt variant via API"""
    response = await app_client.post(
        "/api/improve/test-variant",
        params={
            "agent_name": "TestAgent",
            "variant_prompt": "Improved prompt for testing",
            "variant_name": "v1"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "variant_id" in data


@pytest.mark.asyncio
async def test_improve_report(app_client):
    """Test getting improvement report via API"""
    response = await app_client.get("/api/improve/report/TestAgent")
    
    assert response.status_code == 200
    data = response.json()
    # Should have message since no data yet
    assert "message" in data or "agent_name" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
