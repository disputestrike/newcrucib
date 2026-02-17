"""
Base agent class for all CrucibAI agents.
Provides common validation and execution interface.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class AgentValidationError(Exception):
    """Raised when agent input validation fails."""
    pass


class BaseAgent(ABC):
    """
    Base class for all agents.
    Provides validation and execution interface.
    """
    
    def __init__(self, llm_client: Optional[Any], config: Dict[str, Any]):
        """
        Initialize agent.
        
        Args:
            llm_client: Optional LLM client for agents that need AI
            config: Agent-specific configuration
        """
        self.llm_client = llm_client
        self.config = config
        self.name = self.__class__.__name__
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """
        Validate input context.
        
        Args:
            context: Input context dictionary
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationError: If validation fails
        """
        if not isinstance(context, dict):
            raise AgentValidationError(f"{self.name}: context must be a dictionary")
        return True
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic.
        
        Args:
            context: Input context with action and parameters
            
        Returns:
            Result dictionary with success status and data
        """
        pass
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run agent: validate input, execute, return result.
        
        Args:
            context: Input context
            
        Returns:
            Result dictionary
        """
        try:
            self.validate_input(context)
            result = await self.execute(context)
            return result
        except AgentValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "validation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "execution"
            }
