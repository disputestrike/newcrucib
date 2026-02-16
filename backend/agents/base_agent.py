"""
Base agent class for Newcrucib V2 agent system.
Provides abstract base class with validation, metrics tracking, and LLM integration.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from error_handlers import CrucibError, ErrorSeverity

logger = logging.getLogger(__name__)

# Token estimation multiplier (approximation: words * 1.3 accounts for subword tokenization)
TOKEN_ESTIMATION_MULTIPLIER = 1.3


@dataclass
class AgentMetrics:
    """Metrics for agent execution tracking."""

    agent_name: str
    execution_time: float = 0.0
    tokens_used: int = 0
    success: bool = False
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    llm_calls: int = 0
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "success": self.success,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "llm_calls": self.llm_calls,
            "additional_metrics": self.additional_metrics,
        }


class AgentValidationError(CrucibError):
    """Raised when agent input or output validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AGENT_VALIDATION_ERROR",
            severity=ErrorSeverity.MEDIUM,
            status_code=400,
            details=details,
            recoverable=True
        )


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Newcrucib V2 system.

    Provides:
    - Input/output validation
    - Metrics tracking
    - LLM integration helper
    - Consistent error handling
    - Async execution support

    Usage:
        class MyAgent(BaseAgent):
            async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                # Implement agent logic
                result = await self.call_llm(prompt="...", system="...")
                return {"output": result}

            def validate_input(self, input_data: Dict[str, Any]) -> None:
                if "required_field" not in input_data:
                    raise AgentValidationError("Missing required_field")

            def validate_output(self, output_data: Dict[str, Any]) -> None:
                if "output" not in output_data:
                    raise AgentValidationError("Missing output field")
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the agent.

        Args:
            name: Optional agent name. Defaults to class name.
        """
        self.name = name or self.__class__.__name__
        self._metrics = AgentMetrics(agent_name=self.name)
        self._llm_caller: Optional[Any] = None

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.

        This method must be implemented by subclasses.

        Args:
            input_data: Input data for the agent

        Returns:
            Dictionary containing the agent's output

        Raises:
            AgentValidationError: If execution fails due to validation issues
            Exception: For other execution errors
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Validate input data before execution.

        Override this method to implement custom validation logic.
        Raise AgentValidationError if validation fails.

        Args:
            input_data: Input data to validate

        Raises:
            AgentValidationError: If validation fails
        """
        if not isinstance(input_data, dict):
            raise AgentValidationError(
                "Input data must be a dictionary",
                details={"type": type(input_data).__name__}
            )

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        """
        Validate output data after execution.

        Override this method to implement custom validation logic.
        Raise AgentValidationError if validation fails.

        Args:
            output_data: Output data to validate

        Raises:
            AgentValidationError: If validation fails
        """
        if not isinstance(output_data, dict):
            raise AgentValidationError(
                "Output data must be a dictionary",
                details={"type": type(output_data).__name__}
            )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with full validation and metrics tracking.

        This wrapper method:
        1. Validates input
        2. Executes the agent
        3. Validates output
        4. Tracks metrics
        5. Handles errors

        Args:
            input_data: Input data for the agent

        Returns:
            Dictionary containing the agent's output

        Raises:
            AgentValidationError: If validation fails
            Exception: For other execution errors
        """
        self._metrics = AgentMetrics(agent_name=self.name)
        self._metrics.started_at = datetime.now(timezone.utc)
        start_time = time.time()

        try:
            # Validate input
            self.validate_input(input_data)

            # Execute agent logic
            output_data = await self.execute(input_data)

            # Validate output
            self.validate_output(output_data)

            # Mark success
            self._metrics.success = True

            return output_data

        except AgentValidationError:
            # Re-raise validation errors as-is
            raise

        except Exception as e:
            # Log and re-raise other errors
            self._metrics.error_message = str(e)
            logger.error(f"Agent {self.name} execution failed: {e}")
            raise

        finally:
            # Record execution time
            self._metrics.execution_time = time.time() - start_time
            self._metrics.completed_at = datetime.now(timezone.utc)

    def get_metrics(self) -> AgentMetrics:
        """
        Get the metrics for the last execution.

        Returns:
            AgentMetrics object with execution details
        """
        return self._metrics

    async def call_llm(
        self,
        prompt: str,
        system: str,
        model_chain: Optional[list] = None,
        api_keys: Optional[Dict[str, Optional[str]]] = None,
    ) -> str:
        """
        Helper method to call LLM with fallback support.

        This integrates with the existing LLM router in server.py.
        Tracks token usage in metrics.

        Args:
            prompt: User prompt for the LLM
            system: System message for the LLM
            model_chain: Optional list of model configurations to try
            api_keys: Optional API keys dictionary

        Returns:
            LLM response text

        Raises:
            Exception: If all models in chain fail
        """
        # Import here to avoid circular dependency
        from server import _call_llm_with_fallback, MODEL_FALLBACK_CHAINS
        import uuid

        # Use default model chain if not provided
        if model_chain is None:
            model_chain = MODEL_FALLBACK_CHAINS

        # Generate a session ID for this call
        session_id = str(uuid.uuid4())

        # Call LLM with fallback
        response, model_used = await _call_llm_with_fallback(
            message=prompt,
            system_message=system,
            session_id=session_id,
            model_chain=model_chain,
            api_keys=api_keys,
        )

        # Track metrics
        self._metrics.llm_calls += 1
        # Estimate tokens using approximation multiplier
        tokens = int((len(prompt.split()) + len(response.split())) * TOKEN_ESTIMATION_MULTIPLIER)
        self._metrics.tokens_used += tokens

        logger.info(f"Agent {self.name} called LLM ({model_used}), ~{tokens} tokens")

        return response

    def set_llm_caller(self, caller: Any) -> None:
        """
        Set a custom LLM caller for testing or customization.

        Args:
            caller: Callable that takes (prompt, system, ...) and returns response
        """
        self._llm_caller = caller
