"""
Team Memory - learns from past builds and suggests improvements.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import json
from pathlib import Path
from collections import defaultdict

@dataclass
class BuildHistory:
    """Record of a single build"""
    id: str
    user_id: str
    team_id: str
    prompt: str
    workflow: str
    tech_stack: Dict[str, Any]
    success: bool
    quality_score: float
    duration_seconds: float
    files_generated: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "prompt": self.prompt,
            "workflow": self.workflow,
            "tech_stack": self.tech_stack,
            "success": self.success,
            "quality_score": self.quality_score,
            "duration_seconds": self.duration_seconds,
            "files_generated": self.files_generated,
            "timestamp": self.timestamp
        }

class TeamMemory:
    """Learning system that improves based on history"""
    
    def __init__(self, memory_path: str = "./memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(exist_ok=True)
    
    def record_build(self, build: BuildHistory):
        """Record a build in memory"""
        team_file = self.memory_path / f"team_{build.team_id}.json"
        
        # Load existing history
        if team_file.exists():
            with open(team_file, 'r') as f:
                history = json.load(f)
        else:
            history = {"builds": []}
        
        # Add new build
        history["builds"].append(build.to_dict())
        
        # Save
        with open(team_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_team_history(self, team_id: str) -> List[BuildHistory]:
        """Get all builds for a team"""
        team_file = self.memory_path / f"team_{team_id}.json"
        
        if not team_file.exists():
            return []
        
        with open(team_file, 'r') as f:
            history = json.load(f)
        
        return [BuildHistory(**b) for b in history["builds"]]
    
    def suggest_stack(self, prompt: str, team_id: str) -> Dict[str, Any]:
        """Suggest tech stack based on team history"""
        history = self.get_team_history(team_id)
        
        if not history:
            return {
                "suggestion": None,
                "reason": "No team history available"
            }
        
        # Analyze successful builds
        successful = [b for b in history if b.success and b.quality_score > 70]
        
        if not successful:
            return {
                "suggestion": None,
                "reason": "No successful builds to learn from"
            }
        
        # Count tech stack usage
        stack_usage = defaultdict(int)
        stack_quality = defaultdict(list)
        
        for build in successful:
            stack_key = json.dumps(build.tech_stack, sort_keys=True)
            stack_usage[stack_key] += 1
            stack_quality[stack_key].append(build.quality_score)
        
        # Find most used stack with highest quality
        best_stack = max(
            stack_usage.keys(),
            key=lambda k: (stack_usage[k], sum(stack_quality[k]) / len(stack_quality[k]))
        )
        
        stack_dict = json.loads(best_stack)
        avg_quality = sum(stack_quality[best_stack]) / len(stack_quality[best_stack])
        
        return {
            "suggestion": stack_dict,
            "reason": f"Used {stack_usage[best_stack]} times with {avg_quality:.1f} avg quality",
            "usage_count": stack_usage[best_stack],
            "avg_quality": avg_quality
        }
    
    def get_insights(self, team_id: str) -> Dict[str, Any]:
        """Get insights and recommendations for team"""
        history = self.get_team_history(team_id)
        
        if not history:
            return {"insights": []}
        
        insights = []
        
        # Success rate
        success_rate = sum(1 for b in history if b.success) / len(history) * 100
        insights.append(f"Team success rate: {success_rate:.1f}%")
        
        # Average quality
        avg_quality = sum(b.quality_score for b in history) / len(history)
        insights.append(f"Average code quality: {avg_quality:.1f}/100")
        
        # Most used workflow
        workflows = defaultdict(int)
        for b in history:
            workflows[b.workflow] += 1
        most_used = max(workflows, key=workflows.get)
        insights.append(f"Most used workflow: {most_used} ({workflows[most_used]} times)")
        
        # Speed improvement
        if len(history) >= 5:
            early_builds = history[:5]
            recent_builds = history[-5:]
            early_avg = sum(b.duration_seconds for b in early_builds) / 5
            recent_avg = sum(b.duration_seconds for b in recent_builds) / 5
            improvement = (early_avg - recent_avg) / early_avg * 100
            insights.append(f"Speed improvement: {improvement:+.1f}%")
        
        return {
            "team_id": team_id,
            "total_builds": len(history),
            "insights": insights,
            "success_rate": success_rate,
            "avg_quality": avg_quality
        }
