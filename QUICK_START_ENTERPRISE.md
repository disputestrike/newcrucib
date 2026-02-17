# Phase 4 Enterprise Features - Quick Reference

## Quick Start

### 1. Run the Demo
```bash
cd backend
python demo_enterprise_features.py
```

### 2. Run Tests
```bash
cd backend
pytest tests/test_enterprise_features.py -v
```

### 3. Try the API
```bash
# Start server (requires environment setup)
cd backend
uvicorn server:app --reload
```

## API Examples

### Agent Marketplace

**Publish an agent:**
```bash
curl -X POST http://localhost:8000/api/marketplace/publish \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyAgent",
    "author": "you@example.com",
    "description": "Custom agent",
    "version": "1.0.0",
    "category": "utility",
    "system_prompt": "You are a helpful agent",
    "input_schema": {},
    "output_schema": {},
    "dependencies": []
  }'
```

**List agents:**
```bash
curl http://localhost:8000/api/marketplace/agents
curl http://localhost:8000/api/marketplace/agents?category=frontend
```

**Install an agent:**
```bash
curl -X POST http://localhost:8000/api/marketplace/install/MyAgent
```

**Rate an agent:**
```bash
curl -X POST http://localhost:8000/api/marketplace/rate/MyAgent?rating=4.5
```

### Team Memory

**Record a build:**
```bash
curl -X POST http://localhost:8000/api/memory/record-build \
  -H "Content-Type: application/json" \
  -d '{
    "id": "build_123",
    "user_id": "user_456",
    "team_id": "team_789",
    "prompt": "Build a todo app",
    "workflow": "standard",
    "tech_stack": {
      "frontend": "React",
      "backend": "FastAPI"
    },
    "success": true,
    "quality_score": 85.0,
    "duration_seconds": 120.0,
    "files_generated": 15,
    "timestamp": "2024-01-01T00:00:00Z"
  }'
```

**Get stack suggestion:**
```bash
curl "http://localhost:8000/api/memory/suggest-stack?prompt=Build%20a%20blog&team_id=team_789"
```

**Get team insights:**
```bash
curl http://localhost:8000/api/memory/insights/team_789
```

### Dashboard

**Get real-time metrics:**
```bash
curl http://localhost:8000/api/dashboard
```

### Self-Improvement

**Get optimization report:**
```bash
curl http://localhost:8000/api/optimization/report
```

**Get best prompts:**
```bash
curl http://localhost:8000/api/optimization/best-prompts
```

## Python Examples

### Marketplace
```python
from marketplace.agent_store import AgentMarketplace, CustomAgentDefinition

marketplace = AgentMarketplace()

# Publish
agent = CustomAgentDefinition(
    name="MyAgent",
    author="you@example.com",
    description="Custom agent",
    version="1.0.0",
    category="utility",
    system_prompt="You are helpful",
    input_schema={},
    output_schema={},
    dependencies=[]
)
marketplace.publish_agent(agent)

# List
agents = marketplace.list_agents(category="frontend")

# Install
marketplace.install_agent("MyAgent")

# Rate
marketplace.rate_agent("MyAgent", 4.5)
```

### Team Memory
```python
from memory.team_memory import TeamMemory, BuildHistory
from datetime import datetime

memory = TeamMemory()

# Record
build = BuildHistory(
    id="build_1",
    user_id="user_1",
    team_id="team_1",
    prompt="Build app",
    workflow="standard",
    tech_stack={"frontend": "React"},
    success=True,
    quality_score=85.0,
    duration_seconds=120.0,
    files_generated=15,
    timestamp=datetime.utcnow().isoformat()
)
memory.record_build(build)

# Suggest
suggestion = memory.suggest_stack("New app", "team_1")

# Insights
insights = memory.get_insights("team_1")
```

### Dashboard
```python
from observability.dashboard import Dashboard

dashboard = Dashboard()

# Record execution
dashboard.record_execution(
    agent_name="Frontend Generation",
    success=True,
    duration_ms=2340.5,
    tokens=1523,
    quality_score=85.2
)

# Get data
data = dashboard.get_dashboard_data()
print(f"Success rate: {data['summary']['overall_success_rate']}%")
```

### Self-Improvement
```python
from optimization.self_improvement import SelfImprovement, PromptVariant

optimizer = SelfImprovement()

# Add variants
variant = PromptVariant(
    id="v1",
    agent_name="TestAgent",
    prompt="You are an expert..."
)
optimizer.add_variant("TestAgent", variant)

# Get prompt (epsilon-greedy)
selected = optimizer.get_prompt("TestAgent")

# Record result
optimizer.record_result(
    variant_id="v1",
    success=True,
    quality_score=88.5,
    duration=2340.5
)

# Get best
best = optimizer.get_best_prompts()
```

## File Locations

```
backend/
├── agents/
│   ├── base_agent.py          # Base class
│   └── registry.py            # Registry
├── marketplace/
│   └── agent_store.py         # Marketplace
├── memory/
│   └── team_memory.py         # Team memory
├── observability/
│   └── dashboard.py           # Dashboard
├── optimization/
│   └── self_improvement.py    # Optimizer
├── tests/
│   ├── test_enterprise_features.py  # Unit tests
│   └── test_enterprise_api.py       # API tests
├── ENTERPRISE_FEATURES.md     # Full docs
└── demo_enterprise_features.py # Demo script
```

## Common Tasks

### Test Everything
```bash
cd backend
pytest tests/test_enterprise_features.py -v
```

### Run Demo
```bash
cd backend
python demo_enterprise_features.py
```

### Check Code
```bash
cd backend
python -c "from marketplace.agent_store import *; from memory.team_memory import *; from observability.dashboard import *; from optimization.self_improvement import *; print('All imports OK')"
```

### View Documentation
```bash
# Full documentation
cat backend/ENTERPRISE_FEATURES.md

# Quick summary
cat PHASE_4_COMPLETE.md
```

## Environment Setup

Required environment variables for full server:
```bash
export MONGO_URL="mongodb://localhost:27017"
export DB_NAME="crucibai"
export JWT_SECRET="your-secret-key"
export OPENAI_API_KEY="sk-..."  # Optional
export ANTHROPIC_API_KEY="sk-..." # Optional
```

## Troubleshooting

**Import errors:**
```bash
cd backend
export PYTHONPATH=$PYTHONPATH:.
```

**Test failures:**
```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

**Server won't start:**
```bash
# Check environment variables
env | grep -E "MONGO|JWT|API"

# Install dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Integration**: Connect to existing orchestration
2. **Database**: Migrate to MongoDB for persistence
3. **UI**: Build admin interface for marketplace
4. **WebSocket**: Add real-time dashboard updates
5. **Analytics**: Add more advanced metrics

## Support

- Full Documentation: `backend/ENTERPRISE_FEATURES.md`
- Implementation Summary: `PHASE_4_COMPLETE.md`
- Demo Script: `backend/demo_enterprise_features.py`
- Tests: `backend/tests/test_enterprise_features.py`

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Date:** 2024-02-17
