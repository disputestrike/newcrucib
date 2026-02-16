"""
Speed benchmark system for comparing against competitors.
Measures:
- Time to first code
- Time to complete build
- Token usage
- Success rate
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class BenchmarkResult:
    """Result from a single benchmark run"""
    prompt: str
    tool: str  # "newcrucib-v2", "manus", "cursor", etc.
    start_time: float
    end_time: float
    success: bool
    tokens_used: int
    files_generated: int
    build_validated: bool
    quality_score: float
    error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def duration_minutes(self) -> float:
        return self.duration_seconds / 60
    
    def to_dict(self) -> Dict:
        return {
            "prompt": self.prompt,
            "tool": self.tool,
            "duration_seconds": self.duration_seconds,
            "duration_minutes": round(self.duration_minutes, 2),
            "success": self.success,
            "tokens_used": self.tokens_used,
            "files_generated": self.files_generated,
            "build_validated": self.build_validated,
            "quality_score": self.quality_score,
            "error": self.error
        }


class SpeedBenchmark:
    """Run speed benchmarks across multiple prompts"""
    
    # Standard benchmark prompts
    BENCHMARK_PROMPTS = [
        # Simple (30s-2min expected)
        "Build a simple todo app with React",
        "Create a landing page for a SaaS product",
        "Build a contact form with validation",
        
        # Medium (2-5min expected)
        "Build a blog with React and FastAPI backend",
        "Create a dashboard with charts and user auth",
        "Build an e-commerce product catalog",
        
        # Complex (5-10min expected)
        "Build a full-stack task management app with teams, projects, and real-time updates",
        "Create a SaaS boilerplate with authentication, payments, and admin dashboard",
        "Build a social media feed with posts, comments, likes, and notifications"
    ]
    
    def __init__(self, orchestrator):
        """
        Initialize speed benchmark.
        
        Args:
            orchestrator: The orchestration system to use for benchmarking.
                         Can be any callable that accepts user_prompt and returns results.
        """
        self.orchestrator = orchestrator
        self.results: List[BenchmarkResult] = []
    
    async def run_benchmark_suite(
        self,
        prompts: Optional[List[str]] = None,
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Run complete benchmark suite.
        
        Args:
            prompts: List of prompts to test (defaults to BENCHMARK_PROMPTS)
            iterations: How many times to run each prompt
            
        Returns:
            Complete benchmark report with statistics
        """
        prompts = prompts or self.BENCHMARK_PROMPTS
        
        print(f"🏃 Running benchmark suite: {len(prompts)} prompts × {iterations} iterations")
        
        for iteration in range(iterations):
            print(f"\n📊 Iteration {iteration + 1}/{iterations}")
            
            for i, prompt in enumerate(prompts):
                print(f"\n[{i+1}/{len(prompts)}] Testing: {prompt[:50]}...")
                
                result = await self._benchmark_single_prompt(prompt)
                self.results.append(result)
                
                if result.success:
                    print(f"✅ Success in {result.duration_minutes:.2f}min (Quality: {result.quality_score}/100)")
                else:
                    print(f"❌ Failed: {result.error}")
        
        return self._generate_report()
    
    async def _benchmark_single_prompt(self, prompt: str) -> BenchmarkResult:
        """Benchmark a single prompt"""
        start_time = time.time()
        
        try:
            # Run generation using the orchestrator
            # The orchestrator should be a callable that can handle the prompt
            if callable(self.orchestrator):
                result = await self.orchestrator(prompt)
            else:
                # If orchestrator has execute_workflow method
                result = await self.orchestrator.execute_workflow(
                    user_prompt=prompt,
                    workflow="full_stack",
                    validate_code=True,
                    score_quality=True
                )
            
            end_time = time.time()
            
            # Extract metrics (handle different result formats)
            if isinstance(result, dict):
                success = result.get("success", False)
                tokens = result.get("metrics", {}).get("tokens", {}).get("total", 0)
                files = result.get("summary", {}).get("files_generated", 0)
                build_ok = result.get("validations", {}).get("frontend", {}).get("overall_valid", False)
                quality = result.get("validations", {}).get("quality", {}).get("overall_score", 0)
            else:
                # Default values if result format is unexpected
                success = True
                tokens = 0
                files = 0
                build_ok = False
                quality = 0
            
            return BenchmarkResult(
                prompt=prompt,
                tool="newcrucib-v2",
                start_time=start_time,
                end_time=end_time,
                success=success,
                tokens_used=tokens,
                files_generated=files,
                build_validated=build_ok,
                quality_score=quality
            )
            
        except Exception as e:
            end_time = time.time()
            return BenchmarkResult(
                prompt=prompt,
                tool="newcrucib-v2",
                start_time=start_time,
                end_time=end_time,
                success=False,
                tokens_used=0,
                files_generated=0,
                build_validated=False,
                quality_score=0,
                error=str(e)
            )
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        if not successful:
            return {"error": "All benchmarks failed", "failed": len(failed)}
        
        # Calculate statistics
        durations = [r.duration_seconds for r in successful]
        tokens = [r.tokens_used for r in successful]
        quality_scores = [r.quality_score for r in successful]
        
        avg_duration = sum(durations) / len(durations)
        avg_tokens = sum(tokens) / len(tokens)
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Group by complexity
        simple = [r for r in successful if r.duration_seconds < 120]
        medium = [r for r in successful if 120 <= r.duration_seconds < 300]
        complex_runs = [r for r in successful if r.duration_seconds >= 300]
        
        return {
            "summary": {
                "total_runs": len(self.results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(self.results) * 100,
                "avg_duration_seconds": avg_duration,
                "avg_duration_minutes": avg_duration / 60,
                "avg_tokens": avg_tokens,
                "avg_quality_score": avg_quality,
                "avg_cost_per_build": (avg_tokens / 1000000) * 10  # $10/1M tokens
            },
            "by_complexity": {
                "simple": {
                    "count": len(simple),
                    "avg_duration": sum(r.duration_seconds for r in simple) / len(simple) if simple else 0
                },
                "medium": {
                    "count": len(medium),
                    "avg_duration": sum(r.duration_seconds for r in medium) / len(medium) if medium else 0
                },
                "complex": {
                    "count": len(complex_runs),
                    "avg_duration": sum(r.duration_seconds for r in complex_runs) / len(complex_runs) if complex_runs else 0
                }
            },
            "detailed_results": [r.to_dict() for r in self.results]
        }
    
    def save_report(self, filepath: str = "benchmark_results.json") -> str:
        """Save benchmark report to file"""
        report = self._generate_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to {filepath}")
        return filepath
