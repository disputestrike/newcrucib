"""
Agent Registry - Dynamic agent registration and discovery system
Provides a central registry for all V2 agents with metadata and instantiation.
"""

from typing import Dict, List, Any, Type, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all V2 agents"""
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        self.llm_client = llm_client
        self.config = config
        self.metrics = {
            "agent_name": self.__class__.__name__,
            "success": False,
            "duration_ms": 0,
            "tokens_used": 0,
            "error": None
        }
    
    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given context"""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return agent execution metrics"""
        return self.metrics


class MockAgent(BaseAgent):
    """Mock agent for testing and fallback"""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        import time
        start = time.time()
        
        agent_name = self.__class__.__name__
        logger.info(f"Running {agent_name}")
        
        # Simulate work
        await asyncio.sleep(0.1)
        
        result = {
            "agent": agent_name,
            "status": "success",
            "output": f"{agent_name} completed successfully",
            "context_received": list(context.keys())
        }
        
        self.metrics["success"] = True
        self.metrics["duration_ms"] = (time.time() - start) * 1000
        self.metrics["tokens_used"] = 100
        
        return result


# Create mock agents for all the standard agent types
class PlannerAgent(MockAgent):
    """Decomposes user request into executable tasks"""
    pass


class StackSelectorAgent(MockAgent):
    """Recommends tech stack (frontend, backend, DB)"""
    pass


class DesignAgent(MockAgent):
    """Creates design specifications and image prompts"""
    pass


class DatabaseAgent(MockAgent):
    """Generates database schemas and migrations"""
    pass


class BackendAgent(MockAgent):
    """Generates backend API code"""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = await super().run(context)
        # Add mock files
        result["files"] = {
            "main.py": "# Backend code\nfrom fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'Hello World'}",
            "requirements.txt": "fastapi==0.104.1\nuvicorn==0.24.0"
        }
        return result


class FrontendAgent(MockAgent):
    """Generates frontend code"""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = await super().run(context)
        # Add mock files
        result["files"] = {
            "src/App.tsx": "import React from 'react';\n\nfunction App() {\n  return <div>Hello World</div>;\n}\n\nexport default App;",
            "package.json": '{"name": "frontend", "dependencies": {"react": "^18.0.0"}}'
        }
        return result


class TestGenerationAgent(MockAgent):
    """Generates test code"""
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = await super().run(context)
        # Add mock test files
        result["test_files"] = {
            "test_main.py": "def test_example():\n    assert True"
        }
        result["test_framework"] = "pytest"
        return result


class SecurityAgent(MockAgent):
    """Performs security audits"""
    pass


class DeploymentAgent(MockAgent):
    """Generates deployment configurations"""
    pass


class DocumentationAgent(MockAgent):
    """Generates project documentation"""
    pass


class AgentRegistry:
    """Central registry for all agents"""
    
    _agents: Dict[str, Type[BaseAgent]] = {
        "PlannerAgent": PlannerAgent,
        "StackSelectorAgent": StackSelectorAgent,
        "DesignAgent": DesignAgent,
        "DatabaseAgent": DatabaseAgent,
        "BackendAgent": BackendAgent,
        "FrontendAgent": FrontendAgent,
        "TestGenerationAgent": TestGenerationAgent,
        "SecurityAgent": SecurityAgent,
        "DeploymentAgent": DeploymentAgent,
        "DocumentationAgent": DocumentationAgent,
    }
    
    @classmethod
    def register(cls, name: str, agent_class: Type[BaseAgent]):
        """Register a new agent type"""
        cls._agents[name] = agent_class
        logger.info(f"Registered agent: {name}")
    
    @classmethod
    def create_instance(cls, name: str, llm_client, config: Dict[str, Any]) -> BaseAgent:
        """Create an instance of a registered agent"""
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not found in registry. Available: {list(cls._agents.keys())}")
        
        agent_class = cls._agents[name]
        return agent_class(llm_client, config)
    
    @classmethod
    def list_agents(cls) -> List[Dict[str, Any]]:
        """List all registered agents with metadata"""
        return [
            {
                "name": name,
                "class": agent_class.__name__,
                "description": agent_class.__doc__ or "No description",
            }
            for name, agent_class in cls._agents.items()
        ]
    
    @classmethod
    def get_agent_names(cls) -> List[str]:
        """Get list of all registered agent names"""
        return list(cls._agents.keys())


import asyncio
