"""
Base Agent class for all tool agents.
Provides common interface and run method.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all tool agents"""
    
    def __init__(self, llm_client=None, config: Dict[str, Any] = None):
        self.llm_client = llm_client
        self.config = config or {}
        self.name = "BaseAgent"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent and handle errors"""
        try:
            logger.info(f"{self.name} starting execution")
            result = await self.execute(context)
            logger.info(f"{self.name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{self.name} failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "agent": self.name
            }
