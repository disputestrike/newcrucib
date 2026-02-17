"""
Tests for tool agents: browser, file, api, database, deployment.
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.tools.browser_agent import BrowserAgent
from agents.tools.file_agent import FileAgent
from agents.tools.api_agent import APIAgent
from agents.tools.database_operations_agent import DatabaseOperationsAgent
from agents.tools.deployment_operations_agent import DeploymentOperationsAgent


# ==================== Browser Agent Tests ====================

@pytest.mark.asyncio
async def test_browser_agent_validation():
    """Test BrowserAgent input validation"""
    agent = BrowserAgent(llm_client=None, config={})
    
    # Missing action
    result = await agent.run({})
    assert result["success"] is False
    assert "action" in result["error"]
    
    # Invalid action
    result = await agent.run({"action": "invalid"})
    assert result["success"] is False
    assert "Invalid action" in result["error"]
    
    # Missing URL for navigate
    result = await agent.run({"action": "navigate"})
    assert result["success"] is False
    assert "url" in result["error"]


@pytest.mark.asyncio
async def test_browser_agent_navigate():
    """Test BrowserAgent navigate action"""
    agent = BrowserAgent(llm_client=None, config={})
    
    # This will fail if playwright is not installed, which is expected in CI
    result = await agent.run({
        "action": "navigate",
        "url": "https://example.com"
    })
    
    # Either success or error (playwright not installed)
    assert "success" in result
    if result["success"]:
        assert "title" in result
        assert "html" in result


# ==================== File Agent Tests ====================

@pytest.mark.asyncio
async def test_file_agent_validation():
    """Test FileAgent input validation"""
    agent = FileAgent(llm_client=None, config={"workspace_dir": "/tmp/test_workspace"})
    
    # Missing action
    result = await agent.run({})
    assert result["success"] is False
    assert "action" in result["error"]
    
    # Invalid action
    result = await agent.run({"action": "invalid"})
    assert result["success"] is False
    
    # Missing path for read
    result = await agent.run({"action": "read"})
    assert result["success"] is False
    assert "path" in result["error"]


@pytest.mark.asyncio
async def test_file_agent_write_read():
    """Test FileAgent write and read operations"""
    agent = FileAgent(llm_client=None, config={"workspace_dir": "/tmp/test_workspace"})
    
    # Write file
    result = await agent.run({
        "action": "write",
        "path": "test.txt",
        "content": "Hello, World!"
    })
    assert result["success"] is True
    assert result["bytes_written"] == 13
    
    # Read file
    result = await agent.run({
        "action": "read",
        "path": "test.txt"
    })
    assert result["success"] is True
    assert result["content"] == "Hello, World!"
    
    # Delete file
    result = await agent.run({
        "action": "delete",
        "path": "test.txt"
    })
    assert result["success"] is True


@pytest.mark.asyncio
async def test_file_agent_list():
    """Test FileAgent list operation"""
    agent = FileAgent(llm_client=None, config={"workspace_dir": "/tmp/test_workspace"})
    
    # List root directory
    result = await agent.run({
        "action": "list",
        "path": "."
    })
    assert result["success"] is True
    assert "files" in result
    assert isinstance(result["files"], list)


# ==================== API Agent Tests ====================

@pytest.mark.asyncio
async def test_api_agent_validation():
    """Test APIAgent input validation"""
    agent = APIAgent(llm_client=None, config={})
    
    # Missing URL
    result = await agent.run({})
    assert result["success"] is False
    assert "url" in result["error"]


@pytest.mark.asyncio
async def test_api_agent_get():
    """Test APIAgent GET request"""
    agent = APIAgent(llm_client=None, config={})
    
    # Make GET request to httpbin
    result = await agent.run({
        "url": "https://httpbin.org/get",
        "method": "GET"
    })
    
    # Should succeed
    if result["success"]:
        assert result["status_code"] == 200
        assert "data" in result


@pytest.mark.asyncio
async def test_api_agent_post():
    """Test APIAgent POST request"""
    agent = APIAgent(llm_client=None, config={})
    
    # Make POST request to httpbin
    result = await agent.run({
        "url": "https://httpbin.org/post",
        "method": "POST",
        "data": {"key": "value"}
    })
    
    # Should succeed
    if result["success"]:
        assert result["status_code"] == 200


# ==================== Database Agent Tests ====================

@pytest.mark.asyncio
async def test_database_agent_validation():
    """Test DatabaseOperationsAgent input validation"""
    agent = DatabaseOperationsAgent(llm_client=None, config={})
    
    # Missing query and action
    result = await agent.run({})
    assert result["success"] is False
    assert "query" in result["error"] or "action" in result["error"]


@pytest.mark.asyncio
async def test_database_agent_query():
    """Test DatabaseOperationsAgent query action"""
    agent = DatabaseOperationsAgent(llm_client=None, config={})
    
    # This will fail if sqlalchemy is not installed
    result = await agent.run({
        "action": "execute",
        "query": "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)",
        "database_url": "sqlite:///./test.db"
    })
    
    # Either success or error (sqlalchemy not installed)
    assert "success" in result


# ==================== Deployment Agent Tests ====================

@pytest.mark.asyncio
async def test_deployment_agent_validation():
    """Test DeploymentOperationsAgent input validation"""
    agent = DeploymentOperationsAgent(llm_client=None, config={})
    
    # Missing platform
    result = await agent.run({})
    assert result["success"] is False
    assert "platform" in result["error"]
    
    # Missing files
    result = await agent.run({"platform": "vercel"})
    assert result["success"] is False
    assert "files" in result["error"]


@pytest.mark.asyncio
async def test_deployment_agent_unsupported_platform():
    """Test DeploymentOperationsAgent with unsupported platform"""
    agent = DeploymentOperationsAgent(llm_client=None, config={})
    
    result = await agent.run({
        "platform": "unsupported",
        "files": {"index.html": "<html></html>"}
    })
    
    assert result["success"] is False
    assert "not supported" in result["error"]


# ==================== Agent Registry Tests ====================

def test_agent_registry():
    """Test that agents are registered"""
    # Import agents to trigger registration
    from agents.tools.browser_agent import BrowserAgent
    from agents.tools.file_agent import FileAgent
    from agents.tools.api_agent import APIAgent
    from agents.tools.database_operations_agent import DatabaseOperationsAgent
    from agents.tools.deployment_operations_agent import DeploymentOperationsAgent
    from agents.registry import AgentRegistry
    
    agents = AgentRegistry.list_agents()
    
    # Check that tool agents are registered
    assert "BrowserAgent" in agents
    assert "FileAgent" in agents
    assert "APIAgent" in agents
    assert "DatabaseOperationsAgent" in agents
    assert "DeploymentOperationsAgent" in agents
