# Phase 4: Enterprise Features Documentation

## Overview

Phase 4 introduces four enterprise-grade features that enable CrucibAI to achieve a 10/10 rating through unique competitive advantages:

1. **Agent Marketplace** - Create, share, and install custom agents
2. **Team Memory System** - Learn from past builds and suggest improvements
3. **Observability Dashboard** - Real-time agent performance monitoring
4. **Self-Improvement System** - A/B test and optimize agent prompts

---

## 1. Agent Marketplace

### Purpose
The Agent Marketplace allows users to create custom agents with specific capabilities, share them with the community, and install agents created by others.

### Features
- Create custom agents with custom system prompts
- Search and discover agents by query or category
- Install agents for use in your projects
- Rate and review agents
- Track download statistics

### API Endpoints

#### Create Agent
```http
POST /api/marketplace/create-agent
Content-Type: application/json

{
  "name": "Frontend Builder",
  "description": "Specialized agent for building React components",
  "author": "user@example.com",
  "category": "frontend",
  "system_prompt": "You are an expert React developer...",
  "input_schema": {"type": "object"},
  "output_schema": {"type": "object"}
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "uuid-here"
}
```

#### Search Agents
```http
GET /api/marketplace/search?query=frontend&category=frontend&min_rating=4.0
```

**Response:**
```json
{
  "agents": [
    {
      "id": "uuid",
      "name": "Frontend Builder",
      "description": "Specialized agent...",
      "author": "user@example.com",
      "category": "frontend",
      "downloads": 150,
      "rating": 4.5,
      "version": "1.0.0"
    }
  ]
}
```

#### Install Agent
```http
POST /api/marketplace/install/{agent_id}?user_id=user123
```

**Response:**
```json
{
  "success": true,
  "agent_name": "Frontend Builder",
  "message": "Agent 'Frontend Builder' installed successfully"
}
```

#### Rate Agent
```http
POST /api/marketplace/rate/{agent_id}?rating=4.5&user_id=user123
```

**Response:**
```json
{
  "success": true,
  "new_rating": 4.25
}
```

---

## 2. Team Memory System

### Purpose
Team Memory learns from your build history to provide personalized insights, tech stack suggestions, and improvement recommendations.

### Features
- Track all builds with metadata (tech stack, quality, duration, agents used)
- Generate team insights and analytics
- Suggest tech stacks based on similar past builds
- Provide improvement recommendations
- Track quality trends over time

### API Endpoints

#### Get Team Insights
```http
GET /api/team/insights/{team_id}
```

**Response:**
```json
{
  "total_builds": 50,
  "successful_builds": 45,
  "success_rate": 90.0,
  "avg_quality_score": 82.5,
  "quality_trend": [80, 82, 85, 83, 84],
  "preferred_tech": {
    "frontend": [["React", 30], ["Vue", 10], ["Angular", 5]],
    "backend": [["FastAPI", 25], ["Express", 15], ["Django", 5]]
  },
  "most_used_agents": [
    ["Frontend Generation", 45],
    ["Backend Generation", 43],
    ["Test Generation", 38]
  ],
  "avg_build_time": 125.5
}
```

#### Suggest Tech Stack
```http
POST /api/team/suggest-stack/{team_id}?prompt=Build+a+web+application
```

**Response:**
```json
{
  "suggestion": "learned",
  "tech_stack": {
    "frontend": {"framework": "React"},
    "backend": {"framework": "FastAPI"}
  },
  "reason": "Based on 12 similar builds",
  "success_rate": 91.7
}
```

#### Get Recommendations
```http
GET /api/team/recommendations/{team_id}
```

**Response:**
```json
{
  "recommendations": [
    "Recent builds have lower quality scores. Consider code review.",
    "Build times are high. Consider simpler workflows."
  ]
}
```

---

## 3. Observability Dashboard

### Purpose
Real-time monitoring of agent performance, success rates, token usage, and bottleneck identification.

### Features
- Track execution times for all agents
- Monitor success/failure rates
- Analyze token usage per agent
- Identify performance bottlenecks
- Generate optimization recommendations

### API Endpoints

#### Get Dashboard Data
```http
GET /api/dashboard/agents?hours=24
```

**Response:**
```json
{
  "time_range_hours": 24,
  "overall": {
    "total_executions": 150,
    "success_rate": 94.7,
    "total_tokens": 125000,
    "avg_duration_ms": 2500
  },
  "by_agent": {
    "Frontend Generation": {
      "executions": 50,
      "success_rate": 96.0,
      "avg_duration_ms": 3500,
      "avg_tokens": 1200,
      "total_tokens": 60000,
      "failures": 2,
      "common_errors": []
    },
    "Backend Generation": {
      "executions": 48,
      "success_rate": 95.8,
      "avg_duration_ms": 3200,
      "avg_tokens": 1100,
      "total_tokens": 52800,
      "failures": 2,
      "common_errors": []
    }
  },
  "bottlenecks": [
    {"agent": "Frontend Generation", "avg_duration_ms": 3500},
    {"agent": "Backend Generation", "avg_duration_ms": 3200}
  ],
  "recommendations": [
    "All agents performing well!"
  ]
}
```

---

## 4. Self-Improvement System

### Purpose
Automatically A/B test different agent prompts, learn which variants perform best, and continuously improve agent quality.

### Features
- Create prompt variants for A/B testing
- Epsilon-greedy selection (90% exploitation, 10% exploration)
- Track quality, duration, and success rate per variant
- Identify best performing variants
- Generate improvement reports

### API Endpoints

#### Create Prompt Variant
```http
POST /api/improve/test-variant?agent_name=Frontend+Generation&variant_prompt=Improved+prompt&variant_name=v2
```

**Response:**
```json
{
  "variant_id": "uuid-here"
}
```

#### Get Improvement Report
```http
GET /api/improve/report/{agent_name}
```

**Response:**
```json
{
  "agent_name": "Frontend Generation",
  "best_variant": {
    "variant_id": "uuid",
    "executions": 60,
    "avg_quality": 87.5,
    "success_rate": 95.0,
    "avg_duration_s": 3.2
  },
  "variants_tested": 3,
  "total_executions": 150,
  "recommendation": "Deploy best variant to production"
}
```

---

## Usage Examples

### Python Example: Using the Modules Directly

```python
from marketplace.agent_marketplace import AgentMarketplace
from learning.team_memory import TeamMemory
from observability.agent_dashboard import AgentDashboard
from learning.self_improvement import SelfImprovement

# Initialize systems
marketplace = AgentMarketplace()
team_memory = TeamMemory()
dashboard = AgentDashboard()
self_improvement = SelfImprovement()

# Create and install an agent
agent = marketplace.create_agent(
    name="Custom Agent",
    description="My custom agent",
    author="me@example.com",
    category="frontend",
    system_prompt="You are helpful",
    input_schema={},
    output_schema={}
)
marketplace.install_agent(agent.id, "user123")

# Record a build
result = {
    "prompt": "Build todo app",
    "workflow": "fullstack",
    "success": True,
    "summary": {"tech_stack": {"frontend": {"framework": "React"}}},
    "validations": {"quality": {"overall_score": 85}},
    "metrics": {"timing": {"total_seconds": 120}},
    "results": {}
}
team_memory.record_build("build-1", "user-1", "team-1", result)

# Get insights
insights = team_memory.get_team_insights("team-1")
print(f"Total builds: {insights['total_builds']}")

# Record agent execution
dashboard.record_execution({
    "agent_name": "TestAgent",
    "duration_ms": 1500,
    "tokens_used": 500,
    "success": True
})

# Create A/B test variant
variant = self_improvement.create_prompt_variant(
    agent_name="TestAgent",
    variant_prompt="Improved prompt"
)
```

---

## Storage

All enterprise features use local file-based storage by default:

- **Marketplace**: `./marketplace_agents/` - Stores agent definitions as JSON files
- **Team Memory**: `./team_memory/memories.json` - Stores build history
- **Dashboard**: In-memory (can be extended to persist)
- **Self-Improvement**: In-memory (can be extended to persist)

### Custom Storage Paths

```python
marketplace = AgentMarketplace(storage_path="/custom/path/agents")
team_memory = TeamMemory(storage_path="/custom/path/memory")
```

---

## Testing

### Run Unit Tests
```bash
cd /home/runner/work/newcrucib/newcrucib
python -m pytest backend/tests/test_enterprise_features.py -v
```

### Manual Verification
```bash
cd /home/runner/work/newcrucib/newcrucib/backend
python verify_enterprise_features.py
```

---

## Future Enhancements

1. **Marketplace**
   - User authentication and ownership
   - Agent reviews and comments
   - Version management and updates
   - Private/public agents

2. **Team Memory**
   - Database backend for scaling
   - Cross-team learning
   - Predictive analytics
   - Cost optimization tracking

3. **Dashboard**
   - Real-time WebSocket updates
   - Custom alerts and notifications
   - Historical data analysis
   - Export capabilities

4. **Self-Improvement**
   - Multi-armed bandit algorithms
   - Bayesian optimization
   - Automated prompt engineering
   - Cost-quality tradeoff optimization

---

## Security Considerations

1. **Input Validation**: All API endpoints validate input parameters
2. **User Authentication**: Endpoints should be protected with authentication (implementation needed)
3. **Rate Limiting**: Consider rate limiting for marketplace operations
4. **Storage Security**: Ensure storage directories have appropriate permissions
5. **Prompt Injection**: Validate system prompts to prevent injection attacks

---

## Performance Considerations

1. **Caching**: Consider caching frequently accessed agents and insights
2. **Pagination**: Implement pagination for large result sets
3. **Indexing**: Add search indexes for marketplace queries
4. **Async Operations**: Use async/await for I/O operations
5. **Cleanup**: Implement cleanup for old metrics and memories

---

## Support

For issues or questions about Phase 4 Enterprise Features:
1. Check the test files for usage examples
2. Run the verification script to test functionality
3. Review the API documentation above
4. Check server logs for errors

---

## License

Copyright © 2024 CrucibAI. All rights reserved.
