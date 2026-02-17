"""
Self-Improvement System.
Automatically:
- A/B tests different system prompts
- Learns which variants perform better
- Updates agent prompts based on results
- Tracks improvement over time
"""

from typing import Dict, Any, List
import random
from dataclasses import dataclass
from datetime import datetime

# Constants for self-improvement scoring
DURATION_PENALTY_DIVISOR = 10000  # Divisor for duration penalty calculation
MAX_DURATION_PENALTY = 0.5  # Maximum penalty for slow execution
MIN_EXECUTIONS_FOR_BEST = 10  # Minimum executions required to consider variant

@dataclass
class PromptVariant:
    """A/B test variant of agent prompt"""
    variant_id: str
    agent_name: str
    system_prompt: str
    executions: int
    avg_quality_score: float
    avg_duration_ms: float
    success_rate: float
    
class SelfImprovement:
    """A/B test and improve agent prompts"""
    
    def __init__(self):
        self.variants: Dict[str, List[PromptVariant]] = {}
        self.active_tests: Dict[str, str] = {}  # agent_name -> variant_id
    
    def create_prompt_variant(
        self,
        agent_name: str,
        variant_prompt: str,
        variant_name: str = "variant_a"
    ) -> PromptVariant:
        """Create new prompt variant for A/B testing"""
        import uuid
        
        variant = PromptVariant(
            variant_id=str(uuid.uuid4()),
            agent_name=agent_name,
            system_prompt=variant_prompt,
            executions=0,
            avg_quality_score=0.0,
            avg_duration_ms=0.0,
            success_rate=0.0
        )
        
        if agent_name not in self.variants:
            self.variants[agent_name] = []
        
        self.variants[agent_name].append(variant)
        
        return variant
    
    def select_variant(self, agent_name: str) -> str:
        """Select which prompt variant to use (epsilon-greedy)"""
        variants = self.variants.get(agent_name, [])
        
        if not variants:
            return "default"  # Use default prompt
        
        # 10% exploration, 90% exploitation
        if random.random() < 0.1:
            # Explore: random variant
            return random.choice(variants).variant_id
        else:
            # Exploit: best performing variant
            best = max(variants, key=lambda v: v.avg_quality_score * v.success_rate)
            return best.variant_id
    
    def record_result(
        self,
        agent_name: str,
        variant_id: str,
        quality_score: float,
        duration_ms: float,
        success: bool
    ):
        """Record result of variant execution"""
        variants = self.variants.get(agent_name, [])
        variant = next((v for v in variants if v.variant_id == variant_id), None)
        
        if not variant:
            return
        
        # Update running averages
        n = variant.executions
        variant.avg_quality_score = (variant.avg_quality_score * n + quality_score) / (n + 1)
        variant.avg_duration_ms = (variant.avg_duration_ms * n + duration_ms) / (n + 1)
        variant.success_rate = (variant.success_rate * n + (1 if success else 0)) / (n + 1)
        variant.executions += 1
    
    def get_best_variant(self, agent_name: str) -> PromptVariant:
        """Get best performing variant for an agent"""
        variants = self.variants.get(agent_name, [])
        
        if not variants:
            return None
        
        # Score = quality * success_rate - (duration penalty)
        def score(v: PromptVariant) -> float:
            if v.executions < MIN_EXECUTIONS_FOR_BEST:  # Need minimum data
                return 0
            duration_penalty = min(v.avg_duration_ms / DURATION_PENALTY_DIVISOR, MAX_DURATION_PENALTY)
            return v.avg_quality_score * v.success_rate - duration_penalty
        
        return max(variants, key=score)
    
    def generate_improvement_report(self, agent_name: str) -> Dict[str, Any]:
        """Generate report on improvements"""
        variants = self.variants.get(agent_name, [])
        
        if not variants or all(v.executions < 10 for v in variants):
            return {"message": "Need more data (min 10 executions per variant)"}
        
        best = self.get_best_variant(agent_name)
        
        if not best:
            return {"message": "No clear winner yet"}
        
        return {
            "agent_name": agent_name,
            "best_variant": {
                "variant_id": best.variant_id,
                "executions": best.executions,
                "avg_quality": best.avg_quality_score,
                "success_rate": best.success_rate * 100,
                "avg_duration_s": best.avg_duration_ms / 1000
            },
            "variants_tested": len(variants),
            "total_executions": sum(v.executions for v in variants),
            "recommendation": "Deploy best variant to production" if best.executions > 50 else "Continue testing"
        }
