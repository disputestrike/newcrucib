"""
Orchestration V2 - Production-ready orchestration engine
Specialized agent architecture with validation and quality scoring.
"""

from enum import Enum
from typing import List, Dict, Any, Union
import logging
import asyncio

from backend.agents.registry import AgentRegistry
from backend.code_executor import CodeExecutor
from backend.syntax_validator import SyntaxValidator
from backend.quality_scorer import QualityScorer
from backend.test_runner import TestRunner

logger = logging.getLogger(__name__)


class WorkflowPresets(str, Enum):
    """Predefined workflows for common use cases"""
    FULL_STACK_APP = "full_stack"
    FRONTEND_ONLY = "frontend_only"
    BACKEND_API = "backend_api"
    LANDING_PAGE = "landing_page"
    DOCUMENTATION = "documentation_only"
    
    @staticmethod
    def get_workflow(preset: str) -> List[str]:
        """Get agent list for a preset workflow"""
        workflows = {
            "full_stack": [
                "PlannerAgent",
                "StackSelectorAgent",
                "DesignAgent",
                "DatabaseAgent",
                "BackendAgent",
                "FrontendAgent",
                "TestGenerationAgent",
                "SecurityAgent",
                "DeploymentAgent",
                "DocumentationAgent"
            ],
            "frontend_only": [
                "PlannerAgent",
                "StackSelectorAgent",
                "DesignAgent",
                "FrontendAgent",
                "TestGenerationAgent",
                "DeploymentAgent",
                "DocumentationAgent"
            ],
            "backend_api": [
                "PlannerAgent",
                "StackSelectorAgent",
                "DatabaseAgent",
                "BackendAgent",
                "TestGenerationAgent",
                "SecurityAgent",
                "DeploymentAgent",
                "DocumentationAgent"
            ],
            "landing_page": [
                "PlannerAgent",
                "DesignAgent",
                "FrontendAgent",
                "DeploymentAgent"
            ],
            "documentation_only": [
                "PlannerAgent",
                "DocumentationAgent"
            ]
        }
        return workflows.get(preset, workflows["full_stack"])


class OrchestrationV2:
    """
    New orchestration engine with validation and quality scoring.
    """
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        self.llm_client = llm_client
        self.config = config
        self.executor = CodeExecutor(timeout=config.get("timeout", 300))
        self.validator = SyntaxValidator()
        self.scorer = QualityScorer()
        self.test_runner = TestRunner(self.executor)
        self.metrics = []
    
    async def execute_workflow(
        self,
        user_prompt: str,
        workflow: Union[List[str], str],
        validate_code: bool = True,
        run_tests: bool = False,
        score_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow with optional validation.
        
        Args:
            user_prompt: User's input
            workflow: List of agent names OR preset name (e.g., "full_stack")
            validate_code: Run build/syntax validation
            run_tests: Execute generated tests
            score_quality: Calculate quality scores
            
        Returns:
            {
                "success": bool,
                "results": {agent_name: output},
                "validations": {
                    "frontend": {...},
                    "backend": {...},
                    "quality": {...},
                    "tests": {...}
                },
                "metrics": {
                    "agents": [agent metrics],
                    "tokens": {"total": X, "by_agent": {...}},
                    "timing": {"total_seconds": X, "by_agent": {...}}
                },
                "summary": {
                    "project_type": "Full-stack web app",
                    "tech_stack": "React + FastAPI + PostgreSQL",
                    "files_generated": 42,
                    "quality_score": 85,
                    "build_status": "success",
                    "recommendations": [...]
                }
            }
        """
        logger.info(f"Starting workflow execution: {workflow}")
        
        # Get workflow agents
        if isinstance(workflow, str):
            agents = WorkflowPresets.get_workflow(workflow)
        else:
            agents = workflow
        
        context = {"user_prompt": user_prompt}
        results = {}
        
        # Execute agents sequentially
        for agent_name in agents:
            try:
                print(f"🤖 Executing {agent_name}...")
                agent = AgentRegistry.create_instance(
                    agent_name,
                    self.llm_client,
                    self.config
                )
                
                result = await agent.run(context)
                results[agent_name] = result
                context[agent_name] = result
                self.metrics.append(agent.get_metrics())
                
                print(f"✅ {agent_name} completed ({agent.get_metrics()['duration_ms']:.0f}ms)")
                
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                print(f"❌ {agent_name} failed: {e}")
                results[agent_name] = {"error": str(e)}
                # Add error metrics
                self.metrics.append({
                    "agent_name": agent_name,
                    "success": False,
                    "duration_ms": 0,
                    "tokens_used": 0,
                    "error": str(e)
                })
                break
        
        # Validation phase
        validations = {}
        
        if validate_code:
            validations = await self._validate_all(results, context)
        
        if run_tests and "TestGenerationAgent" in results:
            validations["tests"] = await self._run_tests(results)
        
        if score_quality:
            validations["quality"] = await self._score_quality(results, context)
        
        # Generate summary
        summary = self._generate_summary(results, validations, context)
        
        return {
            "success": all(m["success"] for m in self.metrics),
            "results": results,
            "validations": validations,
            "metrics": self._aggregate_metrics(),
            "summary": summary
        }
    
    async def _validate_all(
        self,
        results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run all validations"""
        validations = {}
        
        # Frontend validation
        if "FrontendAgent" in results:
            frontend = results["FrontendAgent"]
            if frontend.get("files"):
                print("🔍 Validating frontend...")
                
                framework = context.get("StackSelectorAgent", {}).get("frontend", {}).get("framework", "React")
                
                # Syntax check
                main_file = frontend["files"].get("src/App.tsx") or frontend["files"].get("src/App.jsx")
                if main_file:
                    syntax = self.validator.validate_react_component(main_file)
                else:
                    syntax = {"valid": False, "error": "No main component found"}
                
                # Build validation (if syntax ok)
                if syntax["valid"]:
                    build = await self.executor.validate_frontend(frontend["files"], framework)
                else:
                    build = {"skipped": True, "reason": "Syntax errors"}
                
                validations["frontend"] = {
                    "syntax": syntax,
                    "build": build,
                    "overall_valid": syntax["valid"] and build.get("valid", False)
                }
        
        # Backend validation
        if "BackendAgent" in results:
            backend = results["BackendAgent"]
            if backend.get("files"):
                print("🔍 Validating backend...")
                
                language = context.get("StackSelectorAgent", {}).get("backend", {}).get("language", "Python")
                validation = await self.executor.validate_backend(backend["files"], language)
                validations["backend"] = validation
        
        return validations
    
    async def _run_tests(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Run generated tests"""
        print("🧪 Running tests...")
        
        test_agent = results.get("TestGenerationAgent", {})
        if not test_agent.get("test_files"):
            return {"skipped": True, "reason": "No tests generated"}
        
        framework = test_agent.get("test_framework", "pytest")
        
        if "pytest" in framework.lower():
            return await self.test_runner.run_python_tests(test_agent["test_files"])
        else:
            return await self.test_runner.run_javascript_tests(test_agent["test_files"])
    
    async def _score_quality(
        self,
        results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Score code quality"""
        print("📊 Scoring quality...")
        
        all_files = {}
        
        # Collect all code files
        if "FrontendAgent" in results:
            all_files.update(results["FrontendAgent"].get("files", {}))
        
        if "BackendAgent" in results:
            all_files.update(results["BackendAgent"].get("files", {}))
        
        if not all_files:
            return {"skipped": True, "reason": "No code generated"}
        
        language = context.get("StackSelectorAgent", {}).get("backend", {}).get("language", "Python")
        return self.scorer.score_code(all_files, language)
    
    def _aggregate_metrics(self) -> Dict[str, Any]:
        """Aggregate all agent metrics"""
        total_tokens = sum(m["tokens_used"] for m in self.metrics)
        total_duration = sum(m["duration_ms"] for m in self.metrics)
        
        by_agent_tokens = {m["agent_name"]: m["tokens_used"] for m in self.metrics}
        by_agent_timing = {m["agent_name"]: m["duration_ms"] for m in self.metrics}
        
        return {
            "agents": self.metrics,
            "tokens": {
                "total": total_tokens,
                "by_agent": by_agent_tokens
            },
            "timing": {
                "total_seconds": total_duration / 1000,
                "by_agent_ms": by_agent_timing
            }
        }
    
    def _generate_summary(
        self,
        results: Dict[str, Any],
        validations: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable summary"""
        stack = context.get("StackSelectorAgent", {})
        planner = context.get("PlannerAgent", {})
        quality = validations.get("quality", {})
        
        # Determine project type
        has_frontend = "FrontendAgent" in results
        has_backend = "BackendAgent" in results
        
        if has_frontend and has_backend:
            project_type = "Full-stack web application"
        elif has_frontend:
            project_type = "Frontend application"
        elif has_backend:
            project_type = "Backend API"
        else:
            project_type = "Documentation"
        
        # Build tech stack string
        tech_parts = []
        if has_frontend:
            tech_parts.append(stack.get("frontend", {}).get("framework", "React"))
        if has_backend:
            tech_parts.append(stack.get("backend", {}).get("framework", "FastAPI"))
        if "DatabaseAgent" in results:
            tech_parts.append(stack.get("database", {}).get("primary", "PostgreSQL"))
        
        tech_stack = " + ".join(tech_parts) if tech_parts else "Unknown"
        
        # Count files
        files_count = 0
        for agent_result in results.values():
            if isinstance(agent_result, dict):
                files_count += len(agent_result.get("files", {}))
        
        # Build status
        frontend_valid = validations.get("frontend", {}).get("overall_valid", None)
        backend_valid = validations.get("backend", {}).get("valid", None)
        
        if frontend_valid is False or backend_valid is False:
            build_status = "failed"
        elif frontend_valid or backend_valid:
            build_status = "success"
        else:
            build_status = "not_validated"
        
        # Recommendations
        recommendations = []
        
        if quality.get("overall_score", 100) < 70:
            recommendations.append("Consider refactoring for better code quality")
        
        if not validations.get("tests"):
            recommendations.append("Add comprehensive test coverage")
        
        if quality.get("metrics", {}).get("security", 100) < 70:
            recommendations.append("Review security vulnerabilities")
        
        return {
            "project_type": project_type,
            "tech_stack": tech_stack,
            "complexity": planner.get("complexity", "unknown"),
            "estimated_duration": planner.get("estimated_duration", "unknown"),
            "files_generated": files_count,
            "quality_score": quality.get("overall_score"),
            "build_status": build_status,
            "tests_passed": validations.get("tests", {}).get("passed"),
            "recommendations": recommendations
        }
    
    async def execute_parallel_agents(
        self,
        agent_names: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute multiple independent agents in parallel"""
        tasks = []
        for agent_name in agent_names:
            agent = AgentRegistry.create_instance(agent_name, self.llm_client, self.config)
            tasks.append(agent.run(context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            agent_names[i]: results[i] if not isinstance(results[i], Exception) else {"error": str(results[i])}
            for i in range(len(agent_names))
        }
