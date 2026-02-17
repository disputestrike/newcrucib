"""
Base Agent class for all agents in the system.
Provides a common interface and utilities for agent execution.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, llm_client: Any, config: Dict[str, Any]):
        """
        Initialize the agent.
        
        Args:
            llm_client: LLM client for making API calls (can be None for custom agents)
            config: Configuration dictionary for the agent
        """
        self.llm_client = llm_client
        self.config = config
        self.name = self.__class__.__name__
        self.system_prompt = ""
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """
        Validate input context before execution.
        
        Args:
            context: Input context dictionary
            
        Returns:
            True if valid, raises exception otherwise
        """
        if not isinstance(context, dict):
            raise ValueError(f"Context must be a dictionary, got {type(context)}")
        return True
    
    def validate_output(self, result: Dict[str, Any]) -> bool:
        """
        Validate output after execution.
        
        Args:
            result: Output result dictionary
            
        Returns:
            True if valid, raises exception otherwise
        """
        if not isinstance(result, dict):
            raise ValueError(f"Result must be a dictionary, got {type(result)}")
        return True
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with the given context.
        
        Args:
            context: Input context dictionary
            
        Returns:
            Dictionary with agent output
        """
        pass
    
    async def call_llm(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> tuple[str, int]:
        """
        Call the LLM with the given prompts.
        
        Args:
            user_prompt: User prompt
            system_prompt: System prompt (uses self.system_prompt if None)
            
        Returns:
            Tuple of (response_text, tokens_used)
        """
        if self.llm_client is None:
            raise RuntimeError("LLM client not configured for this agent")
        
        sys_prompt = system_prompt or self.system_prompt
        
        # Call the LLM client (this should be implemented by the server)
        # For now, return a placeholder
        if hasattr(self.llm_client, '__call__'):
            return await self.llm_client(user_prompt, sys_prompt)
        
        # Fallback for testing
        return f"Response to: {user_prompt[:100]}", 0
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
