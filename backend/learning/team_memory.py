"""
Team Memory System - Learn from past builds.
Tracks:
- Successful patterns per team/user
- Common tech stack choices
- Quality improvements over time
- Frequently used agents
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from collections import Counter

@dataclass
class BuildMemory:
    """Memory of a past build"""
    build_id: str
    user_id: str
    team_id: str
    prompt: str
    workflow_used: str
    tech_stack: Dict
    quality_score: float
    build_successful: bool
    duration_seconds: float
    agents_used: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "build_id": self.build_id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "prompt": self.prompt,
            "workflow_used": self.workflow_used,
            "tech_stack": self.tech_stack,
            "quality_score": self.quality_score,
            "build_successful": self.build_successful,
            "duration_seconds": self.duration_seconds,
            "agents_used": self.agents_used,
            "created_at": self.created_at.isoformat()
        }

class TeamMemory:
    """Learn from team's build history"""
    
    def __init__(self, storage_path: str = "./team_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.memories: List[BuildMemory] = []
        self._load_memories()
    
    def _load_memories(self):
        """Load past builds from storage"""
        memory_file = self.storage_path / "memories.json"
        if memory_file.exists():
            with open(memory_file) as f:
                data = json.load(f)
                self.memories = [
                    BuildMemory(
                        build_id=m["build_id"],
                        user_id=m["user_id"],
                        team_id=m["team_id"],
                        prompt=m["prompt"],
                        workflow_used=m["workflow_used"],
                        tech_stack=m["tech_stack"],
                        quality_score=m["quality_score"],
                        build_successful=m["build_successful"],
                        duration_seconds=m["duration_seconds"],
                        agents_used=m["agents_used"],
                        created_at=datetime.fromisoformat(m["created_at"])
                    )
                    for m in data
                ]
    
    def record_build(
        self,
        build_id: str,
        user_id: str,
        team_id: str,
        result: Dict[str, Any]
    ) -> BuildMemory:
        """Record a build in team memory"""
        memory = BuildMemory(
            build_id=build_id,
            user_id=user_id,
            team_id=team_id,
            prompt=result.get("prompt", ""),
            workflow_used=result.get("workflow", ""),
            tech_stack=result.get("summary", {}).get("tech_stack", {}),
            quality_score=result.get("validations", {}).get("quality", {}).get("overall_score", 0),
            build_successful=result.get("success", False),
            duration_seconds=result.get("metrics", {}).get("timing", {}).get("total_seconds", 0),
            agents_used=list(result.get("results", {}).keys()),
            created_at=datetime.now()
        )
        
        self.memories.append(memory)
        self._save_memories()
        
        return memory
    
    def get_team_insights(self, team_id: str) -> Dict[str, Any]:
        """Get insights for a team"""
        team_memories = [m for m in self.memories if m.team_id == team_id]
        
        if not team_memories:
            return {"message": "No build history yet"}
        
        successful = [m for m in team_memories if m.build_successful]
        
        # Most used tech stacks
        frontend_frameworks = Counter([
            m.tech_stack.get("frontend", {}).get("framework", "Unknown")
            for m in successful
        ])
        backend_frameworks = Counter([
            m.tech_stack.get("backend", {}).get("framework", "Unknown")
            for m in successful
        ])
        
        # Average quality over time
        quality_trend = [m.quality_score for m in successful[-10:]]  # Last 10 builds
        
        # Most used agents
        all_agents = [agent for m in successful for agent in m.agents_used]
        agent_usage = Counter(all_agents)
        
        return {
            "total_builds": len(team_memories),
            "successful_builds": len(successful),
            "success_rate": len(successful) / len(team_memories) * 100,
            "avg_quality_score": sum(m.quality_score for m in successful) / len(successful) if successful else 0,
            "quality_trend": quality_trend,
            "preferred_tech": {
                "frontend": frontend_frameworks.most_common(3),
                "backend": backend_frameworks.most_common(3)
            },
            "most_used_agents": agent_usage.most_common(5),
            "avg_build_time": sum(m.duration_seconds for m in successful) / len(successful) if successful else 0
        }
    
    def suggest_stack(self, team_id: str, prompt: str) -> Dict[str, Any]:
        """Suggest tech stack based on team history"""
        team_memories = [m for m in self.memories if m.team_id == team_id and m.build_successful]
        
        if len(team_memories) < 3:
            return {"suggestion": "default", "reason": "Not enough build history"}
        
        # Find similar past prompts
        similar = [
            m for m in team_memories
            if any(word in prompt.lower() for word in m.prompt.lower().split())
        ]
        
        if similar:
            # Use most common stack from similar builds
            stacks = [m.tech_stack for m in similar]
            # Simple: use most recent
            suggested_stack = stacks[-1]
            
            return {
                "suggestion": "learned",
                "tech_stack": suggested_stack,
                "reason": f"Based on {len(similar)} similar builds",
                "success_rate": len([m for m in similar if m.build_successful]) / len(similar) * 100
            }
        
        return {"suggestion": "default", "reason": "No similar builds found"}
    
    def get_improvement_recommendations(self, team_id: str) -> List[str]:
        """Recommend improvements based on patterns"""
        team_memories = [m for m in self.memories if m.team_id == team_id]
        
        if len(team_memories) < 5:
            return ["Build more projects to get personalized recommendations"]
        
        recommendations = []
        
        # Check quality trend
        recent_quality = [m.quality_score for m in team_memories[-5:] if m.build_successful]
        if recent_quality and sum(recent_quality) / len(recent_quality) < 75:
            recommendations.append("Recent builds have lower quality scores. Consider code review.")
        
        # Check build times
        recent_times = [m.duration_seconds for m in team_memories[-5:]]
        if recent_times and sum(recent_times) / len(recent_times) > 600:
            recommendations.append("Build times are high. Consider simpler workflows.")
        
        # Check success rate
        recent_success = len([m for m in team_memories[-10:] if m.build_successful]) / min(10, len(team_memories))
        if recent_success < 0.8:
            recommendations.append(f"Success rate is {recent_success*100:.0f}%. Review failed builds for patterns.")
        
        return recommendations or ["Great job! Keep building quality projects."]
    
    def _save_memories(self):
        """Save memories to storage"""
        memory_file = self.storage_path / "memories.json"
        with open(memory_file, 'w') as f:
            json.dump([m.to_dict() for m in self.memories], f, indent=2)
