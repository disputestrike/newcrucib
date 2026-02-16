"""
Tests for base agent infrastructure.
Tests validation, metrics tracking, error handling, and registry functionality.
"""

import pytest
from typing import Dict, Any
from datetime import datetime

from agents import BaseAgent, AgentValidationError, AgentMetrics, AgentRegistry


# Test agent implementations for testing
class SimpleAgent(BaseAgent):
    """Simple test agent that returns input with a prefix."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "output": f"processed: {input_data.get('input', '')}",
            "status": "success"
        }


class ValidationAgent(BaseAgent):
    """Agent with custom validation logic."""

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        super().validate_input(input_data)
        if "required_field" not in input_data:
            raise AgentValidationError(
                "Missing required_field",
                details={"field": "required_field"}
            )

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        super().validate_output(output_data)
        if "result" not in output_data:
            raise AgentValidationError(
                "Missing result field",
                details={"field": "result"}
            )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": "validated"}


class FailingAgent(BaseAgent):
    """Agent that always fails during execution."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("Simulated failure")


class LLMAgent(BaseAgent):
    """Agent that uses LLM calls."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Mock LLM call for testing
        # We'll mock the actual call in tests
        return {"response": "mock response"}


# Fixtures
@pytest.fixture
def simple_agent():
    """Fixture for simple test agent."""
    return SimpleAgent()


@pytest.fixture
def validation_agent():
    """Fixture for validation test agent."""
    return ValidationAgent()


@pytest.fixture
def failing_agent():
    """Fixture for failing test agent."""
    return FailingAgent()


@pytest.fixture
def llm_agent():
    """Fixture for LLM test agent."""
    return LLMAgent()


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear registry before each test."""
    AgentRegistry.clear()
    yield
    AgentRegistry.clear()


# Test AgentMetrics
class TestAgentMetrics:
    """Tests for AgentMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating metrics object."""
        metrics = AgentMetrics(agent_name="test_agent")
        assert metrics.agent_name == "test_agent"
        assert metrics.execution_time == 0.0
        assert metrics.tokens_used == 0
        assert metrics.success is False
        assert metrics.error_message is None
        assert metrics.llm_calls == 0
        assert metrics.additional_metrics == {}

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = AgentMetrics(
            agent_name="test_agent",
            execution_time=1.5,
            tokens_used=100,
            success=True,
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )
        result = metrics.to_dict()

        assert result["agent_name"] == "test_agent"
        assert result["execution_time"] == 1.5
        assert result["tokens_used"] == 100
        assert result["success"] is True
        assert isinstance(result["started_at"], str)
        assert isinstance(result["completed_at"], str)


# Test AgentValidationError
class TestAgentValidationError:
    """Tests for AgentValidationError exception."""

    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = AgentValidationError("Test error")
        assert error.message == "Test error"
        assert error.error_code == "AGENT_VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.recoverable is True

    def test_validation_error_with_details(self):
        """Test validation error with details."""
        details = {"field": "test_field", "value": "invalid"}
        error = AgentValidationError("Test error", details=details)
        assert error.details == details


# Test BaseAgent
class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_cannot_instantiate_base_agent(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent()

    @pytest.mark.asyncio
    async def test_simple_agent_execution(self, simple_agent):
        """Test basic agent execution."""
        input_data = {"input": "test"}
        result = await simple_agent.run(input_data)

        assert result["output"] == "processed: test"
        assert result["status"] == "success"

        metrics = simple_agent.get_metrics()
        assert metrics.success is True
        assert metrics.execution_time > 0
        assert metrics.started_at is not None
        assert metrics.completed_at is not None

    @pytest.mark.asyncio
    async def test_input_validation(self, validation_agent):
        """Test input validation."""
        # Should fail without required field
        with pytest.raises(AgentValidationError) as exc_info:
            await validation_agent.run({"other_field": "value"})

        assert "required_field" in str(exc_info.value)

        # Should succeed with required field
        result = await validation_agent.run({"required_field": "value"})
        assert result["result"] == "validated"

    @pytest.mark.asyncio
    async def test_output_validation(self, simple_agent):
        """Test output validation."""
        # Override execute to return invalid output
        original_execute = simple_agent.execute

        async def bad_execute(input_data):
            return "not a dict"  # Invalid output

        simple_agent.execute = bad_execute

        with pytest.raises(AgentValidationError) as exc_info:
            await simple_agent.run({"input": "test"})

        assert "must be a dictionary" in str(exc_info.value)

        # Restore original
        simple_agent.execute = original_execute

    @pytest.mark.asyncio
    async def test_agent_failure_handling(self, failing_agent):
        """Test handling of execution failures."""
        with pytest.raises(RuntimeError) as exc_info:
            await failing_agent.run({"input": "test"})

        assert "Simulated failure" in str(exc_info.value)

        metrics = failing_agent.get_metrics()
        assert metrics.success is False
        assert metrics.error_message == "Simulated failure"
        assert metrics.execution_time > 0

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, simple_agent):
        """Test that metrics are tracked correctly."""
        await simple_agent.run({"input": "test"})

        metrics = simple_agent.get_metrics()
        assert metrics.agent_name == "SimpleAgent"
        assert metrics.execution_time > 0
        assert metrics.success is True
        assert metrics.error_message is None
        assert metrics.started_at is not None
        assert metrics.completed_at is not None
        assert metrics.started_at <= metrics.completed_at

    @pytest.mark.asyncio
    async def test_multiple_runs(self, simple_agent):
        """Test multiple sequential runs."""
        # First run
        result1 = await simple_agent.run({"input": "test1"})
        metrics1 = simple_agent.get_metrics()

        # Second run should reset metrics
        result2 = await simple_agent.run({"input": "test2"})
        metrics2 = simple_agent.get_metrics()

        assert result1["output"] == "processed: test1"
        assert result2["output"] == "processed: test2"
        assert metrics1.started_at != metrics2.started_at


# Test AgentRegistry
class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def test_register_agent(self):
        """Test registering an agent."""
        @AgentRegistry.register("test_agent")
        class TestAgent(BaseAgent):
            async def execute(self, input_data):
                return {"result": "ok"}

        assert AgentRegistry.is_registered("test_agent")
        assert "test_agent" in AgentRegistry.list_agents()

    def test_register_non_agent_class(self):
        """Test that non-agent classes cannot be registered."""
        with pytest.raises(TypeError):
            @AgentRegistry.register("bad_agent")
            class NotAnAgent:
                pass

    def test_get_agent(self):
        """Test retrieving agent class."""
        @AgentRegistry.register("test_agent")
        class TestAgent(BaseAgent):
            async def execute(self, input_data):
                return {"result": "ok"}

        agent_class = AgentRegistry.get("test_agent")
        assert agent_class == TestAgent

    def test_get_nonexistent_agent(self):
        """Test getting agent that doesn't exist."""
        with pytest.raises(KeyError) as exc_info:
            AgentRegistry.get("nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_list_agents(self):
        """Test listing all agents."""
        @AgentRegistry.register("agent1")
        class Agent1(BaseAgent):
            async def execute(self, input_data):
                return {}

        @AgentRegistry.register("agent2")
        class Agent2(BaseAgent):
            async def execute(self, input_data):
                return {}

        agents = AgentRegistry.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents

    def test_create_instance(self):
        """Test factory method for creating instances."""
        @AgentRegistry.register("test_agent")
        class TestAgent(BaseAgent):
            async def execute(self, input_data):
                return {"result": "ok"}

        agent = AgentRegistry.create_instance("test_agent")
        assert isinstance(agent, TestAgent)
        assert isinstance(agent, BaseAgent)

    def test_create_instance_with_args(self):
        """Test factory method with custom arguments."""
        @AgentRegistry.register("named_agent")
        class NamedAgent(BaseAgent):
            async def execute(self, input_data):
                return {"result": "ok"}

        agent = AgentRegistry.create_instance("named_agent", name="CustomName")
        assert agent.name == "CustomName"

    @pytest.mark.asyncio
    async def test_registered_agent_execution(self):
        """Test that registered agents can be executed."""
        @AgentRegistry.register("executable_agent")
        class ExecutableAgent(BaseAgent):
            async def execute(self, input_data):
                return {"result": input_data.get("value", "") + "_processed"}

        agent = AgentRegistry.create_instance("executable_agent")
        result = await agent.run({"value": "test"})

        assert result["result"] == "test_processed"

    def test_register_overwrites_warning(self):
        """Test that re-registering an agent logs a warning."""
        @AgentRegistry.register("duplicate")
        class Agent1(BaseAgent):
            async def execute(self, input_data):
                return {"v": 1}

        @AgentRegistry.register("duplicate")
        class Agent2(BaseAgent):
            async def execute(self, input_data):
                return {"v": 2}

        # Second registration should overwrite
        agent_class = AgentRegistry.get("duplicate")
        assert agent_class == Agent2

    def test_clear_registry(self):
        """Test clearing the registry."""
        @AgentRegistry.register("test_agent")
        class TestAgent(BaseAgent):
            async def execute(self, input_data):
                return {}

        assert len(AgentRegistry.list_agents()) > 0

        AgentRegistry.clear()

        assert len(AgentRegistry.list_agents()) == 0
        assert not AgentRegistry.is_registered("test_agent")

    def test_is_registered(self):
        """Test checking if agent is registered."""
        assert not AgentRegistry.is_registered("test_agent")

        @AgentRegistry.register("test_agent")
        class TestAgent(BaseAgent):
            async def execute(self, input_data):
                return {}

        assert AgentRegistry.is_registered("test_agent")


# Integration tests
class TestIntegration:
    """Integration tests for agent system."""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow: register, create, execute."""
        # Register agent
        @AgentRegistry.register("workflow_agent")
        class WorkflowAgent(BaseAgent):
            def validate_input(self, input_data):
                super().validate_input(input_data)
                if "task" not in input_data:
                    raise AgentValidationError("Missing task")

            async def execute(self, input_data):
                task = input_data["task"]
                return {
                    "completed": True,
                    "task": task,
                    "result": f"Completed: {task}"
                }

        # Create instance
        agent = AgentRegistry.create_instance("workflow_agent")

        # Execute
        result = await agent.run({"task": "build website"})

        # Verify
        assert result["completed"] is True
        assert result["task"] == "build website"
        assert "Completed" in result["result"]

        # Check metrics
        metrics = agent.get_metrics()
        assert metrics.success is True
        assert metrics.execution_time > 0

    @pytest.mark.asyncio
    async def test_validation_error_recovery(self):
        """Test that validation errors are properly raised and can be caught."""
        @AgentRegistry.register("strict_agent")
        class StrictAgent(BaseAgent):
            def validate_input(self, input_data):
                super().validate_input(input_data)
                if input_data.get("value", 0) < 10:
                    raise AgentValidationError(
                        "Value must be >= 10",
                        details={"min_value": 10, "actual": input_data.get("value")}
                    )

            async def execute(self, input_data):
                return {"result": input_data["value"] * 2}

        agent = AgentRegistry.create_instance("strict_agent")

        # Should fail with value < 10
        with pytest.raises(AgentValidationError) as exc_info:
            await agent.run({"value": 5})

        assert "must be >= 10" in str(exc_info.value)
        assert exc_info.value.recoverable is True

        # Should succeed with value >= 10
        result = await agent.run({"value": 15})
        assert result["result"] == 30
