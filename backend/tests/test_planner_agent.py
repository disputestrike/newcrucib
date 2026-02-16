"""
Tests for PlannerAgent.
"""
import pytest
import json
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner_agent import PlannerAgent
from agents.base_agent import AgentValidationError


@pytest.mark.asyncio
async def test_planner_agent_validation_missing_user_prompt():
    """Test that PlannerAgent raises error when user_prompt is missing."""
    agent = PlannerAgent(llm_client=None, config={})
    
    with pytest.raises(AgentValidationError, match="Missing required field 'user_prompt'"):
        await agent.run({})


@pytest.mark.asyncio
async def test_planner_agent_validation_short_prompt():
    """Test that PlannerAgent raises error when user_prompt is too short."""
    agent = PlannerAgent(llm_client=None, config={})
    
    with pytest.raises(AgentValidationError, match="must be a string with >10 characters"):
        await agent.run({"user_prompt": "short"})


@pytest.mark.asyncio
async def test_planner_agent_output_validation():
    """Test that PlannerAgent validates output structure correctly."""
    agent = PlannerAgent(llm_client=None, config={})
    
    # Test missing required fields
    with pytest.raises(AgentValidationError, match="Missing required field"):
        agent.validate_output({"project_summary": "test"})
    
    # Test invalid complexity
    with pytest.raises(AgentValidationError, match="complexity must be"):
        agent.validate_output({
            "project_summary": "test",
            "estimated_duration": "2 hours",
            "complexity": "invalid",
            "tasks": []
        })
    
    # Test too few tasks
    with pytest.raises(AgentValidationError, match="Must generate 5-15 tasks"):
        agent.validate_output({
            "project_summary": "test",
            "estimated_duration": "2 hours",
            "complexity": "low",
            "tasks": []
        })


@pytest.mark.asyncio
async def test_planner_agent_valid_output():
    """Test that PlannerAgent accepts valid output."""
    agent = PlannerAgent(llm_client=None, config={})
    
    valid_output = {
        "project_summary": "Build a todo app with authentication",
        "estimated_duration": "2-3 hours",
        "complexity": "medium",
        "tasks": [
            {
                "id": 1,
                "title": "Select technology stack",
                "description": "Choose React and FastAPI",
                "agent": "StackSelectorAgent",
                "dependencies": [],
                "estimated_complexity": "low"
            },
            {
                "id": 2,
                "title": "Design database schema",
                "description": "Create schema for users and todos",
                "agent": "DatabaseAgent",
                "dependencies": [1],
                "estimated_complexity": "medium"
            },
            {
                "id": 3,
                "title": "Implement backend API",
                "description": "Build REST API with FastAPI",
                "agent": "BackendAgent",
                "dependencies": [2],
                "estimated_complexity": "high"
            },
            {
                "id": 4,
                "title": "Build frontend",
                "description": "Create React components",
                "agent": "FrontendAgent",
                "dependencies": [1],
                "estimated_complexity": "medium"
            },
            {
                "id": 5,
                "title": "Write tests",
                "description": "Unit and integration tests",
                "agent": "TestGenerationAgent",
                "dependencies": [3, 4],
                "estimated_complexity": "medium"
            }
        ]
    }
    
    # Should not raise
    assert agent.validate_output(valid_output) is True


def test_planner_agent_registry():
    """Test that PlannerAgent is registered in the registry."""
    from agents.registry import AgentRegistry
    
    assert "PlannerAgent" in AgentRegistry.list_agents()
    assert AgentRegistry.get_agent("PlannerAgent") == PlannerAgent
