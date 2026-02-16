"""
Comprehensive integration tests for Orchestration V2
Tests workflow execution, validation, and quality scoring.
"""

import pytest
from backend.orchestration_v2 import OrchestrationV2, WorkflowPresets
from backend.agents.registry import AgentRegistry


@pytest.mark.asyncio
async def test_workflow_presets():
    """Test that all workflow presets return agent lists"""
    # Test full_stack
    agents = WorkflowPresets.get_workflow("full_stack")
    assert len(agents) == 10
    assert "PlannerAgent" in agents
    assert "FrontendAgent" in agents
    assert "BackendAgent" in agents
    
    # Test frontend_only
    agents = WorkflowPresets.get_workflow("frontend_only")
    assert len(agents) == 7
    assert "FrontendAgent" in agents
    assert "BackendAgent" not in agents
    
    # Test backend_api
    agents = WorkflowPresets.get_workflow("backend_api")
    assert "BackendAgent" in agents
    assert "FrontendAgent" not in agents
    
    # Test landing_page
    agents = WorkflowPresets.get_workflow("landing_page")
    assert len(agents) == 4
    assert "DesignAgent" in agents


@pytest.mark.asyncio
async def test_agent_registry():
    """Test agent registration and listing"""
    # List all agents
    agents = AgentRegistry.list_agents()
    assert len(agents) > 0
    assert any(a["name"] == "PlannerAgent" for a in agents)
    
    # Get agent names
    names = AgentRegistry.get_agent_names()
    assert "PlannerAgent" in names
    assert "FrontendAgent" in names
    
    # Create instance
    agent = AgentRegistry.create_instance("PlannerAgent", None, {})
    assert agent is not None
    assert agent.metrics["agent_name"] == "PlannerAgent"


@pytest.mark.asyncio
async def test_simple_workflow():
    """Test simple workflow execution (landing page)"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    result = await orchestrator.execute_workflow(
        user_prompt="Build a simple todo app",
        workflow=WorkflowPresets.LANDING_PAGE,
        validate_code=False,  # Skip validation in tests
        run_tests=False,
        score_quality=False
    )
    
    # Check result structure
    assert "success" in result
    assert "results" in result
    assert "metrics" in result
    assert "summary" in result
    
    # Check agents ran
    assert "PlannerAgent" in result["results"]
    assert "DesignAgent" in result["results"]
    assert "FrontendAgent" in result["results"]
    
    # Check metrics
    assert len(result["metrics"]["agents"]) > 0
    assert result["metrics"]["tokens"]["total"] >= 0


@pytest.mark.asyncio
async def test_full_workflow_no_validation():
    """Test complete workflow execution without validation"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    result = await orchestrator.execute_workflow(
        user_prompt="Build a todo app with React and FastAPI",
        workflow="full_stack",
        validate_code=False,
        run_tests=False,
        score_quality=False
    )
    
    assert result["success"]
    assert "PlannerAgent" in result["results"]
    assert "FrontendAgent" in result["results"]
    assert "BackendAgent" in result["results"]
    
    # Check summary
    summary = result["summary"]
    assert summary["project_type"] == "Full-stack web application"
    assert summary["files_generated"] > 0


@pytest.mark.asyncio
async def test_workflow_with_validation():
    """Test workflow with validation enabled"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    result = await orchestrator.execute_workflow(
        user_prompt="Build a simple frontend app",
        workflow="frontend_only",
        validate_code=True,
        run_tests=False,
        score_quality=False
    )
    
    # Check validation results exist
    assert "validations" in result
    if "FrontendAgent" in result["results"]:
        # Frontend validation should have been attempted
        assert "frontend" in result["validations"] or not result["results"]["FrontendAgent"].get("files")


@pytest.mark.asyncio
async def test_workflow_with_quality_scoring():
    """Test workflow with quality scoring enabled"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    result = await orchestrator.execute_workflow(
        user_prompt="Build a backend API",
        workflow="backend_api",
        validate_code=False,
        run_tests=False,
        score_quality=True
    )
    
    # Check quality scoring results
    assert "validations" in result
    quality = result["validations"].get("quality")
    
    # Should have quality results if code was generated
    if quality and not quality.get("skipped"):
        assert "overall_score" in quality
        assert "metrics" in quality


@pytest.mark.asyncio
async def test_parallel_execution():
    """Test parallel agent execution"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    # Test executing multiple independent agents in parallel
    context = {"user_prompt": "Build an app"}
    result = await orchestrator.execute_parallel_agents(
        ["DesignAgent", "DocumentationAgent"],
        context
    )
    
    assert "DesignAgent" in result
    assert "DocumentationAgent" in result
    assert not isinstance(result["DesignAgent"], Exception)


@pytest.mark.asyncio
async def test_metrics_aggregation():
    """Test that metrics are properly aggregated"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    result = await orchestrator.execute_workflow(
        user_prompt="Test metrics",
        workflow=["PlannerAgent", "DesignAgent"],
        validate_code=False,
        run_tests=False,
        score_quality=False
    )
    
    metrics = result["metrics"]
    
    # Check structure
    assert "agents" in metrics
    assert "tokens" in metrics
    assert "timing" in metrics
    
    # Check tokens
    assert "total" in metrics["tokens"]
    assert "by_agent" in metrics["tokens"]
    
    # Check timing
    assert "total_seconds" in metrics["timing"]
    assert "by_agent_ms" in metrics["timing"]
    
    # Verify counts
    assert len(metrics["agents"]) == 2


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in workflow"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    # Try with invalid agent name
    try:
        result = await orchestrator.execute_workflow(
            user_prompt="Test",
            workflow=["InvalidAgent"],
            validate_code=False,
            run_tests=False,
            score_quality=False
        )
        
        # Should handle error gracefully
        assert not result["success"]
        assert "InvalidAgent" in result["results"]
        assert "error" in result["results"]["InvalidAgent"]
    except Exception as e:
        # If it throws, that's also acceptable
        assert "InvalidAgent" in str(e)


@pytest.mark.asyncio
async def test_summary_generation():
    """Test summary generation with different project types"""
    orchestrator = OrchestrationV2(llm_client=None, config={})
    
    # Test frontend-only
    result = await orchestrator.execute_workflow(
        user_prompt="Build a landing page",
        workflow="frontend_only",
        validate_code=False,
        run_tests=False,
        score_quality=False
    )
    
    summary = result["summary"]
    assert summary["project_type"] == "Frontend application"
    
    # Test backend-only
    result = await orchestrator.execute_workflow(
        user_prompt="Build an API",
        workflow="backend_api",
        validate_code=False,
        run_tests=False,
        score_quality=False
    )
    
    summary = result["summary"]
    assert summary["project_type"] == "Backend API"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
