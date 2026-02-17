"""
Tests for Phase 4 Enterprise Features:
- Agent Marketplace
- Team Memory
- Observability Dashboard
- Self-Improvement System
"""
import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.marketplace.agent_marketplace import AgentMarketplace, CustomAgent
from backend.learning.team_memory import TeamMemory, BuildMemory
from backend.observability.agent_dashboard import AgentDashboard, AgentMetric
from backend.learning.self_improvement import SelfImprovement, PromptVariant


class TestAgentMarketplace:
    """Test Agent Marketplace functionality"""
    
    @pytest.fixture
    def temp_marketplace(self):
        """Create a temporary marketplace for testing"""
        temp_dir = tempfile.mkdtemp()
        marketplace = AgentMarketplace(storage_path=temp_dir)
        yield marketplace
        shutil.rmtree(temp_dir)
    
    def test_create_agent(self, temp_marketplace):
        """Test creating a custom agent"""
        agent = temp_marketplace.create_agent(
            name="Test Agent",
            description="A test agent",
            author="test_user",
            category="frontend",
            system_prompt="You are a helpful agent",
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )
        
        assert agent.name == "Test Agent"
        assert agent.author == "test_user"
        assert agent.category == "frontend"
        assert agent.version == "1.0.0"
        assert agent.downloads == 0
        assert agent.rating == 0.0
        assert agent.id in temp_marketplace.agents
    
    def test_search_agents_by_query(self, temp_marketplace):
        """Test searching agents by query"""
        # Create multiple agents
        temp_marketplace.create_agent(
            name="Frontend Builder",
            description="Builds frontend components",
            author="user1",
            category="frontend",
            system_prompt="Build frontend",
            input_schema={},
            output_schema={}
        )
        temp_marketplace.create_agent(
            name="Backend API",
            description="Creates backend APIs",
            author="user2",
            category="backend",
            system_prompt="Build backend",
            input_schema={},
            output_schema={}
        )
        
        # Search for frontend
        results = temp_marketplace.search_agents(query="frontend")
        assert len(results) == 1
        assert results[0].name == "Frontend Builder"
    
    def test_search_agents_by_category(self, temp_marketplace):
        """Test searching agents by category"""
        temp_marketplace.create_agent(
            name="Agent 1",
            description="Test",
            author="user1",
            category="frontend",
            system_prompt="Test",
            input_schema={},
            output_schema={}
        )
        temp_marketplace.create_agent(
            name="Agent 2",
            description="Test",
            author="user2",
            category="backend",
            system_prompt="Test",
            input_schema={},
            output_schema={}
        )
        
        results = temp_marketplace.search_agents(category="backend")
        assert len(results) == 1
        assert results[0].category == "backend"
    
    def test_install_agent(self, temp_marketplace):
        """Test installing an agent"""
        agent = temp_marketplace.create_agent(
            name="Installable Agent",
            description="Test",
            author="user1",
            category="frontend",
            system_prompt="Test",
            input_schema={},
            output_schema={}
        )
        
        result = temp_marketplace.install_agent(agent.id, "test_user")
        
        assert result["success"] is True
        assert agent.downloads == 1
        assert "Agent 'Installable Agent' installed successfully" in result["message"]
    
    def test_install_nonexistent_agent(self, temp_marketplace):
        """Test installing a non-existent agent"""
        result = temp_marketplace.install_agent("nonexistent-id", "test_user")
        
        assert result["success"] is False
        assert "Agent not found" in result["error"]
    
    def test_rate_agent(self, temp_marketplace):
        """Test rating an agent"""
        agent = temp_marketplace.create_agent(
            name="Rateable Agent",
            description="Test",
            author="user1",
            category="frontend",
            system_prompt="Test",
            input_schema={},
            output_schema={}
        )
        
        result = temp_marketplace.rate_agent(agent.id, 4.5, "test_user")
        
        assert result["success"] is True
        assert agent.rating > 0
        assert result["new_rating"] == agent.rating
    
    def test_agent_persistence(self, temp_marketplace):
        """Test that agents are persisted to disk"""
        agent = temp_marketplace.create_agent(
            name="Persistent Agent",
            description="Test",
            author="user1",
            category="frontend",
            system_prompt="Test",
            input_schema={},
            output_schema={}
        )
        
        # Create new marketplace instance with same path
        new_marketplace = AgentMarketplace(storage_path=temp_marketplace.storage_path)
        
        assert agent.id in new_marketplace.agents
        assert new_marketplace.agents[agent.id].name == "Persistent Agent"


class TestTeamMemory:
    """Test Team Memory functionality"""
    
    @pytest.fixture
    def temp_memory(self):
        """Create a temporary team memory for testing"""
        temp_dir = tempfile.mkdtemp()
        memory = TeamMemory(storage_path=temp_dir)
        yield memory
        shutil.rmtree(temp_dir)
    
    def test_record_build(self, temp_memory):
        """Test recording a build"""
        result = {
            "prompt": "Build a todo app",
            "workflow": "fullstack",
            "success": True,
            "summary": {
                "tech_stack": {
                    "frontend": {"framework": "React"},
                    "backend": {"framework": "FastAPI"}
                }
            },
            "validations": {
                "quality": {"overall_score": 85}
            },
            "metrics": {
                "timing": {"total_seconds": 120}
            },
            "results": {
                "frontend": {},
                "backend": {}
            }
        }
        
        memory = temp_memory.record_build(
            build_id="build-1",
            user_id="user-1",
            team_id="team-1",
            result=result
        )
        
        assert memory.build_id == "build-1"
        assert memory.user_id == "user-1"
        assert memory.team_id == "team-1"
        assert memory.prompt == "Build a todo app"
        assert memory.quality_score == 85
        assert memory.build_successful is True
        assert len(temp_memory.memories) == 1
    
    def test_get_team_insights_no_history(self, temp_memory):
        """Test getting insights with no build history"""
        insights = temp_memory.get_team_insights("team-1")
        
        assert insights["message"] == "No build history yet"
    
    def test_get_team_insights_with_history(self, temp_memory):
        """Test getting team insights with build history"""
        # Record multiple builds
        for i in range(3):
            result = {
                "prompt": f"Build app {i}",
                "workflow": "fullstack",
                "success": True,
                "summary": {
                    "tech_stack": {
                        "frontend": {"framework": "React"},
                        "backend": {"framework": "FastAPI"}
                    }
                },
                "validations": {
                    "quality": {"overall_score": 80 + i}
                },
                "metrics": {
                    "timing": {"total_seconds": 100 + i * 10}
                },
                "results": {
                    "frontend": {},
                    "backend": {}
                }
            }
            temp_memory.record_build(f"build-{i}", "user-1", "team-1", result)
        
        insights = temp_memory.get_team_insights("team-1")
        
        assert insights["total_builds"] == 3
        assert insights["successful_builds"] == 3
        assert insights["success_rate"] == 100
        assert insights["avg_quality_score"] > 0
        assert "preferred_tech" in insights
        assert "most_used_agents" in insights
    
    def test_suggest_stack_no_history(self, temp_memory):
        """Test tech stack suggestion with no history"""
        suggestion = temp_memory.suggest_stack("team-1", "Build a web app")
        
        assert suggestion["suggestion"] == "default"
        assert "Not enough build history" in suggestion["reason"]
    
    def test_suggest_stack_with_history(self, temp_memory):
        """Test tech stack suggestion with history"""
        # Record multiple similar builds
        for i in range(3):
            result = {
                "prompt": f"Build web application {i}",
                "workflow": "fullstack",
                "success": True,
                "summary": {
                    "tech_stack": {
                        "frontend": {"framework": "React"},
                        "backend": {"framework": "FastAPI"}
                    }
                },
                "validations": {
                    "quality": {"overall_score": 85}
                },
                "metrics": {
                    "timing": {"total_seconds": 120}
                },
                "results": {}
            }
            temp_memory.record_build(f"build-{i}", "user-1", "team-1", result)
        
        suggestion = temp_memory.suggest_stack("team-1", "Build a web portal")
        
        assert suggestion["suggestion"] == "learned"
        assert "tech_stack" in suggestion
    
    def test_get_improvement_recommendations_insufficient_data(self, temp_memory):
        """Test recommendations with insufficient data"""
        recommendations = temp_memory.get_improvement_recommendations("team-1")
        
        assert len(recommendations) == 1
        assert "Build more projects" in recommendations[0]
    
    def test_get_improvement_recommendations_quality_issues(self, temp_memory):
        """Test recommendations for quality issues"""
        # Record builds with low quality
        for i in range(6):
            result = {
                "prompt": f"Build {i}",
                "workflow": "fullstack",
                "success": True,
                "summary": {"tech_stack": {}},
                "validations": {
                    "quality": {"overall_score": 60}  # Low quality
                },
                "metrics": {
                    "timing": {"total_seconds": 100}
                },
                "results": {}
            }
            temp_memory.record_build(f"build-{i}", "user-1", "team-1", result)
        
        recommendations = temp_memory.get_improvement_recommendations("team-1")
        
        assert any("quality" in r.lower() for r in recommendations)


class TestAgentDashboard:
    """Test Agent Dashboard functionality"""
    
    @pytest.fixture
    def dashboard(self):
        """Create a dashboard for testing"""
        return AgentDashboard()
    
    def test_record_execution(self, dashboard):
        """Test recording agent execution"""
        metrics = {
            "agent_name": "TestAgent",
            "duration_ms": 1000,
            "tokens_used": 500,
            "success": True
        }
        
        dashboard.record_execution(metrics)
        
        assert len(dashboard.metrics) == 1
        assert dashboard.metrics[0].agent_name == "TestAgent"
        assert dashboard.metrics[0].duration_ms == 1000
        assert dashboard.metrics[0].tokens_used == 500
        assert dashboard.metrics[0].success is True
    
    def test_get_dashboard_data_no_data(self, dashboard):
        """Test getting dashboard data with no metrics"""
        data = dashboard.get_dashboard_data()
        
        assert data["message"] == "No recent data"
    
    def test_get_dashboard_data_with_metrics(self, dashboard):
        """Test getting dashboard data with metrics"""
        # Record multiple executions
        for i in range(5):
            metrics = {
                "agent_name": "Agent1",
                "duration_ms": 1000 + i * 100,
                "tokens_used": 500,
                "success": True
            }
            dashboard.record_execution(metrics)
        
        # Record some failures
        for i in range(2):
            metrics = {
                "agent_name": "Agent2",
                "duration_ms": 2000,
                "tokens_used": 1000,
                "success": False,
                "error": "Test error"
            }
            dashboard.record_execution(metrics)
        
        data = dashboard.get_dashboard_data(hours=24)
        
        assert "overall" in data
        assert data["overall"]["total_executions"] == 7
        assert "by_agent" in data
        assert "Agent1" in data["by_agent"]
        assert "Agent2" in data["by_agent"]
        assert data["by_agent"]["Agent1"]["success_rate"] == 100
        assert data["by_agent"]["Agent2"]["success_rate"] == 0
    
    def test_recommendations_slow_agents(self, dashboard):
        """Test recommendations for slow agents"""
        metrics = {
            "agent_name": "SlowAgent",
            "duration_ms": 40000,  # 40 seconds
            "tokens_used": 500,
            "success": True
        }
        dashboard.record_execution(metrics)
        
        data = dashboard.get_dashboard_data(hours=24)
        
        assert "recommendations" in data
        assert any("slow" in r.lower() for r in data["recommendations"])
    
    def test_recommendations_failing_agents(self, dashboard):
        """Test recommendations for failing agents"""
        # Record mostly failures
        for i in range(10):
            metrics = {
                "agent_name": "FailingAgent",
                "duration_ms": 1000,
                "tokens_used": 500,
                "success": i < 2  # Only 2 successes
            }
            dashboard.record_execution(metrics)
        
        data = dashboard.get_dashboard_data(hours=24)
        
        assert "recommendations" in data
        assert any("reliability" in r.lower() for r in data["recommendations"])


class TestSelfImprovement:
    """Test Self-Improvement System functionality"""
    
    @pytest.fixture
    def improvement(self):
        """Create a self-improvement system for testing"""
        return SelfImprovement()
    
    def test_create_prompt_variant(self, improvement):
        """Test creating a prompt variant"""
        variant = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Improved system prompt",
            variant_name="variant_a"
        )
        
        assert variant.agent_name == "TestAgent"
        assert variant.system_prompt == "Improved system prompt"
        assert variant.executions == 0
        assert "TestAgent" in improvement.variants
        assert len(improvement.variants["TestAgent"]) == 1
    
    def test_select_variant_no_variants(self, improvement):
        """Test selecting variant with no variants available"""
        variant_id = improvement.select_variant("NonExistentAgent")
        
        assert variant_id == "default"
    
    def test_select_variant_with_variants(self, improvement):
        """Test selecting variant with available variants"""
        variant = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Test prompt",
            variant_name="v1"
        )
        
        # Record some good results to make it exploitable
        for i in range(20):
            improvement.record_result(
                agent_name="TestAgent",
                variant_id=variant.variant_id,
                quality_score=90,
                duration_ms=1000,
                success=True
            )
        
        # Should mostly select the best variant (90% exploitation)
        selected = improvement.select_variant("TestAgent")
        # Should be either the variant or "default" (10% exploration)
        assert selected == variant.variant_id or selected == "default"
    
    def test_record_result(self, improvement):
        """Test recording variant results"""
        variant = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Test prompt",
            variant_name="v1"
        )
        
        improvement.record_result(
            agent_name="TestAgent",
            variant_id=variant.variant_id,
            quality_score=85,
            duration_ms=1500,
            success=True
        )
        
        assert variant.executions == 1
        assert variant.avg_quality_score == 85
        assert variant.avg_duration_ms == 1500
        assert variant.success_rate == 1.0
    
    def test_get_best_variant_insufficient_data(self, improvement):
        """Test getting best variant with insufficient data"""
        variant = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Test prompt",
            variant_name="v1"
        )
        
        # Record only a few results
        for i in range(5):
            improvement.record_result(
                agent_name="TestAgent",
                variant_id=variant.variant_id,
                quality_score=85,
                duration_ms=1000,
                success=True
            )
        
        best = improvement.get_best_variant("TestAgent")
        # Should still return None or handle gracefully due to minimum data requirement
        assert best is None or best.executions < 10
    
    def test_get_best_variant_with_data(self, improvement):
        """Test getting best variant with sufficient data"""
        variant1 = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Variant 1",
            variant_name="v1"
        )
        variant2 = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Variant 2",
            variant_name="v2"
        )
        
        # Record better results for variant1
        for i in range(15):
            improvement.record_result(
                agent_name="TestAgent",
                variant_id=variant1.variant_id,
                quality_score=90,
                duration_ms=1000,
                success=True
            )
        
        # Record worse results for variant2
        for i in range(15):
            improvement.record_result(
                agent_name="TestAgent",
                variant_id=variant2.variant_id,
                quality_score=70,
                duration_ms=2000,
                success=True
            )
        
        best = improvement.get_best_variant("TestAgent")
        
        assert best is not None
        assert best.variant_id == variant1.variant_id
    
    def test_generate_improvement_report_no_data(self, improvement):
        """Test improvement report with no data"""
        report = improvement.generate_improvement_report("TestAgent")
        
        assert "message" in report
    
    def test_generate_improvement_report_with_data(self, improvement):
        """Test improvement report with sufficient data"""
        variant = improvement.create_prompt_variant(
            agent_name="TestAgent",
            variant_prompt="Test prompt",
            variant_name="v1"
        )
        
        # Record sufficient data
        for i in range(60):
            improvement.record_result(
                agent_name="TestAgent",
                variant_id=variant.variant_id,
                quality_score=85,
                duration_ms=1500,
                success=True
            )
        
        report = improvement.generate_improvement_report("TestAgent")
        
        assert "agent_name" in report
        assert "best_variant" in report
        assert report["agent_name"] == "TestAgent"
        assert report["best_variant"]["executions"] == 60
        assert "Deploy best variant to production" in report["recommendation"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
