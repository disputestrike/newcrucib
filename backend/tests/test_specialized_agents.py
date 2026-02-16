"""
Tests for all specialized agents - validation and registration.
"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import AgentValidationError
from agents.registry import AgentRegistry
from agents.planner_agent import PlannerAgent
from agents.stack_selector_agent import StackSelectorAgent
from agents.design_agent import DesignAgent
from agents.database_agent import DatabaseAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.test_generation_agent import TestGenerationAgent
from agents.security_agent import SecurityAgent
from agents.deployment_agent import DeploymentAgent
from agents.documentation_agent import DocumentationAgent


def test_all_agents_registered():
    """Test that all 10 agents are registered."""
    expected_agents = [
        "PlannerAgent",
        "StackSelectorAgent",
        "DesignAgent",
        "DatabaseAgent",
        "BackendAgent",
        "FrontendAgent",
        "TestGenerationAgent",
        "SecurityAgent",
        "DeploymentAgent",
        "DocumentationAgent",
    ]
    
    registered_agents = AgentRegistry.list_agents()
    
    for agent_name in expected_agents:
        assert agent_name in registered_agents, f"{agent_name} not registered"


@pytest.mark.parametrize("agent_class", [
    PlannerAgent,
    StackSelectorAgent,
    DesignAgent,
    DatabaseAgent,
    BackendAgent,
    FrontendAgent,
    TestGenerationAgent,
    SecurityAgent,
    DeploymentAgent,
    DocumentationAgent,
])
def test_agent_requires_user_prompt(agent_class):
    """Test that all agents require user_prompt in context."""
    agent = agent_class(llm_client=None, config={})
    
    with pytest.raises(AgentValidationError, match="Missing required field 'user_prompt'"):
        agent.validate_input({})


@pytest.mark.parametrize("agent_class", [
    PlannerAgent,
    StackSelectorAgent,
    DesignAgent,
    DatabaseAgent,
    BackendAgent,
    FrontendAgent,
    TestGenerationAgent,
    SecurityAgent,
    DeploymentAgent,
    DocumentationAgent,
])
def test_agent_accepts_valid_input(agent_class):
    """Test that all agents accept context with user_prompt."""
    agent = agent_class(llm_client=None, config={})
    
    # Should not raise
    assert agent.validate_input({"user_prompt": "Build a todo app"}) is True


def test_stack_selector_output_structure():
    """Test StackSelectorAgent output validation."""
    agent = StackSelectorAgent(llm_client=None, config={})
    
    valid_output = {
        "frontend": {
            "framework": "React",
            "language": "TypeScript",
            "styling": "TailwindCSS",
            "state_management": "Context",
            "reasoning": "React is popular"
        },
        "backend": {
            "framework": "FastAPI",
            "language": "Python",
            "reasoning": "FastAPI is modern"
        },
        "database": {
            "primary": "PostgreSQL",
            "caching": "Redis",
            "reasoning": "PostgreSQL is reliable"
        },
        "deployment": {
            "frontend": "Vercel",
            "backend": "Railway",
            "reasoning": "Easy deployment"
        },
        "additional_tools": ["Prisma", "Docker"],
        "overall_reasoning": "Modern stack for rapid development"
    }
    
    assert agent.validate_output(valid_output) is True


def test_database_agent_output_structure():
    """Test DatabaseAgent output validation."""
    agent = DatabaseAgent(llm_client=None, config={})
    
    valid_output = {
        "schema": {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "SERIAL PRIMARY KEY"}
                    ]
                }
            ],
            "relationships": []
        },
        "migrations": {
            "001_initial": "CREATE TABLE users (id SERIAL PRIMARY KEY);"
        },
        "orm_models": {
            "prisma_schema": "model User { id Int @id }"
        }
    }
    
    assert agent.validate_output(valid_output) is True


def test_frontend_agent_requires_package_json():
    """Test that FrontendAgent requires package.json in output."""
    agent = FrontendAgent(llm_client=None, config={})
    
    invalid_output = {
        "files": {
            "src/App.tsx": "code"
        },
        "structure": {
            "description": "test",
            "entry_point": "src/main.tsx",
            "main_components": ["App"]
        },
        "setup_instructions": ["npm install"]
    }
    
    with pytest.raises(AgentValidationError, match="Must include package.json"):
        agent.validate_output(invalid_output)


def test_frontend_agent_validates_package_json():
    """Test that FrontendAgent validates package.json is valid JSON."""
    agent = FrontendAgent(llm_client=None, config={})
    
    invalid_output = {
        "files": {
            "package.json": "not valid json {{"
        },
        "structure": {
            "description": "test",
            "entry_point": "src/main.tsx",
            "main_components": ["App"]
        },
        "setup_instructions": ["npm install"]
    }
    
    with pytest.raises(AgentValidationError, match="package.json must be valid JSON"):
        agent.validate_output(invalid_output)


def test_documentation_agent_requires_readme():
    """Test that DocumentationAgent requires README.md."""
    agent = DocumentationAgent(llm_client=None, config={})
    
    invalid_output = {
        "files": {
            "docs/API.md": "content"
        },
        "api_documentation": {
            "format": "OpenAPI 3.0",
            "content": "spec"
        },
        "architecture_diagram": "diagram",
        "setup_guide": "guide"
    }
    
    with pytest.raises(AgentValidationError, match="Must include README.md"):
        agent.validate_output(invalid_output)


def test_agent_registry_get_all():
    """Test getting all agents from registry."""
    all_agents = AgentRegistry.get_all_agents()
    
    assert len(all_agents) >= 10
    assert "PlannerAgent" in all_agents
    assert all_agents["PlannerAgent"] == PlannerAgent


def test_agent_registry_get_unknown_agent():
    """Test that registry raises error for unknown agent."""
    with pytest.raises(KeyError, match="not registered"):
        AgentRegistry.get_agent("NonExistentAgent")
