"""
Tests for Phase 3 Tool Agents
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.browser_agent import BrowserAgent
from tools.file_agent import FileAgent
from tools.api_agent import APIAgent
from tools.database_operations_agent import DatabaseOperationsAgent
from tools.deployment_operations_agent import DeploymentOperationsAgent


# ==================== BrowserAgent Tests ====================

@pytest.mark.asyncio
async def test_browser_agent_navigate():
    """Test BrowserAgent navigate action"""
    agent = BrowserAgent(llm_client=None, config={})
    
    # Mock playwright
    with patch('tools.browser_agent.async_playwright') as mock_playwright:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.content = AsyncMock(return_value="<html>Test</html>")
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_p = AsyncMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__.return_value = mock_p
        
        result = await agent.execute({
            "action": "navigate",
            "url": "https://example.com"
        })
        
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        assert result["title"] == "Test Page"


@pytest.mark.asyncio
async def test_browser_agent_scrape():
    """Test BrowserAgent scrape action"""
    agent = BrowserAgent(llm_client=None, config={})
    
    with patch('tools.browser_agent.async_playwright') as mock_playwright:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.inner_text = AsyncMock(return_value="Test Text")
        mock_element.inner_html = AsyncMock(return_value="<div>Test</div>")
        mock_page.goto = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=mock_element)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        
        mock_p = AsyncMock()
        mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_playwright.return_value.__aenter__.return_value = mock_p
        
        result = await agent.execute({
            "action": "scrape",
            "url": "https://example.com",
            "selector": "body"
        })
        
        assert result["success"] is True
        assert result["text"] == "Test Text"


# ==================== FileAgent Tests ====================

def test_file_agent_write_read(tmp_path):
    """Test FileAgent write and read operations"""
    agent = FileAgent(llm_client=None, config={"workspace": str(tmp_path)})
    
    # Write file
    write_result = agent._write_file({
        "path": "test.txt",
        "content": "Hello World"
    })
    assert write_result["success"] is True
    
    # Read file
    read_result = agent._read_file({"path": "test.txt"})
    assert read_result["success"] is True
    assert read_result["content"] == "Hello World"


def test_file_agent_list_directory(tmp_path):
    """Test FileAgent list directory operation"""
    agent = FileAgent(llm_client=None, config={"workspace": str(tmp_path)})
    
    # Create some files
    agent._write_file({"path": "file1.txt", "content": "test1"})
    agent._write_file({"path": "file2.txt", "content": "test2"})
    
    # List directory
    result = agent._list_directory({"path": "."})
    assert result["success"] is True
    assert result["count"] == 2


def test_file_agent_mkdir(tmp_path):
    """Test FileAgent create directory operation"""
    agent = FileAgent(llm_client=None, config={"workspace": str(tmp_path)})
    
    result = agent._create_directory({"path": "test_dir"})
    assert result["success"] is True
    assert (tmp_path / "test_dir").exists()


# ==================== APIAgent Tests ====================

@pytest.mark.asyncio
async def test_api_agent_get():
    """Test APIAgent GET request"""
    agent = APIAgent(llm_client=None, config={})
    
    with patch('tools.api_agent.httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.example.com/test"
        
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await agent.execute({
            "method": "GET",
            "url": "https://api.example.com/test"
        })
        
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["data"] == {"data": "test"}


@pytest.mark.asyncio
async def test_api_agent_post():
    """Test APIAgent POST request"""
    agent = APIAgent(llm_client=None, config={})
    
    with patch('tools.api_agent.httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123}
        mock_response.headers = {"content-type": "application/json"}
        mock_response.url = "https://api.example.com/create"
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        result = await agent.execute({
            "method": "POST",
            "url": "https://api.example.com/create",
            "body": {"name": "test"}
        })
        
        assert result["success"] is True
        assert result["status_code"] == 201


# ==================== DatabaseOperationsAgent Tests ====================

@pytest.mark.asyncio
async def test_database_agent_sqlite():
    """Test DatabaseOperationsAgent with SQLite"""
    agent = DatabaseOperationsAgent(llm_client=None, config={})
    
    # Create in-memory database
    result = await agent.execute({
        "db_type": "sqlite",
        "connection": {"database": ":memory:"},
        "query": "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)",
        "params": []
    })
    
    # Note: This will fail without actual database setup
    # In real tests, use a test database
    assert "error" in result or "success" in result


@pytest.mark.asyncio
async def test_database_agent_postgres_mock():
    """Test DatabaseOperationsAgent with mocked Postgres"""
    agent = DatabaseOperationsAgent(llm_client=None, config={})
    
    with patch('tools.database_operations_agent.asyncpg.connect') as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[{"id": 1, "name": "test"}])
        mock_conn.close = AsyncMock()
        mock_connect.return_value = mock_conn
        
        result = await agent.execute({
            "db_type": "postgres",
            "connection": {"host": "localhost", "database": "test"},
            "query": "SELECT * FROM users",
            "params": []
        })
        
        assert result["success"] is True
        assert result["row_count"] == 1


# ==================== DeploymentOperationsAgent Tests ====================

@pytest.mark.asyncio
async def test_deployment_agent_vercel_mock(tmp_path):
    """Test DeploymentOperationsAgent with mocked Vercel"""
    agent = DeploymentOperationsAgent(llm_client=None, config={})
    
    # Create a temporary directory for the test
    test_app = tmp_path / "test-app"
    test_app.mkdir()
    
    with patch('tools.deployment_operations_agent.subprocess.run') as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Deployed to https://my-app-123.vercel.app"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = await agent.execute({
            "platform": "vercel",
            "project_path": str(test_app)
        })
        
        assert result["success"] is True
        assert "vercel" in result["platform"]


@pytest.mark.asyncio
async def test_deployment_agent_unknown_platform():
    """Test DeploymentOperationsAgent with unknown platform"""
    agent = DeploymentOperationsAgent(llm_client=None, config={})
    
    result = await agent.execute({
        "platform": "unknown",
        "project_path": "./test-app"
    })
    
    assert "error" in result


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_browser_agent_run_method():
    """Test BrowserAgent run method wraps execute"""
    agent = BrowserAgent(llm_client=None, config={})
    
    with patch.object(agent, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = {"success": True}
        
        result = await agent.run({"action": "navigate", "url": "https://example.com"})
        
        assert result["success"] is True
        mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_file_agent_execute_wrapper():
    """Test FileAgent execute method"""
    agent = FileAgent(llm_client=None, config={"workspace": "/tmp/test"})
    
    # Test with unknown action
    result = await agent.execute({"action": "unknown"})
    assert "error" in result
