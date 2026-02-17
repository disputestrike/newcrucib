# Tool Agents Documentation

## Overview

The CrucibAI platform now includes 5 powerful tool agents that provide real automation capabilities:

1. **BrowserAgent** - Browser automation with Playwright
2. **FileAgent** - File system operations
3. **APIAgent** - HTTP requests and API integration
4. **DatabaseOperationsAgent** - SQL database operations
5. **DeploymentOperationsAgent** - Cloud deployment automation

---

## BrowserAgent

Automate browser actions using Playwright.

### Capabilities
- Navigate to URLs
- Take screenshots
- Scrape content
- Fill forms
- Click elements
- Extract data

### API Endpoint
`POST /api/tools/browser`

### Request Format
```json
{
  "action": "navigate|screenshot|scrape|fill_form|click",
  "url": "https://example.com",
  "selector": ".some-class",
  "form_data": {"name": "value"},
  "screenshot_path": "screenshot.png"
}
```

### Examples

#### Navigate to URL
```json
{
  "action": "navigate",
  "url": "https://example.com"
}
```

#### Take Screenshot
```json
{
  "action": "screenshot",
  "url": "https://example.com",
  "screenshot_path": "/tmp/screenshot.png"
}
```

#### Scrape Content
```json
{
  "action": "scrape",
  "url": "https://example.com",
  "selector": "body"
}
```

---

## FileAgent

Perform file system operations within a workspace.

### Capabilities
- Read files
- Write files
- Move/rename files
- Delete files
- List directory contents
- Create directories

### API Endpoint
`POST /api/tools/file`

### Request Format
```json
{
  "action": "read|write|move|delete|list|mkdir",
  "path": "path/to/file",
  "content": "...",
  "destination": "..."
}
```

### Examples

#### Write File
```json
{
  "action": "write",
  "path": "test.txt",
  "content": "Hello World"
}
```

#### Read File
```json
{
  "action": "read",
  "path": "test.txt"
}
```

#### List Directory
```json
{
  "action": "list",
  "path": "."
}
```

---

## APIAgent

Make HTTP requests and handle API integrations.

### Capabilities
- GET/POST/PUT/DELETE requests
- Handle authentication (Bearer, Basic, OAuth)
- Parse JSON/XML responses
- Handle rate limits

### API Endpoint
`POST /api/tools/api`

### Request Format
```json
{
  "method": "GET|POST|PUT|DELETE",
  "url": "https://api.example.com/endpoint",
  "headers": {"Authorization": "Bearer token"},
  "body": {"key": "value"},
  "params": {"page": 1}
}
```

### Examples

#### GET Request
```json
{
  "method": "GET",
  "url": "https://api.github.com/users/octocat"
}
```

#### POST Request
```json
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "headers": {"Authorization": "Bearer YOUR_TOKEN"},
  "body": {"name": "John Doe", "email": "john@example.com"}
}
```

---

## DatabaseOperationsAgent

Execute SQL queries on various databases.

### Capabilities
- PostgreSQL support
- MySQL support
- SQLite support
- Query execution
- Transaction management

### API Endpoint
`POST /api/tools/database`

### Request Format
```json
{
  "db_type": "postgres|mysql|sqlite",
  "connection": {
    "host": "localhost",
    "database": "mydb",
    "user": "username",
    "password": "password"
  },
  "query": "SELECT * FROM users WHERE id = $1",
  "params": [123]
}
```

### Examples

#### SQLite Query
```json
{
  "db_type": "sqlite",
  "connection": {"database": "test.db"},
  "query": "SELECT * FROM users",
  "params": []
}
```

#### PostgreSQL Insert
```json
{
  "db_type": "postgres",
  "connection": {
    "host": "localhost",
    "database": "myapp",
    "user": "postgres",
    "password": "secret"
  },
  "query": "INSERT INTO users (name, email) VALUES ($1, $2)",
  "params": ["John Doe", "john@example.com"]
}
```

---

## DeploymentOperationsAgent

Deploy applications to cloud platforms.

### Capabilities
- Vercel deployment
- Railway deployment
- Netlify deployment
- Environment configuration
- Build automation

### API Endpoint
`POST /api/tools/deploy`

### Request Format
```json
{
  "platform": "vercel|railway|netlify",
  "project_path": "./my-app",
  "config": {
    "env": {...},
    "build_command": "npm run build"
  }
}
```

### Examples

#### Deploy to Vercel
```json
{
  "platform": "vercel",
  "project_path": "./my-nextjs-app"
}
```

#### Deploy to Netlify
```json
{
  "platform": "netlify",
  "project_path": "./dist"
}
```

---

## Security Considerations

1. **BrowserAgent**: Be cautious with untrusted URLs. The agent runs in headless mode for security.
2. **FileAgent**: All operations are scoped to a workspace directory to prevent unauthorized file access.
3. **APIAgent**: Always validate API keys and credentials. Never log sensitive data.
4. **DatabaseOperationsAgent**: Use parameterized queries to prevent SQL injection. Never expose database credentials.
5. **DeploymentOperationsAgent**: Ensure deployment credentials are properly secured.

---

## Testing

All tool agents have comprehensive test coverage. Run tests with:

```bash
cd backend
pytest tests/test_tool_agents.py -v
```

---

## Architecture

All tool agents inherit from `BaseAgent` which provides:
- Common initialization
- Error handling
- Logging
- Run method that wraps execution

Each agent implements an `execute()` method that performs the specific tool operations.

---

## Future Enhancements

- **BrowserAgent**: Add support for authentication flows, file uploads, network interception
- **FileAgent**: Add file watching, compression, encryption
- **APIAgent**: Add GraphQL support, request retries, circuit breakers
- **DatabaseOperationsAgent**: Add connection pooling, query optimization, migration support
- **DeploymentOperationsAgent**: Add more platforms (AWS, Google Cloud, Azure), rollback support

---

## Contributing

To add a new tool agent:

1. Create a new file in `backend/tools/`
2. Inherit from `BaseAgent`
3. Implement the `execute()` method
4. Add tests in `backend/tests/test_tool_agents.py`
5. Add API endpoint in `backend/server.py`
6. Update documentation
