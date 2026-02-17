# CrucibAI Tool Agents

Phase 3: Tool Integrations - 5 Real Tool Agents for browser automation, file operations, API calls, database queries, and cloud deployment.

## Overview

CrucibAI now includes 5 powerful tool agents that extend the platform's capabilities to match Manus' 29 tools. These agents provide real-world integrations for common development tasks:

1. **BrowserAgent** - Browser automation with Playwright
2. **FileAgent** - File system operations
3. **APIAgent** - HTTP requests with authentication
4. **DatabaseOperationsAgent** - SQL query execution
5. **DeploymentOperationsAgent** - Cloud platform deployment

## Installation

### Dependencies

All required dependencies are in `backend/requirements.txt`:

```bash
pip install playwright asyncpg aiomysql aiosqlite
python -m playwright install chromium
```

### Import

```python
from tools.browser_agent import BrowserAgent
from tools.file_agent import FileAgent
from tools.api_agent import APIAgent
from tools.database_operations_agent import DatabaseOperationsAgent
from tools.deployment_operations_agent import DeploymentOperationsAgent
```

## Tool Agents

### 1. BrowserAgent

Automate browser actions using Playwright for web scraping, testing, and automation.

**Endpoint:** `POST /api/tools/browser`

**Actions:**
- `navigate` - Navigate to a URL
- `screenshot` - Take screenshot of a page
- `scrape` - Extract content from page
- `fill_form` - Fill and submit forms
- `click` - Click elements on page

**Example: Navigate to URL**
```python
from tools.browser_agent import BrowserAgent

agent = BrowserAgent(llm_client=None, config={})
result = await agent.execute({
    "action": "navigate",
    "url": "https://example.com"
})
# Returns: {"url": "...", "title": "...", "content_length": 123, "success": True}
```

**Example: Take Screenshot**
```python
result = await agent.execute({
    "action": "screenshot",
    "url": "https://example.com",
    "screenshot_path": "screenshot.png"
})
# Returns: {"screenshot_path": "...", "screenshot_base64": "...", "success": True}
```

**Example: Scrape Content**
```python
result = await agent.execute({
    "action": "scrape",
    "url": "https://example.com",
    "selector": "h1"  # CSS selector
})
# Returns: {"text": "...", "html": "...", "success": True}
```

**Example: Fill Form**
```python
result = await agent.execute({
    "action": "fill_form",
    "url": "https://example.com/login",
    "form_data": {
        "#username": "user@example.com",
        "#password": "secret123"
    },
    "submit_selector": "button[type='submit']"
})
# Returns: {"form_filled": [...], "current_url": "...", "success": True}
```

**Example: Click Element**
```python
result = await agent.execute({
    "action": "click",
    "url": "https://example.com",
    "selector": ".login-button"
})
# Returns: {"clicked": "...", "current_url": "...", "success": True}
```

### 2. FileAgent

Perform file system operations with workspace isolation.

**Endpoint:** `POST /api/tools/file`

**Actions:**
- `read` - Read file content
- `write` - Write content to file
- `move` - Move/rename file
- `delete` - Delete file or directory
- `list` - List directory contents
- `mkdir` - Create directory

**Example: Write File**
```python
from tools.file_agent import FileAgent

agent = FileAgent(llm_client=None, config={"workspace": "./workspace"})
result = await agent.execute({
    "action": "write",
    "path": "test.txt",
    "content": "Hello, World!"
})
# Returns: {"path": "...", "size": 13, "success": True}
```

**Example: Read File**
```python
result = await agent.execute({
    "action": "read",
    "path": "test.txt"
})
# Returns: {"path": "...", "content": "Hello, World!", "size": 13, "success": True}
```

**Example: List Directory**
```python
result = await agent.execute({
    "action": "list",
    "path": "."
})
# Returns: {"path": "...", "files": [...], "count": 5, "success": True}
```

**Example: Create Directory**
```python
result = await agent.execute({
    "action": "mkdir",
    "path": "my/nested/dir"
})
# Returns: {"path": "...", "success": True}
```

**Example: Delete File**
```python
result = await agent.execute({
    "action": "delete",
    "path": "old_file.txt"
})
# Returns: {"path": "...", "success": True}
```

**Example: Move File**
```python
result = await agent.execute({
    "action": "move",
    "path": "old.txt",
    "destination": "new.txt"
})
# Returns: {"source": "...", "destination": "...", "success": True}
```

### 3. APIAgent

Make HTTP requests with support for authentication and JSON handling.

**Endpoint:** `POST /api/tools/api`

**Methods:** `GET`, `POST`, `PUT`, `DELETE`

**Example: GET Request**
```python
from tools.api_agent import APIAgent

agent = APIAgent(llm_client=None, config={})
result = await agent.execute({
    "method": "GET",
    "url": "https://api.example.com/users",
    "headers": {"Authorization": "Bearer token123"},
    "params": {"page": 1, "limit": 10}
})
# Returns: {"status_code": 200, "success": True, "data": {...}, "headers": {...}}
```

**Example: POST Request**
```python
result = await agent.execute({
    "method": "POST",
    "url": "https://api.example.com/users",
    "headers": {"Authorization": "Bearer token123"},
    "body": {
        "name": "John Doe",
        "email": "john@example.com"
    }
})
# Returns: {"status_code": 201, "success": True, "data": {...}}
```

**Example: PUT Request**
```python
result = await agent.execute({
    "method": "PUT",
    "url": "https://api.example.com/users/123",
    "headers": {"Authorization": "Bearer token123"},
    "body": {"name": "Jane Doe"}
})
```

**Example: DELETE Request**
```python
result = await agent.execute({
    "method": "DELETE",
    "url": "https://api.example.com/users/123",
    "headers": {"Authorization": "Bearer token123"}
})
```

### 4. DatabaseOperationsAgent

Execute SQL queries on PostgreSQL, MySQL, or SQLite databases.

**Endpoint:** `POST /api/tools/database`

**Supported Databases:**
- PostgreSQL (`postgres`)
- MySQL (`mysql`)
- SQLite (`sqlite`)

**Example: SQLite Query**
```python
from tools.database_operations_agent import DatabaseOperationsAgent

agent = DatabaseOperationsAgent(llm_client=None, config={})
result = await agent.execute({
    "db_type": "sqlite",
    "connection": {"database": "mydb.db"},
    "query": "SELECT * FROM users WHERE id = ?",
    "params": [123]
})
# Returns: {"rows": [...], "row_count": 1, "success": True}
```

**Example: PostgreSQL Insert**
```python
result = await agent.execute({
    "db_type": "postgres",
    "connection": {
        "host": "localhost",
        "database": "mydb",
        "user": "postgres",
        "password": "secret"
    },
    "query": "INSERT INTO users (name, email) VALUES ($1, $2)",
    "params": ["John Doe", "john@example.com"]
})
# Returns: {"status": "INSERT 0 1", "success": True}
```

**Example: MySQL Select**
```python
result = await agent.execute({
    "db_type": "mysql",
    "connection": {
        "host": "localhost",
        "database": "mydb",
        "user": "root",
        "password": "secret"
    },
    "query": "SELECT * FROM users WHERE email = %s",
    "params": ["john@example.com"]
})
# Returns: {"rows": [...], "row_count": 1, "success": True}
```

### 5. DeploymentOperationsAgent

Deploy applications to cloud platforms.

**Endpoint:** `POST /api/tools/deploy`

**Supported Platforms:**
- Vercel (`vercel`)
- Railway (`railway`)
- Netlify (`netlify`)

**Example: Deploy to Vercel**
```python
from tools.deployment_operations_agent import DeploymentOperationsAgent

agent = DeploymentOperationsAgent(llm_client=None, config={})
result = await agent.execute({
    "platform": "vercel",
    "project_path": "./my-app",
    "config": {
        "env": {"API_KEY": "secret"},
        "build_command": "npm run build"
    }
})
# Returns: {"platform": "vercel", "url": "https://...", "success": True}
```

**Example: Deploy to Railway**
```python
result = await agent.execute({
    "platform": "railway",
    "project_path": "./my-app"
})
# Returns: {"platform": "railway", "success": True, "output": "..."}
```

**Example: Deploy to Netlify**
```python
result = await agent.execute({
    "platform": "netlify",
    "project_path": "./my-app"
})
# Returns: {"platform": "netlify", "url": "https://...", "success": True}
```

## API Endpoints

All tool agents are available via REST API endpoints:

```bash
# Browser automation
POST /api/tools/browser
Content-Type: application/json
{"action": "navigate", "url": "https://example.com"}

# File operations
POST /api/tools/file
Content-Type: application/json
{"action": "read", "path": "test.txt"}

# HTTP requests
POST /api/tools/api
Content-Type: application/json
{"method": "GET", "url": "https://api.example.com/data"}

# Database queries
POST /api/tools/database
Content-Type: application/json
{"db_type": "sqlite", "connection": {...}, "query": "SELECT * FROM users"}

# Cloud deployment
POST /api/tools/deploy
Content-Type: application/json
{"platform": "vercel", "project_path": "./my-app"}
```

## Error Handling

All agents return a consistent error format:

```python
{
    "error": "Error message here",
    "success": False,
    "agent": "AgentName"  # Optional
}
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_tool_agents.py -v
```

Test coverage includes:
- ✅ FileAgent: write, read, list, mkdir, delete
- ✅ DatabaseAgent: SQLite create, insert, select
- ✅ APIAgent: GET, POST requests
- ✅ BrowserAgent: navigate, scrape
- ✅ All tool endpoints availability

## Architecture

### BaseAgent

All tool agents inherit from `BaseAgent`:

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, llm_client, config):
        super().__init__(llm_client, config)
        self.name = "MyAgent"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation here
        return {"success": True, "result": "..."}
```

### Configuration

Each agent accepts a configuration dictionary:

```python
agent = FileAgent(
    llm_client=None,  # Optional LLM client for AI-powered features
    config={
        "workspace": "./workspace",  # Agent-specific config
        "max_file_size": 1000000
    }
)
```

### Async Execution

All agents use async/await for non-blocking operations:

```python
import asyncio

async def main():
    agent = BrowserAgent(None, {})
    result = await agent.execute({"action": "navigate", "url": "https://example.com"})
    print(result)

asyncio.run(main())
```

## Security

- **FileAgent**: Operates within configured workspace directory (sandbox)
- **APIAgent**: Supports bearer tokens, basic auth, custom headers
- **DatabaseAgent**: Uses parameterized queries to prevent SQL injection
- **BrowserAgent**: Runs in headless mode by default
- **DeploymentAgent**: Uses platform CLI tools with subprocess isolation

## Integration with Agent DAG

Tool agents can be registered in the Agent DAG for orchestration:

```python
# In agent_dag.py
AGENT_DAG = {
    # ... existing agents
    "Browser Tool": {
        "depends_on": ["Stack Selector"],
        "system_prompt": "You are a Browser Tool. Use BrowserAgent to scrape data."
    },
    "File Tool": {
        "depends_on": ["Backend Generation"],
        "system_prompt": "You are a File Tool. Use FileAgent to manage files."
    },
    # ... etc
}
```

## Future Enhancements

Potential additions for Phase 4:
- [ ] Email Agent (SendGrid, Resend)
- [ ] Storage Agent (S3, GCS, Azure)
- [ ] Container Agent (Docker operations)
- [ ] Git Agent (Repository operations)
- [ ] Monitoring Agent (Sentry, DataDog)

## Support

For issues or questions:
- GitHub Issues: https://github.com/disputestrike/newcrucib/issues
- Documentation: See individual agent files for detailed docstrings

## License

Part of CrucibAI - see main repository LICENSE.
