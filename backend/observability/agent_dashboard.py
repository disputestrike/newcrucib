"""
Agent Observability Dashboard.
Tracks:
- Agent execution times
- Success/failure rates
- Token usage per agent
- Bottlenecks in workflows
- Error patterns
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import json

@dataclass
class AgentMetric:
    """Single agent execution metric"""
    agent_name: str
    timestamp: datetime
    duration_ms: float
    tokens_used: int
    success: bool
    error: str = None

class AgentDashboard:
    """Real-time agent performance dashboard"""
    
    def __init__(self):
        self.metrics: List[AgentMetric] = []
    
    def record_execution(self, agent_metrics: Dict[str, Any]):
        """Record agent execution metrics"""
        metric = AgentMetric(
            agent_name=agent_metrics["agent_name"],
            timestamp=datetime.now(),
            duration_ms=agent_metrics["duration_ms"],
            tokens_used=agent_metrics["tokens_used"],
            success=agent_metrics["success"],
            error=agent_metrics.get("error")
        )
        self.metrics.append(metric)
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get dashboard data for last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.metrics if m.timestamp > cutoff]
        
        if not recent:
            return {"message": "No recent data"}
        
        # By agent statistics
        by_agent = defaultdict(lambda: {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "total_duration_ms": 0,
            "total_tokens": 0,
            "errors": []
        })
        
        for m in recent:
            stats = by_agent[m.agent_name]
            stats["executions"] += 1
            if m.success:
                stats["successes"] += 1
            else:
                stats["failures"] += 1
                if m.error:
                    stats["errors"].append(m.error)
            stats["total_duration_ms"] += m.duration_ms
            stats["total_tokens"] += m.tokens_used
        
        # Calculate averages and format
        agent_stats = {}
        for agent, stats in by_agent.items():
            agent_stats[agent] = {
                "executions": stats["executions"],
                "success_rate": stats["successes"] / stats["executions"] * 100,
                "avg_duration_ms": stats["total_duration_ms"] / stats["executions"],
                "avg_tokens": stats["total_tokens"] / stats["executions"],
                "total_tokens": stats["total_tokens"],
                "failures": stats["failures"],
                "common_errors": list(set(stats["errors"]))[:3]
            }
        
        # Overall statistics
        total_executions = len(recent)
        total_successes = len([m for m in recent if m.success])
        
        # Find bottlenecks
        sorted_by_time = sorted(agent_stats.items(), key=lambda x: x[1]["avg_duration_ms"], reverse=True)
        bottlenecks = sorted_by_time[:3]
        
        return {
            "time_range_hours": hours,
            "overall": {
                "total_executions": total_executions,
                "success_rate": total_successes / total_executions * 100,
                "total_tokens": sum(m.tokens_used for m in recent),
                "avg_duration_ms": sum(m.duration_ms for m in recent) / len(recent)
            },
            "by_agent": agent_stats,
            "bottlenecks": [
                {"agent": agent, "avg_duration_ms": stats["avg_duration_ms"]}
                for agent, stats in bottlenecks
            ],
            "recommendations": self._generate_recommendations(agent_stats)
        }
    
    def _generate_recommendations(self, agent_stats: Dict) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for slow agents
        slow_agents = [
            agent for agent, stats in agent_stats.items()
            if stats["avg_duration_ms"] > 30000  # >30s
        ]
        if slow_agents:
            recommendations.append(f"Optimize slow agents: {', '.join(slow_agents)}")
        
        # Check for high failure rates
        failing_agents = [
            agent for agent, stats in agent_stats.items()
            if stats["success_rate"] < 80
        ]
        if failing_agents:
            recommendations.append(f"Improve reliability: {', '.join(failing_agents)}")
        
        # Check token usage
        expensive_agents = [
            agent for agent, stats in agent_stats.items()
            if stats["avg_tokens"] > 5000
        ]
        if expensive_agents:
            recommendations.append(f"Reduce token usage: {', '.join(expensive_agents)}")
        
        return recommendations or ["All agents performing well!"]
