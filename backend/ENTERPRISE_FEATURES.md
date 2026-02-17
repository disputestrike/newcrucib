# Phase 4: Enterprise Features Documentation

This document describes the Phase 4 Enterprise Features added to CrucibAI, including the Agent Marketplace, Team Memory, Observability Dashboard, and Self-Improvement system.

## Overview

Phase 4 introduces four major enterprise features that create competitive moats:

1. **Agent Marketplace** - Create, share, and install custom agents
2. **Team Memory** - Learn from past builds and suggest improvements
3. **Observability Dashboard** - Real-time agent performance monitoring
4. **Self-Improvement System** - A/B test prompts and automatically optimize

## Agent Marketplace

### Purpose
Allow users to create custom agents, publish them to a marketplace, and install agents created by others.

### Features
- **Publish Custom Agents**: Define agents with custom system prompts, input/output schemas, and metadata
- **Install Agents**: Download and install agents from the marketplace
- **Rate Agents**: 1-5 star rating system with average ratings
- **Category Filtering**: Filter agents by category (frontend, backend, design, utility, etc.)
- **Download Tracking**: Track popularity via download counts

### API Endpoints

#### Publish an Agent
```http
POST /api/marketplace/publish
Content-Type: application/json

{
  "name": "MyCustomAgent",
  "author": "john@example.com",
  "description": "A specialized agent for React component generation",
  "version": "1.0.0",
  "category": "frontend",
  "system_prompt": "You are an expert React developer...",
  "input_schema": {
    "type": "object",
    "properties": {
      "component_type": {"type": "string"}
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "code": {"type": "string"}
    }
  },
  "dependencies": []
}
```

#### Install an Agent
```http
POST /api/marketplace/install/{agent_name}
```

#### List All Agents
```http
GET /api/marketplace/agents?category=frontend
```

#### Rate an Agent
```http
POST /api/marketplace/rate/{agent_name}?rating=4.5
```

### Code Example

```python
from marketplace.agent_store import AgentMarketplace, CustomAgentDefinition

# Initialize marketplace
marketplace = AgentMarketplace(store_path="./marketplace")

# Create a custom agent definition
agent = CustomAgentDefinition(
    name="ReactExpert",
    author="dev@company.com",
    description="Generates React components with TypeScript",
    version="1.0.0",
    category="frontend",
    system_prompt="You are an expert React + TypeScript developer...",
    input_schema={"type": "object"},
    output_schema={"type": "object"},
    dependencies=[]
)

# Publish to marketplace
result = marketplace.publish_agent(agent)
print(result)  # {"success": True, "agent_name": "ReactExpert", ...}

# List available agents
agents = marketplace.list_agents(category="frontend")
for agent in agents:
    print(f"{agent['name']} - ⭐ {agent['rating']} - 📥 {agent['downloads']}")
```

## Team Memory

### Purpose
Learn from past builds to suggest optimal tech stacks and provide insights into team performance.

### Features
- **Build Recording**: Store complete build history with quality scores and metadata
- **Stack Suggestions**: Recommend tech stacks based on past successes
- **Team Insights**: Calculate success rates, quality trends, and speed improvements
- **Historical Analysis**: Identify patterns in successful builds

### API Endpoints

#### Record a Build
```http
POST /api/memory/record-build
Content-Type: application/json

{
  "id": "build_123",
  "user_id": "user_456",
  "team_id": "team_789",
  "prompt": "Build a todo app",
  "workflow": "standard",
  "tech_stack": {
    "frontend": "React",
    "backend": "FastAPI",
    "database": "PostgreSQL"
  },
  "success": true,
  "quality_score": 85.0,
  "duration_seconds": 120.0,
  "files_generated": 15,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Get Stack Suggestion
```http
GET /api/memory/suggest-stack?prompt=Build%20a%20blog&team_id=team_789
```

Response:
```json
{
  "suggestion": {
    "frontend": "React",
    "backend": "FastAPI",
    "database": "PostgreSQL"
  },
  "reason": "Used 12 times with 87.3 avg quality",
  "usage_count": 12,
  "avg_quality": 87.3
}
```

#### Get Team Insights
```http
GET /api/memory/insights/team_789
```

Response:
```json
{
  "team_id": "team_789",
  "total_builds": 45,
  "success_rate": 89.5,
  "avg_quality": 82.3,
  "insights": [
    "Team success rate: 89.5%",
    "Average code quality: 82.3/100",
    "Most used workflow: standard (35 times)",
    "Speed improvement: +15.2%"
  ]
}
```

### Code Example

```python
from memory.team_memory import TeamMemory, BuildHistory
import uuid
from datetime import datetime

# Initialize team memory
memory = TeamMemory(memory_path="./memory")

# Record a build
build = BuildHistory(
    id=str(uuid.uuid4()),
    user_id="user_123",
    team_id="team_456",
    prompt="Build a real-time chat app",
    workflow="standard",
    tech_stack={
        "frontend": "React",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "realtime": "WebSockets"
    },
    success=True,
    quality_score=88.5,
    duration_seconds=180.0,
    files_generated=20,
    timestamp=datetime.utcnow().isoformat()
)

memory.record_build(build)

# Get stack suggestion
suggestion = memory.suggest_stack("Build a dashboard", "team_456")
print(f"Recommended: {suggestion['suggestion']}")
print(f"Reason: {suggestion['reason']}")

# Get insights
insights = memory.get_insights("team_456")
print(f"Success rate: {insights['success_rate']}%")
for insight in insights['insights']:
    print(f"  - {insight}")
```

## Observability Dashboard

### Purpose
Provide real-time monitoring of agent performance with metrics, success rates, and system health.

### Features
- **Agent Metrics**: Track executions, success/failure rates, duration, tokens used
- **Real-time Updates**: Live dashboard data
- **Quality Tracking**: Monitor code quality scores
- **System Summary**: Overall performance across all agents

### API Endpoint

#### Get Dashboard Data
```http
GET /api/dashboard
```

Response:
```json
{
  "agents": [
    {
      "agent_name": "Frontend Generation",
      "total_executions": 1250,
      "successful": 1180,
      "failed": 70,
      "success_rate": 94.4,
      "avg_duration_ms": 2350.5,
      "avg_tokens": 1520.3,
      "avg_quality_score": 84.7,
      "last_executed": "2024-01-15T10:30:00Z"
    }
  ],
  "summary": {
    "total_agents": 25,
    "total_executions": 15000,
    "overall_success_rate": 92.3,
    "overall_avg_duration_ms": 1850.2
  }
}
```

### Code Example

```python
from observability.dashboard import Dashboard

# Initialize dashboard
dashboard = Dashboard()

# Record agent executions
dashboard.record_execution(
    agent_name="Frontend Generation",
    success=True,
    duration_ms=2340.5,
    tokens=1523,
    quality_score=85.2
)

dashboard.record_execution(
    agent_name="Backend Generation",
    success=True,
    duration_ms=3120.8,
    tokens=2145,
    quality_score=88.7
)

# Get dashboard data
data = dashboard.get_dashboard_data()

print(f"Total Agents: {data['summary']['total_agents']}")
print(f"Overall Success Rate: {data['summary']['overall_success_rate']}%")

for agent in data['agents']:
    print(f"\n{agent['agent_name']}:")
    print(f"  Success Rate: {agent['success_rate']}%")
    print(f"  Avg Duration: {agent['avg_duration_ms']:.1f}ms")
    print(f"  Avg Quality: {agent['avg_quality_score']:.1f}/100")
```

## Self-Improvement System

### Purpose
Automatically optimize agent performance through A/B testing of prompt variants.

### Features
- **Prompt Variants**: Test multiple system prompts for each agent
- **Epsilon-Greedy Strategy**: Balance exploration (10%) and exploitation (90%)
- **Performance Tracking**: Monitor success rates, quality scores, and duration
- **Optimization Reports**: Identify best prompts and measure improvements

### API Endpoints

#### Get Optimization Report
```http
GET /api/optimization/report
```

Response:
```json
{
  "agents_optimized": 5,
  "improvements": [
    {
      "agent": "Frontend Generation",
      "baseline_score": 0.72,
      "best_score": 0.89,
      "improvement_percent": 23.6
    }
  ],
  "avg_improvement": 18.4
}
```

#### Get Best Prompts
```http
GET /api/optimization/best-prompts
```

Response:
```json
{
  "best_prompts": {
    "Frontend Generation": {
      "prompt": "You are an expert React developer...",
      "score": 0.89,
      "executions": 150,
      "success_rate": 95.3
    }
  }
}
```

### Code Example

```python
from optimization.self_improvement import SelfImprovement, PromptVariant

# Initialize self-improvement system
optimizer = SelfImprovement()

# Add prompt variants to test
variants = [
    PromptVariant(
        id="v1",
        agent_name="Frontend Generation",
        prompt="You are a frontend developer. Generate React code."
    ),
    PromptVariant(
        id="v2",
        agent_name="Frontend Generation",
        prompt="You are an expert React developer with 10+ years experience. Generate production-ready React code with TypeScript, following best practices."
    ),
    PromptVariant(
        id="v3",
        agent_name="Frontend Generation",
        prompt="You are a senior React engineer. Write clean, maintainable React code with hooks and modern patterns."
    )
]

for variant in variants:
    optimizer.add_variant("Frontend Generation", variant)

# During execution, get the prompt to use (epsilon-greedy)
selected_variant = optimizer.get_prompt("Frontend Generation")
print(f"Using variant: {selected_variant.id}")

# Record the result
optimizer.record_result(
    variant_id=selected_variant.id,
    success=True,
    quality_score=88.5,
    duration=2340.5
)

# After sufficient data, get the best prompts
best = optimizer.get_best_prompts()
print(f"Best prompt for Frontend Generation: {best['Frontend Generation'].prompt}")
print(f"Score: {best['Frontend Generation'].score:.3f}")

# Generate optimization report
report = optimizer.get_optimization_report()
print(f"Average improvement: {report['avg_improvement']:.1f}%")
```

## Integration with Existing System

### Integrating with Orchestration

To integrate these features with the existing orchestration system:

```python
from orchestration import run_orchestration_with_dag
from observability.dashboard import dashboard
from memory.team_memory import team_memory, BuildHistory
import time

async def run_build_with_enterprise_features(prompt, team_id, user_id):
    start_time = time.time()
    
    # Run the build
    result = await run_orchestration_with_dag(prompt)
    
    duration = time.time() - start_time
    
    # Record in team memory
    build = BuildHistory(
        id=result['build_id'],
        user_id=user_id,
        team_id=team_id,
        prompt=prompt,
        workflow=result['workflow'],
        tech_stack=result['tech_stack'],
        success=result['success'],
        quality_score=result.get('quality_score', 0),
        duration_seconds=duration,
        files_generated=len(result.get('files', [])),
        timestamp=datetime.utcnow().isoformat()
    )
    team_memory.record_build(build)
    
    # Record in dashboard (for each agent)
    for agent_name, agent_result in result.get('agent_results', {}).items():
        dashboard.record_execution(
            agent_name=agent_name,
            success=agent_result.get('success', False),
            duration_ms=agent_result.get('duration_ms', 0),
            tokens=agent_result.get('tokens', 0),
            quality_score=agent_result.get('quality', 0)
        )
    
    return result
```

## Testing

All features include comprehensive tests:

```bash
# Run enterprise features tests
cd backend
pytest tests/test_enterprise_features.py -v

# Test output:
# tests/test_enterprise_features.py::TestAgentMarketplace::test_publish_agent PASSED
# tests/test_enterprise_features.py::TestTeamMemory::test_record_build PASSED
# tests/test_enterprise_features.py::TestDashboard::test_record_execution PASSED
# tests/test_enterprise_features.py::TestSelfImprovement::test_add_variant PASSED
# ... (20 tests total)
```

## Storage

All enterprise features use file-based storage by default:

- **Marketplace**: `./marketplace/*.json` - One JSON file per agent
- **Team Memory**: `./memory/team_*.json` - One JSON file per team
- **Dashboard**: In-memory (can be persisted to database)
- **Self-Improvement**: In-memory (can be persisted to database)

## Architecture

```
backend/
├── agents/
│   ├── base_agent.py          # Abstract base class for all agents
│   └── registry.py            # Central agent registry
├── marketplace/
│   ├── __init__.py
│   └── agent_store.py         # Marketplace implementation
├── memory/
│   ├── __init__.py
│   └── team_memory.py         # Team learning system
├── observability/
│   ├── __init__.py
│   └── dashboard.py           # Real-time metrics
├── optimization/
│   ├── __init__.py
│   └── self_improvement.py    # A/B testing & optimization
└── tests/
    └── test_enterprise_features.py
```

## Future Enhancements

Potential improvements for Phase 5+:

1. **Marketplace**:
   - Agent versioning and updates
   - User reviews and comments
   - Paid agents with Stripe integration
   - Agent dependencies and auto-installation

2. **Team Memory**:
   - Machine learning for better predictions
   - Cross-team learning (with privacy)
   - Anomaly detection for failed builds
   - Automated recommendations

3. **Observability**:
   - Real-time WebSocket updates
   - Alerting for failures
   - Cost tracking and optimization
   - Performance trends and forecasting

4. **Self-Improvement**:
   - Multi-armed bandit algorithms
   - Contextual bandits (per project type)
   - Automated prompt generation with LLMs
   - Fine-tuning based on results

## License

These enterprise features are part of the CrucibAI platform and subject to the same license terms.
