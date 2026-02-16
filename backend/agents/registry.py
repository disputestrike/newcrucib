"""
Agent registry for managing and instantiating agents.
Provides decorator-based registration and factory methods.
"""

import logging
from typing import Dict, Type, Any, List

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing agent classes.

    Provides:
    - Decorator-based registration
    - Agent class retrieval
    - Factory method for instantiation
    - Listing all registered agents

    Usage:
        # Register an agent
        @AgentRegistry.register("my_agent")
        class MyAgent(BaseAgent):
            pass

        # Get agent class
        agent_class = AgentRegistry.get("my_agent")

        # Create instance
        agent = AgentRegistry.create_instance("my_agent", name="Custom Name")

        # List all agents
        agents = AgentRegistry.list_agents()
    """

    _agents: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, name: str):
        """
        Decorator to register an agent class.

        Args:
            name: Unique name for the agent

        Returns:
            Decorator function

        Example:
            @AgentRegistry.register("planner")
            class PlannerAgent(BaseAgent):
                async def execute(self, input_data):
                    return {"plan": "..."}
        """
        def decorator(agent_class: Type[BaseAgent]):
            if not issubclass(agent_class, BaseAgent):
                raise TypeError(
                    f"Agent class {agent_class.__name__} must inherit from BaseAgent"
                )

            if name in cls._agents:
                logger.warning(
                    f"Agent '{name}' already registered. Overwriting with {agent_class.__name__}"
                )

            cls._agents[name] = agent_class
            logger.info(f"Registered agent: {name} ({agent_class.__name__})")

            return agent_class

        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseAgent]:
        """
        Get an agent class by name.

        Args:
            name: Name of the agent to retrieve

        Returns:
            Agent class

        Raises:
            KeyError: If agent is not registered
        """
        if name not in cls._agents:
            available = ", ".join(cls._agents.keys()) or "none"
            raise KeyError(
                f"Agent '{name}' not found in registry. "
                f"Available agents: {available}"
            )

        return cls._agents[name]

    @classmethod
    def list_agents(cls) -> List[str]:
        """
        List all registered agent names.

        Returns:
            List of agent names
        """
        return list(cls._agents.keys())

    @classmethod
    def create_instance(
        cls,
        agent_name: str,
        **kwargs: Any
    ) -> BaseAgent:
        """
        Factory method to create an agent instance.

        Args:
            agent_name: Name of the agent to instantiate
            **kwargs: Arguments to pass to the agent constructor

        Returns:
            Instantiated agent

        Raises:
            KeyError: If agent is not registered

        Example:
            agent = AgentRegistry.create_instance(
                "planner",
                name="Custom Planner"
            )
        """
        agent_class = cls.get(agent_name)
        return agent_class(**kwargs)

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered agents.

        Primarily for testing purposes.
        """
        cls._agents.clear()
        logger.info("Cleared agent registry")

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if an agent is registered.

        Args:
            name: Name of the agent to check

        Returns:
            True if agent is registered, False otherwise
        """
        return name in cls._agents
