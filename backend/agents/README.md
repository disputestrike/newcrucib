# Agent System for Newcrucib V2

This directory contains the base agent infrastructure for Newcrucib V2, providing a foundational architecture that all specialized agents inherit from.

## Overview

The agent system provides:
- **Abstract base class** with validation, metrics tracking, and LLM integration
- **Registry pattern** for managing and instantiating agents
- **Consistent error handling** with custom validation errors
- **Async execution** support throughout
- **Integration** with existing LLM router from server.py

## Components

### BaseAgent (`base_agent.py`)

Abstract base class providing:
- Input/output validation with `validate_input()` and `validate_output()`
- Metrics tracking via `AgentMetrics` dataclass
- Main execution via `execute()` (must be implemented by subclasses)
- Complete workflow via `run()` wrapper
- LLM integration helper via `call_llm()`

#### Example Usage

```python
from agents import BaseAgent, AgentValidationError, AgentRegistry

@AgentRegistry.register("my_agent")
class MyAgent(BaseAgent):
    """Custom agent implementation."""
    
    def validate_input(self, input_data):
        """Validate input data."""
        super().validate_input(input_data)
        if "required_field" not in input_data:
            raise AgentValidationError("Missing required_field")
    
    async def execute(self, input_data):
        """Main agent logic."""
        # Use LLM if needed
        prompt = f"Process: {input_data['required_field']}"
        result = await self.call_llm(
            prompt=prompt,
            system="You are a helpful assistant."
        )
        
        return {"result": result}
    
    def validate_output(self, output_data):
        """Validate output data."""
        super().validate_output(output_data)
        if "result" not in output_data:
            raise AgentValidationError("Missing result field")

# Create and run agent
agent = AgentRegistry.create_instance("my_agent")
result = await agent.run({"required_field": "value"})

# Get metrics
metrics = agent.get_metrics()
print(f"Execution time: {metrics.execution_time}s")
print(f"Tokens used: {metrics.tokens_used}")
print(f"Success: {metrics.success}")
```

### AgentRegistry (`registry.py`)

Registry for managing agent classes:
- `@AgentRegistry.register(name)` - Decorator to register agents
- `AgentRegistry.get(name)` - Retrieve agent class
- `AgentRegistry.create_instance(name, **kwargs)` - Factory method
- `AgentRegistry.list_agents()` - List all registered agents

### AgentMetrics

Dataclass tracking execution metrics:
- `agent_name` - Name of the agent
- `execution_time` - Time taken in seconds
- `tokens_used` - Total tokens consumed
- `success` - Whether execution succeeded
- `error_message` - Error details if failed
- `started_at` / `completed_at` - Timestamps
- `llm_calls` - Number of LLM calls made
- `additional_metrics` - Custom metrics dict

### AgentValidationError

Custom exception for validation failures:
- Inherits from `CrucibError`
- Status code: 400
- Severity: MEDIUM
- Recoverable: True

## Testing

Comprehensive test suite in `tests/test_base_agent.py`:
- 24 tests covering all functionality
- 81% coverage for `base_agent.py`
- 100% coverage for `registry.py`

Run tests:
```bash
cd backend
python -m pytest tests/test_base_agent.py -v
```

Run with coverage:
```bash
python -m pytest tests/test_base_agent.py --cov=agents --cov-report=term-missing
```

## Code Quality

All code passes:
- ✅ flake8 linting (max line length: 120)
- ✅ mypy type checking
- ✅ CodeQL security scanning (0 vulnerabilities)

## Design Decisions

1. **Async-first**: All methods are async to match existing FastAPI patterns
2. **Type hints**: Full type annotations using Pydantic and typing module
3. **LLM Integration**: Uses existing `_call_llm_with_fallback` from server.py
4. **Error handling**: Inherits from existing `CrucibError` hierarchy
5. **Testing**: Follows pytest-asyncio patterns from existing tests

## Next Steps

Specialized agents can now be built on top of this infrastructure:
1. Create agent class inheriting from `BaseAgent`
2. Register with `@AgentRegistry.register(name)` decorator
3. Implement `execute()` method
4. Override `validate_input()` and `validate_output()` as needed
5. Use `call_llm()` helper for LLM interactions
