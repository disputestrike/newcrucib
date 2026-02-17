"""
Observability Dashboard - monitor agent performance in real-time.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class AgentMetrics:
    """Real-time metrics for an agent"""
    agent_name: str
    total_executions: int
    successful: int
    failed: int
    avg_duration_ms: float
    avg_tokens: float
    avg_quality_score: float
    last_executed: str
    
    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0
        return (self.successful / self.total_executions) * 100
    
    def to_dict(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "total_executions": self.total_executions,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": round(self.success_rate, 2),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "avg_tokens": round(self.avg_tokens, 2),
            "avg_quality_score": round(self.avg_quality_score, 2),
            "last_executed": self.last_executed
        }

class Dashboard:
    """Real-time observability dashboard"""
    
    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}
    
    def record_execution(
        self,
        agent_name: str,
        success: bool,
        duration_ms: float,
        tokens: int,
        quality_score: float = None
    ):
        """Record an agent execution"""
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics(
                agent_name=agent_name,
                total_executions=0,
                successful=0,
                failed=0,
                avg_duration_ms=0,
                avg_tokens=0,
                avg_quality_score=0,
                last_executed=datetime.now().isoformat()
            )
        
        metric = self.metrics[agent_name]
        
        # Update counts
        metric.total_executions += 1
        if success:
            metric.successful += 1
        else:
            metric.failed += 1
        
        # Update averages
        n = metric.total_executions
        metric.avg_duration_ms = (metric.avg_duration_ms * (n-1) + duration_ms) / n
        metric.avg_tokens = (metric.avg_tokens * (n-1) + tokens) / n
        
        if quality_score is not None:
            metric.avg_quality_score = (metric.avg_quality_score * (n-1) + quality_score) / n
        
        metric.last_executed = datetime.now().isoformat()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        agents = [m.to_dict() for m in self.metrics.values()]
        
        # Sort by total executions
        agents.sort(key=lambda x: x["total_executions"], reverse=True)
        
        # Calculate overall metrics
        if agents:
            overall_success = sum(a["successful"] for a in agents) / sum(a["total_executions"] for a in agents) * 100
            overall_avg_duration = sum(a["avg_duration_ms"] * a["total_executions"] for a in agents) / sum(a["total_executions"] for a in agents)
        else:
            overall_success = 0
            overall_avg_duration = 0
        
        return {
            "agents": agents,
            "summary": {
                "total_agents": len(agents),
                "total_executions": sum(a["total_executions"] for a in agents),
                "overall_success_rate": round(overall_success, 2),
                "overall_avg_duration_ms": round(overall_avg_duration, 2)
            }
        }
