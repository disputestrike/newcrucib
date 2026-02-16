# CrucibAI

**State the idea. We build it.** No product limit—web, SaaS, bots, agents, dashboards, tools. One idea to the next.

**Local app (after starting backend + frontend):**  
**http://localhost:3000**

Backend API: http://localhost:8000  

How to run: see **[RUN.md](RUN.md)**. Vision: **[BUILD_ANYTHING.md](BUILD_ANYTHING.md)**.

---

## V2 API (New Agent Architecture)

CrucibAI V2 introduces a production-ready orchestration system with specialized agents, automatic validation, and quality scoring.

### Generate with V2

```bash
curl -X POST http://localhost:8000/api/generate/v2 \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a todo app with React and FastAPI",
    "workflow": "full_stack",
    "validate": true,
    "score_quality": true
  }'
```

**Available Workflows:**
- `full_stack` - Complete frontend + backend + database + deployment (10 agents)
- `frontend_only` - React/Vue frontend with deployment (7 agents)
- `backend_api` - RESTful API with database and auth (8 agents)
- `landing_page` - Marketing/landing page with design (4 agents)
- `documentation_only` - Documentation generation (2 agents)

### List Available Agents

```bash
curl http://localhost:8000/api/agents/v2
```

Returns list of all 10 registered V2 agents with descriptions.

### Get Workflows

```bash
curl http://localhost:8000/api/workflows
```

Returns detailed information about all predefined workflows including:
- Agent list
- Estimated time
- Best use cases

### Validate Code

```bash
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "files": {
      "src/App.tsx": "import React from \"react\";\n\nfunction App() {\n  return <div>Hello</div>;\n}\n\nexport default App;"
    },
    "language": "TypeScript",
    "validate_build": true
  }'
```

Validates code syntax and optionally runs build checks.

### Score Code Quality

```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "files": {
      "main.py": "def hello():\n    print(\"Hello World\")"
    },
    "language": "Python"
  }'
```

Returns quality scores across multiple dimensions:
- Readability
- Maintainability
- Complexity
- Documentation
- Best practices
- Security

---

# Here are your Instructions
