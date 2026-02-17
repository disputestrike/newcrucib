"""
Tests for Phase 4: Enterprise Features
- Agent Marketplace
- Team Memory
- Observability Dashboard
- Self-Improvement System
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from marketplace.agent_store import AgentMarketplace, CustomAgentDefinition
from memory.team_memory import TeamMemory, BuildHistory
from observability.dashboard import Dashboard
from optimization.self_improvement import SelfImprovement, PromptVariant


class TestAgentMarketplace:
    """Tests for Agent Marketplace"""
    
    @pytest.fixture
    def marketplace(self, tmp_path):
        """Create a marketplace instance with temporary storage"""
        return AgentMarketplace(store_path=str(tmp_path / "marketplace"))
    
    def test_publish_agent(self, marketplace):
        """Test publishing a custom agent"""
        definition = CustomAgentDefinition(
            name="TestAgent",
            author="TestAuthor",
            description="A test agent",
            version="1.0.0",
            category="utility",
            system_prompt="You are a test agent.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            dependencies=[]
        )
        
        result = marketplace.publish_agent(definition)
        
        assert result["success"] is True
        assert result["agent_name"] == "TestAgent"
        assert "published successfully" in result["message"]
    
    def test_publish_duplicate_agent(self, marketplace):
        """Test that publishing a duplicate agent fails"""
        definition = CustomAgentDefinition(
            name="TestAgent",
            author="TestAuthor",
            description="A test agent",
            version="1.0.0",
            category="utility",
            system_prompt="You are a test agent.",
            input_schema={},
            output_schema={},
            dependencies=[]
        )
        
        marketplace.publish_agent(definition)
        result = marketplace.publish_agent(definition)
        
        assert result["success"] is False
        assert "already exists" in result["error"]
    
    def test_install_agent(self, marketplace):
        """Test installing an agent from marketplace"""
        # First publish
        definition = CustomAgentDefinition(
            name="InstallAgent",
            author="Author",
            description="Test",
            version="1.0.0",
            category="utility",
            system_prompt="Test prompt",
            input_schema={},
            output_schema={},
            dependencies=[]
        )
        marketplace.publish_agent(definition)
        
        # Then install
        result = marketplace.install_agent("InstallAgent")
        
        assert result["success"] is True
        assert "installed successfully" in result["message"]
    
    def test_install_nonexistent_agent(self, marketplace):
        """Test that installing a non-existent agent fails"""
        result = marketplace.install_agent("NonExistentAgent")
        
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_list_agents(self, marketplace):
        """Test listing all agents"""
        # Publish some agents
        for i in range(3):
            definition = CustomAgentDefinition(
                name=f"Agent{i}",
                author="Author",
                description=f"Agent {i}",
                version="1.0.0",
                category="utility",
                system_prompt="Test",
                input_schema={},
                output_schema={},
                dependencies=[]
            )
            marketplace.publish_agent(definition)
        
        agents = marketplace.list_agents()
        
        assert len(agents) == 3
        assert all("name" in agent for agent in agents)
    
    def test_list_agents_by_category(self, marketplace):
        """Test listing agents filtered by category"""
        # Publish agents in different categories
        for category in ["frontend", "backend", "utility"]:
            definition = CustomAgentDefinition(
                name=f"{category}Agent",
                author="Author",
                description="Test",
                version="1.0.0",
                category=category,
                system_prompt="Test",
                input_schema={},
                output_schema={},
                dependencies=[]
            )
            marketplace.publish_agent(definition)
        
        frontend_agents = marketplace.list_agents(category="frontend")
        
        assert len(frontend_agents) == 1
        assert frontend_agents[0]["category"] == "frontend"
    
    def test_rate_agent(self, marketplace):
        """Test rating an agent"""
        # Publish an agent
        definition = CustomAgentDefinition(
            name="RateAgent",
            author="Author",
            description="Test",
            version="1.0.0",
            category="utility",
            system_prompt="Test",
            input_schema={},
            output_schema={},
            dependencies=[]
        )
        marketplace.publish_agent(definition)
        
        # Rate it
        result = marketplace.rate_agent("RateAgent", 4.5)
        
        assert result["success"] is True
        assert result["new_rating"] > 0


class TestTeamMemory:
    """Tests for Team Memory"""
    
    @pytest.fixture
    def memory(self, tmp_path):
        """Create a team memory instance with temporary storage"""
        return TeamMemory(memory_path=str(tmp_path / "memory"))
    
    def test_record_build(self, memory):
        """Test recording a build"""
        build = BuildHistory(
            id="build1",
            user_id="user1",
            team_id="team1",
            prompt="Build a todo app",
            workflow="standard",
            tech_stack={"frontend": "React", "backend": "FastAPI"},
            success=True,
            quality_score=85.0,
            duration_seconds=120.0,
            files_generated=10,
            timestamp="2024-01-01T00:00:00Z"
        )
        
        memory.record_build(build)
        history = memory.get_team_history("team1")
        
        assert len(history) == 1
        assert history[0].id == "build1"
    
    def test_get_team_history_empty(self, memory):
        """Test getting history for a team with no builds"""
        history = memory.get_team_history("nonexistent_team")
        
        assert history == []
    
    def test_suggest_stack(self, memory):
        """Test stack suggestion based on history"""
        # Record some successful builds
        for i in range(3):
            build = BuildHistory(
                id=f"build{i}",
                user_id="user1",
                team_id="team1",
                prompt=f"Build app {i}",
                workflow="standard",
                tech_stack={"frontend": "React", "backend": "FastAPI"},
                success=True,
                quality_score=80.0 + i,
                duration_seconds=100.0,
                files_generated=10,
                timestamp="2024-01-01T00:00:00Z"
            )
            memory.record_build(build)
        
        suggestion = memory.suggest_stack("Build a new app", "team1")
        
        assert suggestion["suggestion"] is not None
        assert "React" in str(suggestion["suggestion"])
    
    def test_suggest_stack_no_history(self, memory):
        """Test stack suggestion with no history"""
        suggestion = memory.suggest_stack("Build app", "team1")
        
        assert suggestion["suggestion"] is None
        assert "No team history" in suggestion["reason"]
    
    def test_get_insights(self, memory):
        """Test getting team insights"""
        # Record multiple builds
        for i in range(5):
            build = BuildHistory(
                id=f"build{i}",
                user_id="user1",
                team_id="team1",
                prompt=f"Build app {i}",
                workflow="standard",
                tech_stack={"frontend": "React"},
                success=i % 2 == 0,  # 60% success rate
                quality_score=70.0 + i * 5,
                duration_seconds=100.0 + i * 10,
                files_generated=10,
                timestamp="2024-01-01T00:00:00Z"
            )
            memory.record_build(build)
        
        insights = memory.get_insights("team1")
        
        assert insights["total_builds"] == 5
        assert "success_rate" in insights
        assert "avg_quality" in insights
        assert len(insights["insights"]) > 0


class TestDashboard:
    """Tests for Observability Dashboard"""
    
    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance"""
        return Dashboard()
    
    def test_record_execution(self, dashboard):
        """Test recording an agent execution"""
        dashboard.record_execution(
            agent_name="TestAgent",
            success=True,
            duration_ms=100.0,
            tokens=50,
            quality_score=85.0
        )
        
        data = dashboard.get_dashboard_data()
        
        assert len(data["agents"]) == 1
        assert data["agents"][0]["agent_name"] == "TestAgent"
        assert data["agents"][0]["total_executions"] == 1
    
    def test_record_multiple_executions(self, dashboard):
        """Test recording multiple executions"""
        for i in range(5):
            dashboard.record_execution(
                agent_name="TestAgent",
                success=i % 2 == 0,
                duration_ms=100.0 + i * 10,
                tokens=50 + i * 5
            )
        
        data = dashboard.get_dashboard_data()
        agent = data["agents"][0]
        
        assert agent["total_executions"] == 5
        assert agent["successful"] == 3
        assert agent["failed"] == 2
    
    def test_dashboard_summary(self, dashboard):
        """Test dashboard summary calculation"""
        # Record executions for multiple agents
        for agent_name in ["Agent1", "Agent2", "Agent3"]:
            for i in range(3):
                dashboard.record_execution(
                    agent_name=agent_name,
                    success=True,
                    duration_ms=100.0,
                    tokens=50
                )
        
        data = dashboard.get_dashboard_data()
        
        assert data["summary"]["total_agents"] == 3
        assert data["summary"]["total_executions"] == 9
        assert data["summary"]["overall_success_rate"] == 100.0


class TestSelfImprovement:
    """Tests for Self-Improvement System"""
    
    @pytest.fixture
    def optimizer(self):
        """Create a self-improvement instance"""
        return SelfImprovement()
    
    def test_add_variant(self, optimizer):
        """Test adding a prompt variant"""
        variant = PromptVariant(
            id="v1",
            agent_name="TestAgent",
            prompt="You are a test agent v1"
        )
        
        optimizer.add_variant("TestAgent", variant)
        
        assert "TestAgent" in optimizer.variants
        assert len(optimizer.variants["TestAgent"]) == 1
    
    def test_get_prompt(self, optimizer):
        """Test getting a prompt variant"""
        variant = PromptVariant(
            id="v1",
            agent_name="TestAgent",
            prompt="Test prompt"
        )
        optimizer.add_variant("TestAgent", variant)
        
        selected = optimizer.get_prompt("TestAgent")
        
        assert selected is not None
        assert selected.id == "v1"
    
    def test_record_result(self, optimizer):
        """Test recording variant results"""
        variant = PromptVariant(
            id="v1",
            agent_name="TestAgent",
            prompt="Test prompt"
        )
        optimizer.add_variant("TestAgent", variant)
        
        optimizer.record_result("v1", success=True, quality_score=85.0, duration=100.0)
        
        assert variant.executions == 1
        assert variant.successes == 1
        assert variant.avg_quality == 85.0
    
    def test_get_best_prompts(self, optimizer):
        """Test getting best prompts"""
        # Add variants with different performance
        for i in range(3):
            variant = PromptVariant(
                id=f"v{i}",
                agent_name="TestAgent",
                prompt=f"Prompt {i}"
            )
            optimizer.add_variant("TestAgent", variant)
            
            # Record results (variant 2 is best)
            for _ in range(25):
                success = i == 2  # Only v2 succeeds
                optimizer.record_result(f"v{i}", success=success, quality_score=80.0 + i * 5, duration=100.0)
        
        best = optimizer.get_best_prompts()
        
        assert "TestAgent" in best
        assert best["TestAgent"].id == "v2"
    
    def test_optimization_report(self, optimizer):
        """Test generating optimization report"""
        # Add and test variants
        for i in range(2):
            variant = PromptVariant(
                id=f"v{i}",
                agent_name="TestAgent",
                prompt=f"Prompt {i}"
            )
            optimizer.add_variant("TestAgent", variant)
            
            for _ in range(25):
                optimizer.record_result(f"v{i}", success=(i == 1), quality_score=70.0 + i * 10, duration=100.0)
        
        report = optimizer.get_optimization_report()
        
        assert report["agents_optimized"] == 1
        assert len(report["improvements"]) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
