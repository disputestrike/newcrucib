"""
Agent Registry for dynamic agent registration and discovery.
"""

from typing import Dict, Type, List, Optional
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing agent classes"""
    
    _agents: Dict[str, Type] = {}
    _metadata: Dict[str, Dict] = {}
    
    @classmethod
    def register(
        cls,
        agent_class: Type,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Register an agent class.
        
        Args:
            agent_class: The agent class to register
            metadata: Optional metadata about the agent
        """
        name = agent_class.__name__
        
        if name in cls._agents:
            logger.warning(f"Agent '{name}' already registered, overwriting")
        
        cls._agents[name] = agent_class
        cls._metadata[name] = metadata or {}
        
        logger.info(f"Registered agent: {name}")
    
    @classmethod
    def unregister(cls, agent_name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_name: Name of the agent to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if agent_name in cls._agents:
            del cls._agents[agent_name]
            if agent_name in cls._metadata:
                del cls._metadata[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
            return True
        return False
    
    @classmethod
    def get(cls, agent_name: str) -> Optional[Type]:
        """
        Get an agent class by name.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent class or None if not found
        """
        return cls._agents.get(agent_name)
    
    @classmethod
    def get_all(cls) -> Dict[str, Type]:
        """Get all registered agents"""
        return cls._agents.copy()
    
    @classmethod
    def get_metadata(cls, agent_name: str) -> Optional[Dict]:
        """Get metadata for an agent"""
        return cls._metadata.get(agent_name)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent names"""
        return list(cls._agents.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered agents (mainly for testing)"""
        cls._agents.clear()
        cls._metadata.clear()
        logger.info("Cleared all registered agents")
