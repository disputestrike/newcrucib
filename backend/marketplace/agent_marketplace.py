"""
Agent Marketplace - Create and share custom agents.
Users can:
- Create custom agents with prompts
- Share agents with community
- Install agents from others
- Rate and review agents
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

@dataclass
class CustomAgent:
    """Custom agent definition"""
    id: str
    name: str
    description: str
    author: str
    category: str  # "frontend", "backend", "data", "design", etc.
    system_prompt: str
    input_schema: Dict
    output_schema: Dict
    version: str
    downloads: int
    rating: float
    created_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "category": self.category,
            "system_prompt": self.system_prompt,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "version": self.version,
            "downloads": self.downloads,
            "rating": self.rating,
            "created_at": self.created_at.isoformat()
        }

class AgentMarketplace:
    """Manage custom agent marketplace"""
    
    def __init__(self, storage_path: str = "./marketplace_agents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.agents: Dict[str, CustomAgent] = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load agents from storage"""
        for agent_file in self.storage_path.glob("*.json"):
            with open(agent_file) as f:
                data = json.load(f)
                agent = CustomAgent(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    author=data["author"],
                    category=data["category"],
                    system_prompt=data["system_prompt"],
                    input_schema=data["input_schema"],
                    output_schema=data["output_schema"],
                    version=data["version"],
                    downloads=data.get("downloads", 0),
                    rating=data.get("rating", 0.0),
                    created_at=datetime.fromisoformat(data["created_at"])
                )
                self.agents[agent.id] = agent
    
    def create_agent(
        self,
        name: str,
        description: str,
        author: str,
        category: str,
        system_prompt: str,
        input_schema: Dict,
        output_schema: Dict
    ) -> CustomAgent:
        """Create new custom agent"""
        import uuid
        
        agent_id = str(uuid.uuid4())
        agent = CustomAgent(
            id=agent_id,
            name=name,
            description=description,
            author=author,
            category=category,
            system_prompt=system_prompt,
            input_schema=input_schema,
            output_schema=output_schema,
            version="1.0.0",
            downloads=0,
            rating=0.0,
            created_at=datetime.now()
        )
        
        # Save to storage
        agent_file = self.storage_path / f"{agent_id}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent.to_dict(), f, indent=2)
        
        self.agents[agent_id] = agent
        return agent
    
    def search_agents(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: float = 0.0
    ) -> List[CustomAgent]:
        """Search marketplace agents"""
        results = list(self.agents.values())
        
        if query:
            query_lower = query.lower()
            results = [
                a for a in results
                if query_lower in a.name.lower() or query_lower in a.description.lower()
            ]
        
        if category:
            results = [a for a in results if a.category == category]
        
        if min_rating > 0:
            results = [a for a in results if a.rating >= min_rating]
        
        # Sort by downloads * rating
        results.sort(key=lambda a: a.downloads * a.rating, reverse=True)
        
        return results
    
    def install_agent(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Install agent for a user"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        # Increment downloads
        agent.downloads += 1
        self._save_agent(agent)
        
        # Register agent dynamically
        # Note: In production, this would integrate with agent registry
        # For now, just return success
        
        return {
            "success": True,
            "agent_name": agent.name,
            "message": f"Agent '{agent.name}' installed successfully"
        }
    
    def rate_agent(self, agent_id: str, rating: float, user_id: str) -> Dict[str, Any]:
        """Rate an agent (1-5 stars)"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"success": False, "error": "Agent not found"}
        
        # Simple average (in production, track individual ratings)
        agent.rating = (agent.rating + rating) / 2
        self._save_agent(agent)
        
        return {
            "success": True,
            "new_rating": agent.rating
        }
    
    def _save_agent(self, agent: CustomAgent):
        """Save agent to storage"""
        agent_file = self.storage_path / f"{agent.id}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent.to_dict(), f, indent=2)
