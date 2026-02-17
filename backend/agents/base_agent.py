"""
Base Agent class for all tool agents.
Provides common interface and async execution pattern.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all tool agents"""
    
    def __init__(self, llm_client=None, config: Dict[str, Any] = None):
        """
        Initialize base agent.
        
        Args:
            llm_client: Optional LLM client for agents that need AI capabilities
            config: Configuration dictionary for the agent
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.name = "BaseAgent"
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            context: Input context with parameters for the agent
            
        Returns:
            Dictionary with results and success status
        """
        pass
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run wrapper that calls execute and handles common patterns.
        
        Args:
            context: Input context dictionary
            
        Returns:
            Result dictionary from execute
        """
        try:
            result = await self.execute(context)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "agent": self.name
            }
