"""
Agent registry for auto-registration and discovery.
"""

from typing import Dict, Type, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_agent import BaseAgent


class AgentRegistry:
    """
    Registry for all agent classes.
    Agents can register themselves using the @AgentRegistry.register decorator.
    """
    
    _agents: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, agent_class: Type) -> Type:
        """
        Register an agent class.
        
        Usage:
            @AgentRegistry.register
            class MyAgent(BaseAgent):
                ...
        """
        cls._agents[agent_class.__name__] = agent_class
        return agent_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type]:
        """Get an agent class by name."""
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls) -> Dict[str, Type]:
        """Get all registered agents."""
        return cls._agents.copy()
