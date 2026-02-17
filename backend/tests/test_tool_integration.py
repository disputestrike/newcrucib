"""
Integration test for tool agent endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path is set
from unittest.mock import AsyncMock, patch


def test_tool_endpoints_defined():
    """Test that all tool endpoints are defined in server"""
    # Import server to check endpoints
    from server import app
    
    routes = [route.path for route in app.routes]
    
    # Check that all tool endpoints are defined
    assert "/api/tools/browser" in routes
    assert "/api/tools/file" in routes
    assert "/api/tools/api" in routes
    assert "/api/tools/database" in routes
    assert "/api/tools/deploy" in routes


def test_tool_agents_can_be_imported():
    """Test that tool agents can be imported"""
    from tools import (
        BrowserAgent, 
        FileAgent, 
        APIAgent, 
        DatabaseOperationsAgent, 
        DeploymentOperationsAgent
    )
    
    # Verify agents exist and can be instantiated
    assert BrowserAgent is not None
    assert FileAgent is not None
    assert APIAgent is not None
    assert DatabaseOperationsAgent is not None
    assert DeploymentOperationsAgent is not None


def test_base_agent_interface():
    """Test that BaseAgent provides correct interface"""
    from tools.base_agent import BaseAgent
    
    agent = BaseAgent(llm_client=None, config={})
    
    # Check that base agent has required methods
    assert hasattr(agent, 'execute')
    assert hasattr(agent, 'run')
    assert hasattr(agent, 'name')
    assert agent.name == "BaseAgent"


@pytest.mark.asyncio
async def test_file_agent_endpoint_logic():
    """Test FileAgent logic without HTTP"""
    from tools.file_agent import FileAgent
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = FileAgent(llm_client=None, config={"workspace": tmpdir})
        
        # Test write
        result = await agent.run({
            "action": "write",
            "path": "test.txt",
            "content": "Hello"
        })
        assert result["success"] is True
        
        # Test read
        result = await agent.run({
            "action": "read",
            "path": "test.txt"
        })
        assert result["success"] is True
        assert result["content"] == "Hello"


@pytest.mark.asyncio
async def test_api_agent_endpoint_logic():
    """Test APIAgent logic without HTTP"""
    from tools.api_agent import APIAgent
    
    agent = APIAgent(llm_client=None, config={})
    
    with patch('tools.api_agent.httpx.AsyncClient') as mock_client:
        from unittest.mock import MagicMock
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.headers = {}
        mock_response.url = "https://example.com"
        
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await agent.run({
            "method": "GET",
            "url": "https://example.com"
        })
        
        assert result["success"] is True
        assert result["status_code"] == 200
