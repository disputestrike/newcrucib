"""
Integration test to verify specialized agents work end-to-end.
This test verifies agents can be instantiated and their basic flow works.
"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.registry import AgentRegistry


def test_registry_has_all_agents():
    """Verify all 10 agents are registered."""
    agents = AgentRegistry.list_agents()
    
    expected = [
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
    
    assert len(agents) >= 10, f"Expected at least 10 agents, got {len(agents)}"
    
    for agent_name in expected:
        assert agent_name in agents, f"{agent_name} not found in registry"


def test_can_instantiate_all_agents():
    """Test that all agents can be instantiated."""
    for agent_name, agent_class in AgentRegistry.get_all_agents().items():
        # Should not raise
        agent = agent_class(llm_client=None, config={})
        assert agent is not None
        assert agent.name == agent_name


def test_agent_chain_context():
    """Test that agents can pass context to each other."""
    # This simulates how agents would be chained together
    planner_output = {
        "project_summary": "Build a todo app",
        "estimated_duration": "2-3 hours",
        "complexity": "medium",
        "tasks": [
            {
                "id": 1,
                "title": "Select stack",
                "description": "Choose technologies",
                "agent": "StackSelectorAgent",
                "dependencies": [],
                "estimated_complexity": "low"
            },
            {
                "id": 2,
                "title": "Design database",
                "description": "Create schema",
                "agent": "DatabaseAgent",
                "dependencies": [1],
                "estimated_complexity": "medium"
            }
        ]
    }
    
    stack_output = {
        "frontend": {
            "framework": "React",
            "language": "TypeScript",
            "styling": "TailwindCSS",
            "state_management": "Context",
            "reasoning": "Modern and popular"
        },
        "backend": {
            "framework": "FastAPI",
            "language": "Python",
            "reasoning": "Fast and easy"
        },
        "database": {
            "primary": "PostgreSQL",
            "caching": "Redis",
            "reasoning": "Reliable"
        },
        "deployment": {
            "frontend": "Vercel",
            "backend": "Railway",
            "reasoning": "Easy"
        },
        "additional_tools": ["Docker"],
        "overall_reasoning": "Modern stack"
    }
    
    # Test that DatabaseAgent can accept stack context
    DatabaseAgent = AgentRegistry.get_agent("DatabaseAgent")
    db_agent = DatabaseAgent(llm_client=None, config={})
    
    context = {
        "user_prompt": "Build a todo app",
        "planner_output": planner_output,
        "stack_output": stack_output
    }
    
    # Should not raise
    assert db_agent.validate_input(context) is True


def test_all_agents_have_docstrings():
    """Verify all agents have documentation."""
    for agent_name, agent_class in AgentRegistry.get_all_agents().items():
        assert agent_class.__doc__ is not None, f"{agent_name} missing docstring"
        assert len(agent_class.__doc__.strip()) > 0, f"{agent_name} has empty docstring"


def test_agent_metadata():
    """Test that agents have proper metadata."""
    for agent_name, agent_class in AgentRegistry.get_all_agents().items():
        agent = agent_class(llm_client=None, config={})
        
        # Check name
        assert hasattr(agent, 'name')
        assert agent.name == agent_name
        
        # Check methods exist
        assert hasattr(agent, 'validate_input')
        assert hasattr(agent, 'validate_output')
        assert hasattr(agent, 'execute')
        assert hasattr(agent, 'run')
        assert hasattr(agent, 'call_llm')
        assert hasattr(agent, 'parse_json_response')


if __name__ == "__main__":
    # Run basic smoke test
    print("Running agent integration smoke test...")
    test_registry_has_all_agents()
    print("✓ All agents registered")
    
    test_can_instantiate_all_agents()
    print("✓ All agents can be instantiated")
    
    test_agent_chain_context()
    print("✓ Agents can receive chained context")
    
    test_all_agents_have_docstrings()
    print("✓ All agents have documentation")
    
    test_agent_metadata()
    print("✓ All agents have required methods")
    
    print("\n✅ All integration tests passed!")
