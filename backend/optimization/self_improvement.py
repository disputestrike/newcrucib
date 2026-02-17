"""
Self-Improvement System - automatically optimize agent prompts and parameters.
"""

from typing import Dict, Any, List
import random
from dataclasses import dataclass

@dataclass
class PromptVariant:
    """A variant of a system prompt being tested"""
    id: str
    agent_name: str
    prompt: str
    executions: int = 0
    successes: int = 0
    avg_quality: float = 0
    avg_duration: float = 0
    
    @property
    def success_rate(self) -> float:
        if self.executions == 0:
            return 0
        return (self.successes / self.executions) * 100
    
    @property
    def score(self) -> float:
        """Combined score: success_rate * 0.5 + quality * 0.5"""
        return (self.success_rate / 100) * 0.5 + (self.avg_quality / 100) * 0.5

class SelfImprovement:
    """A/B testing and automatic optimization"""
    
    def __init__(self):
        self.variants: Dict[str, List[PromptVariant]] = {}
    
    def add_variant(self, agent_name: str, variant: PromptVariant):
        """Add a prompt variant to test"""
        if agent_name not in self.variants:
            self.variants[agent_name] = []
        
        self.variants[agent_name].append(variant)
    
    def get_prompt(self, agent_name: str) -> PromptVariant:
        """Get prompt variant to use (epsilon-greedy)"""
        if agent_name not in self.variants:
            return None
        
        variants = self.variants[agent_name]
        
        # Exploration vs exploitation (90% best, 10% random)
        if random.random() < 0.9 and any(v.executions > 10 for v in variants):
            # Use best variant
            best = max(variants, key=lambda v: v.score if v.executions > 10 else 0)
            return best
        else:
            # Random exploration
            return random.choice(variants)
    
    def record_result(
        self,
        variant_id: str,
        success: bool,
        quality_score: float,
        duration: float
    ):
        """Record result of using a variant"""
        # Find variant
        variant = None
        for variants in self.variants.values():
            for v in variants:
                if v.id == variant_id:
                    variant = v
                    break
        
        if not variant:
            return
        
        # Update metrics
        variant.executions += 1
        if success:
            variant.successes += 1
        
        n = variant.executions
        variant.avg_quality = (variant.avg_quality * (n-1) + quality_score) / n
        variant.avg_duration = (variant.avg_duration * (n-1) + duration) / n
    
    def get_best_prompts(self) -> Dict[str, PromptVariant]:
        """Get best prompt for each agent"""
        best = {}
        
        for agent_name, variants in self.variants.items():
            # Only consider variants with >20 executions
            eligible = [v for v in variants if v.executions > 20]
            
            if eligible:
                best[agent_name] = max(eligible, key=lambda v: v.score)
        
        return best
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get optimization report"""
        best_prompts = self.get_best_prompts()
        
        improvements = []
        for agent_name, best_variant in best_prompts.items():
            variants = self.variants[agent_name]
            baseline = min(variants, key=lambda v: v.id)  # First variant is baseline
            
            if baseline.executions > 10 and best_variant.id != baseline.id:
                improvement = (best_variant.score - baseline.score) / baseline.score * 100
                improvements.append({
                    "agent": agent_name,
                    "baseline_score": baseline.score,
                    "best_score": best_variant.score,
                    "improvement_percent": round(improvement, 1)
                })
        
        return {
            "agents_optimized": len(best_prompts),
            "improvements": improvements,
            "avg_improvement": sum(i["improvement_percent"] for i in improvements) / len(improvements) if improvements else 0
        }
