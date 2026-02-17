# Tool Agents Documentation

CrucibAI Phase 3: Tool Integrations provides 5 powerful tool agents for real-world automation tasks.

## Overview

The tool agents provide:
- **BrowserAgent**: Web automation with Playwright
- **FileAgent**: File system operations
- **APIAgent**: HTTP API calls
- **DatabaseOperationsAgent**: Database operations
- **DeploymentOperationsAgent**: Cloud deployment

All agents follow a common pattern:
1. Input validation
2. Async execution
3. Structured result with success/error status

## Architecture

### Base Agent

All agents inherit from `BaseAgent` which provides:
- Input validation via `validate_input()`
- Execution via `execute()`
- Error handling via `run()`

### Agent Registry

Agents auto-register using the `@AgentRegistry.register` decorator. This allows:
- Dynamic discovery of all available agents
- Centralized agent management
- Easy addition of new agents

## API Endpoints

All tool endpoints are available at `/api/tools/*`:

### Browser Automation: `/api/tools/browser`

**POST** with JSON body:

```json
{
  "action": "navigate|screenshot|scrape|extract",
  "url": "https://example.com",
  "selector": ".content",  // optional, for scrape
  "extract_type": "text|links|images"  // optional, for extract
}
```

**Examples:**

Navigate to URL:
```json
{"action": "navigate", "url": "https://example.com"}
```

Take screenshot:
```json
{"action": "screenshot", "url": "https://example.com"}
```

Scrape content:
```json
{"action": "scrape", "url": "https://example.com", "selector": ".content"}
```

Extract links:
```json
{"action": "extract", "url": "https://example.com", "extract_type": "links"}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "title": "Example Domain",
  "html": "<html>...",
  "_tokens_used": 0,
  "_model_used": "playwright"
}
```

### File Operations: `/api/tools/file`

**POST** with JSON body:

```json
{
  "action": "read|write|create_dir|delete|move|list|exists",
  "path": "test.txt",
  "content": "...",  // for write
  "destination": "..."  // for move
}
```

**Examples:**

Write file:
```json
{"action": "write", "path": "test.txt", "content": "Hello World"}
```

Read file:
```json
{"action": "read", "path": "test.txt"}
```

List directory:
```json
{"action": "list", "path": "."}
```

**Response:**
```json
{
  "success": true,
  "path": "test.txt",
  "content": "Hello World",
  "size": 11
}
```

**Security:** All file operations are restricted to a workspace directory.

### API Calls: `/api/tools/api`

**POST** with JSON body:

```json
{
  "url": "https://api.github.com/repos/facebook/react",
  "method": "GET|POST|PUT|DELETE|PATCH",
  "headers": {"Authorization": "..."},  // optional
  "data": {...},  // optional, for POST/PUT/PATCH
  "params": {...},  // optional, query parameters
  "auth": ["username", "password"],  // optional
  "timeout": 30  // optional, default 30s
}
```

**Examples:**

GET request:
```json
{
  "url": "https://api.github.com/repos/facebook/react",
  "method": "GET"
}
```

POST request:
```json
{
  "url": "https://httpbin.org/post",
  "method": "POST",
  "data": {"key": "value"}
}
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "headers": {...},
  "data": {...},
  "url": "https://api.github.com/repos/facebook/react"
}
```

### Database Operations: `/api/tools/database`

**POST** with JSON body:

```json
{
  "action": "query|execute|create_table",
  "query": "SELECT * FROM users",
  "database_url": "sqlite:///./test.db",  // optional
  "schema": "CREATE TABLE ..."  // for create_table
}
```

**Examples:**

Query data:
```json
{
  "action": "query",
  "query": "SELECT * FROM users LIMIT 10",
  "database_url": "sqlite:///./app.db"
}
```

Insert data:
```json
{
  "action": "execute",
  "query": "INSERT INTO users (name) VALUES ('John')",
  "database_url": "sqlite:///./app.db"
}
```

**Response:**
```json
{
  "success": true,
  "rows": [...],
  "count": 10
}
```

**Supported databases:** PostgreSQL, MySQL, SQLite (via SQLAlchemy)

### Deployment: `/api/tools/deploy`

**POST** with JSON body:

```json
{
  "platform": "vercel|railway|netlify",
  "files": {
    "index.html": "...",
    "package.json": "..."
  },
  "api_key": "...",
  "project_name": "my-app"
}
```

**Examples:**

Deploy to Vercel:
```json
{
  "platform": "vercel",
  "files": {
    "index.html": "<!DOCTYPE html>...",
    "package.json": "{...}"
  },
  "api_key": "vercel_token_...",
  "project_name": "my-app"
}
```

**Response:**
```json
{
  "success": true,
  "platform": "vercel",
  "url": "https://my-app-abc123.vercel.app",
  "deployment_id": "dpl_abc123"
}
```

**Supported platforms:**
- Vercel (full API integration)
- Railway (pending CLI integration)
- Netlify (pending CLI integration)

## Usage in Code

### Direct Agent Usage

```python
from agents.tools.browser_agent import BrowserAgent

# Initialize agent
agent = BrowserAgent(llm_client=None, config={})

# Run agent
result = await agent.run({
    "action": "navigate",
    "url": "https://example.com"
})

print(result)
```

### Via API

```bash
curl -X POST http://localhost:8000/api/tools/browser \
  -H "Content-Type: application/json" \
  -d '{"action": "navigate", "url": "https://example.com"}'
```

## Testing

All agents have comprehensive unit tests:

```bash
cd backend
pytest tests/test_tool_agents.py -v
```

**Test coverage:**
- Input validation
- Success cases
- Error handling
- Agent registry

## Security Considerations

1. **FileAgent**: All operations restricted to workspace directory
2. **APIAgent**: Rate limiting on API endpoints (via middleware)
3. **DatabaseAgent**: SQL injection protection via parameterized queries
4. **DeploymentAgent**: API keys must be provided by user
5. **BrowserAgent**: Runs in headless mode, no display server required

## Dependencies

Added to `requirements.txt`:
```
playwright>=1.40.0
httpx>=0.25.0
sqlalchemy>=2.0.0
```

Install Playwright browsers:
```bash
playwright install chromium
```

## Error Handling

All agents return a consistent error structure:

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "validation|execution"
}
```

## Future Enhancements

1. Add authentication/authorization for tool endpoints
2. Implement rate limiting per user
3. Add audit logging for all tool operations
4. Extend deployment platforms (Fly.io, Heroku, AWS)
5. Add more browser actions (fill forms, click buttons)
6. Add database schema migration support
7. Add file upload/download for FileAgent

## Examples

See `backend/tests/test_tool_agents.py` for comprehensive examples of each agent.

## Support

For issues or questions about tool agents, see:
- Backend documentation: `backend/DEVELOPER_GUIDE.md`
- API documentation: `backend/API_DOCUMENTATION.md`
