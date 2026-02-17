"""
Agent Marketplace - create, share, install custom agents.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.registry import AgentRegistry

@dataclass
class CustomAgentDefinition:
    """Definition for a custom agent"""
    name: str
    author: str
    description: str
    version: str
    category: str  # "frontend", "backend", "design", "utility", etc.
    system_prompt: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str]
    rating: float = 0.0
    downloads: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "author": self.author,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "system_prompt": self.system_prompt,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "dependencies": self.dependencies,
            "rating": self.rating,
            "downloads": self.downloads
        }

class AgentMarketplace:
    """Marketplace for custom agents"""
    
    def __init__(self, store_path: str = "./marketplace"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(exist_ok=True)
    
    def publish_agent(self, definition: CustomAgentDefinition) -> Dict[str, Any]:
        """Publish a custom agent to marketplace"""
        agent_file = self.store_path / f"{definition.name}.json"
        
        if agent_file.exists():
            return {
                "success": False,
                "error": "Agent already exists. Use update_agent() instead."
            }
        
        # Save agent definition
        with open(agent_file, 'w') as f:
            json.dump(definition.to_dict(), f, indent=2)
        
        # Create agent class dynamically
        agent_class = self._create_agent_class(definition)
        
        # Register with AgentRegistry
        AgentRegistry.register(agent_class)
        
        return {
            "success": True,
            "agent_name": definition.name,
            "message": f"Agent '{definition.name}' published successfully"
        }
    
    def install_agent(self, agent_name: str) -> Dict[str, Any]:
        """Install an agent from marketplace"""
        agent_file = self.store_path / f"{agent_name}.json"
        
        if not agent_file.exists():
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found in marketplace"
            }
        
        # Load definition
        with open(agent_file, 'r') as f:
            definition_dict = json.load(f)
        
        definition = CustomAgentDefinition(**definition_dict)
        
        # Create and register agent
        agent_class = self._create_agent_class(definition)
        AgentRegistry.register(agent_class)
        
        # Update download count
        definition.downloads += 1
        with open(agent_file, 'w') as f:
            json.dump(definition.to_dict(), f, indent=2)
        
        return {
            "success": True,
            "agent_name": agent_name,
            "message": f"Agent '{agent_name}' installed successfully"
        }
    
    def list_agents(self, category: str = None) -> List[Dict]:
        """List all agents in marketplace"""
        agents = []
        
        for agent_file in self.store_path.glob("*.json"):
            with open(agent_file, 'r') as f:
                definition = json.load(f)
            
            if category is None or definition.get("category") == category:
                agents.append(definition)
        
        # Sort by downloads and rating
        agents.sort(key=lambda x: (x.get("downloads", 0), x.get("rating", 0)), reverse=True)
        
        return agents
    
    def rate_agent(self, agent_name: str, rating: float) -> Dict[str, Any]:
        """Rate an agent (1-5 stars)"""
        agent_file = self.store_path / f"{agent_name}.json"
        
        if not agent_file.exists():
            return {"success": False, "error": "Agent not found"}
        
        with open(agent_file, 'r') as f:
            definition = json.load(f)
        
        # Update rating (simple average for now)
        current_rating = definition.get("rating", 0)
        downloads = definition.get("downloads", 1)
        new_rating = (current_rating * downloads + rating) / (downloads + 1)
        
        definition["rating"] = round(new_rating, 2)
        
        with open(agent_file, 'w') as f:
            json.dump(definition, f, indent=2)
        
        return {
            "success": True,
            "agent_name": agent_name,
            "new_rating": new_rating
        }
    
    def _create_agent_class(self, definition: CustomAgentDefinition):
        """Dynamically create agent class from definition"""
        
        class DynamicAgent(BaseAgent):
            """Dynamically created custom agent"""
            
            def __init__(self, llm_client, config):
                super().__init__(llm_client, config)
                self.name = definition.name
                self.system_prompt = definition.system_prompt
            
            def validate_input(self, context: Dict[str, Any]) -> bool:
                super().validate_input(context)
                # Validate against input schema
                # TODO: Add JSON schema validation
                return True
            
            def validate_output(self, result: Dict[str, Any]) -> bool:
                super().validate_output(result)
                # Validate against output schema
                return True
            
            async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
                # Use LLM with custom system prompt
                user_prompt = context.get("user_prompt", "")
                
                response, tokens = await self.call_llm(
                    user_prompt,
                    self.system_prompt
                )
                
                # Parse response
                try:
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    
                    data = json.loads(response)
                    data["_tokens_used"] = tokens
                    data["_model_used"] = self.config.get("default_model", "gpt-4o")
                    
                    return data
                except:
                    return {
                        "output": response,
                        "_tokens_used": tokens,
                        "_model_used": self.config.get("default_model", "gpt-4o")
                    }
        
        # Set class name
        DynamicAgent.__name__ = definition.name
        DynamicAgent.__qualname__ = definition.name
        
        return DynamicAgent
