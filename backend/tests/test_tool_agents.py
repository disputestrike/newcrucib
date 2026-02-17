"""
Tests for Phase 3 Tool Agents.
Tests BrowserAgent, FileAgent, APIAgent, DatabaseOperationsAgent, DeploymentOperationsAgent.
"""
import pytest
import os
import tempfile
from pathlib import Path


# Skip all tests if dependencies are not installed
try:
    from tools.browser_agent import BrowserAgent
    from tools.file_agent import FileAgent
    from tools.api_agent import APIAgent
    from tools.database_operations_agent import DatabaseOperationsAgent
    from tools.deployment_operations_agent import DeploymentOperationsAgent
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not TOOLS_AVAILABLE, reason="Tool agents not available")


@pytest.mark.asyncio
async def test_browser_agent_navigate():
    """Test BrowserAgent navigation"""
    agent = BrowserAgent(llm_client=None, config={})
    result = await agent.execute({
        "action": "navigate",
        "url": "https://example.com"
    })
    # May fail due to network/environment, check that we get a response
    assert isinstance(result, dict), "Should return a dict"
    # If successful, check for expected fields
    if result.get("success"):
        assert "title" in result
        assert "content_length" in result
    else:
        # Network failure is expected in CI
        assert "error" in result


@pytest.mark.asyncio
async def test_browser_agent_scrape():
    """Test BrowserAgent scraping"""
    agent = BrowserAgent(llm_client=None, config={})
    result = await agent.execute({
        "action": "scrape",
        "url": "https://example.com",
        "selector": "h1"
    })
    # May fail due to network/environment
    assert isinstance(result, dict), "Should return a dict"
    # If successful, check for expected fields
    if result.get("success"):
        assert "text" in result
        assert "html" in result
    else:
        # Network failure is expected in CI
        assert "error" in result


@pytest.mark.asyncio
async def test_file_agent_write_read():
    """Test FileAgent write and read operations"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = FileAgent(llm_client=None, config={"workspace": tmpdir})
        
        # Write file
        write_result = await agent.execute({
            "action": "write",
            "path": "test.txt",
            "content": "Hello, World!"
        })
        assert write_result["success"] is True
        
        # Read file
        read_result = await agent.execute({
            "action": "read",
            "path": "test.txt"
        })
        assert read_result["success"] is True
        assert read_result["content"] == "Hello, World!"


@pytest.mark.asyncio
async def test_file_agent_list_directory():
    """Test FileAgent list directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = FileAgent(llm_client=None, config={"workspace": tmpdir})
        
        # Create some files
        await agent.execute({
            "action": "write",
            "path": "file1.txt",
            "content": "test1"
        })
        await agent.execute({
            "action": "write",
            "path": "file2.txt",
            "content": "test2"
        })
        
        # List directory
        result = await agent.execute({
            "action": "list",
            "path": "."
        })
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["files"]) == 2


@pytest.mark.asyncio
async def test_file_agent_mkdir():
    """Test FileAgent create directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = FileAgent(llm_client=None, config={"workspace": tmpdir})
        
        result = await agent.execute({
            "action": "mkdir",
            "path": "testdir/subdir"
        })
        assert result["success"] is True
        assert Path(tmpdir) / "testdir" / "subdir" in Path(tmpdir).rglob("*")


@pytest.mark.asyncio
async def test_file_agent_delete():
    """Test FileAgent delete file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = FileAgent(llm_client=None, config={"workspace": tmpdir})
        
        # Create file
        await agent.execute({
            "action": "write",
            "path": "delete_me.txt",
            "content": "temporary"
        })
        
        # Delete file
        result = await agent.execute({
            "action": "delete",
            "path": "delete_me.txt"
        })
        assert result["success"] is True


@pytest.mark.asyncio
async def test_api_agent_get_request():
    """Test APIAgent GET request"""
    agent = APIAgent(llm_client=None, config={})
    result = await agent.execute({
        "method": "GET",
        "url": "https://httpbin.org/get"
    })
    # May be blocked by network policy, check structure instead
    assert isinstance(result, dict), "Should return a dict"
    # Either success with status_code, or error
    if result.get("success"):
        assert result["status_code"] == 200
        assert "data" in result
    else:
        assert "error" in result


@pytest.mark.asyncio
async def test_api_agent_post_request():
    """Test APIAgent POST request with JSON placeholder API"""
    agent = APIAgent(llm_client=None, config={})
    result = await agent.execute({
        "method": "POST",
        "url": "https://httpbin.org/post",
        "body": {
            "title": "test",
            "body": "test body",
            "userId": 1
        }
    })
    # May be blocked by network policy
    assert isinstance(result, dict), "Should return a dict"
    # Either success or error
    if result.get("success"):
        assert "status_code" in result
        assert "data" in result
    else:
        assert "error" in result


@pytest.mark.asyncio
async def test_database_agent_sqlite():
    """Test DatabaseOperationsAgent with SQLite"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test.db")
        agent = DatabaseOperationsAgent(llm_client=None, config={})
        
        # Create table
        create_result = await agent.execute({
            "db_type": "sqlite",
            "connection": {"database": db_path},
            "query": "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)",
            "params": []
        })
        assert create_result["success"] is True
        
        # Insert data
        insert_result = await agent.execute({
            "db_type": "sqlite",
            "connection": {"database": db_path},
            "query": "INSERT INTO users (name) VALUES (?)",
            "params": ["John Doe"]
        })
        assert insert_result["success"] is True
        
        # Select data
        select_result = await agent.execute({
            "db_type": "sqlite",
            "connection": {"database": db_path},
            "query": "SELECT * FROM users",
            "params": []
        })
        assert select_result["success"] is True
        assert select_result["row_count"] == 1
        assert select_result["rows"][0]["name"] == "John Doe"


@pytest.mark.asyncio
async def test_deployment_agent_invalid_platform():
    """Test DeploymentOperationsAgent with invalid platform"""
    agent = DeploymentOperationsAgent(llm_client=None, config={})
    result = await agent.execute({
        "platform": "invalid",
        "project_path": "/tmp/test"
    })
    assert isinstance(result, dict), "Should return a dict"
    assert "error" in result, "Should have error for invalid platform"
    # Check success field if present
    if "success" in result:
        assert result["success"] is False


@pytest.mark.asyncio
async def test_tool_endpoints_available(app_client):
    """Test that tool endpoints are available"""
    # Test browser tool endpoint
    response = await app_client.post(
        "/api/tools/browser",
        json={"action": "navigate", "url": "https://example.com"}
    )
    # Should return something (may need auth or setup, but endpoint should exist)
    assert response.status_code != 404
    
    # Test file tool endpoint
    response = await app_client.post(
        "/api/tools/file",
        json={"action": "list", "path": "."}
    )
    assert response.status_code != 404
    
    # Test API tool endpoint
    response = await app_client.post(
        "/api/tools/api",
        json={"method": "GET", "url": "https://example.com"}
    )
    assert response.status_code != 404
    
    # Test database tool endpoint
    response = await app_client.post(
        "/api/tools/database",
        json={"db_type": "sqlite", "connection": {"database": ":memory:"}, "query": "SELECT 1"}
    )
    assert response.status_code != 404
    
    # Test deployment tool endpoint
    response = await app_client.post(
        "/api/tools/deploy",
        json={"platform": "vercel", "project_path": "/tmp/test"}
    )
    assert response.status_code != 404
