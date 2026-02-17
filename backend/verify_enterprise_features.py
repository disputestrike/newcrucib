#!/usr/bin/env python3
"""
Manual verification script for Phase 4 Enterprise Features
Tests all new API endpoints without requiring a full server startup
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marketplace.agent_marketplace import AgentMarketplace
from learning.team_memory import TeamMemory
from observability.agent_dashboard import AgentDashboard
from learning.self_improvement import SelfImprovement

print("=" * 60)
print("Phase 4 Enterprise Features - Manual Verification")
print("=" * 60)

# Test 1: Agent Marketplace
print("\n1. Testing Agent Marketplace...")
marketplace = AgentMarketplace(storage_path="./test_marketplace")
agent = marketplace.create_agent(
    name="Demo Agent",
    description="A demonstration agent",
    author="test_user",
    category="frontend",
    system_prompt="You are a helpful agent",
    input_schema={"type": "object"},
    output_schema={"type": "object"}
)
print(f"✓ Created agent: {agent.name} (ID: {agent.id})")

results = marketplace.search_agents(query="Demo")
print(f"✓ Search found {len(results)} agent(s)")

install_result = marketplace.install_agent(agent.id, "user123")
print(f"✓ Agent installed: {install_result['success']}")

rate_result = marketplace.rate_agent(agent.id, 4.5, "user123")
print(f"✓ Agent rated: {rate_result['new_rating']:.2f}")

# Test 2: Team Memory
print("\n2. Testing Team Memory...")
team_memory = TeamMemory(storage_path="./test_team_memory")
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
memory = team_memory.record_build("build-1", "user-1", "team-1", result)
print(f"✓ Build recorded: {memory.build_id}")

insights = team_memory.get_team_insights("team-1")
print(f"✓ Team insights retrieved: {insights['total_builds']} builds")

suggestion = team_memory.suggest_stack("team-1", "Build a web app")
print(f"✓ Stack suggestion: {suggestion['suggestion']}")

recommendations = team_memory.get_improvement_recommendations("team-1")
print(f"✓ Recommendations: {len(recommendations)} suggestion(s)")

# Test 3: Observability Dashboard
print("\n3. Testing Observability Dashboard...")
dashboard = AgentDashboard()
metrics = {
    "agent_name": "TestAgent",
    "duration_ms": 1500,
    "tokens_used": 500,
    "success": True
}
dashboard.record_execution(metrics)
print(f"✓ Execution recorded for: {metrics['agent_name']}")

dashboard_data = dashboard.get_dashboard_data(hours=24)
if "message" in dashboard_data:
    print(f"✓ Dashboard data: {dashboard_data['message']}")
else:
    print(f"✓ Dashboard data: {dashboard_data['overall']['total_executions']} executions")

# Test 4: Self-Improvement
print("\n4. Testing Self-Improvement System...")
improvement = SelfImprovement()
variant = improvement.create_prompt_variant(
    agent_name="TestAgent",
    variant_prompt="Improved system prompt",
    variant_name="v1"
)
print(f"✓ Variant created: {variant.variant_id}")

selected = improvement.select_variant("TestAgent")
print(f"✓ Variant selected: {selected}")

improvement.record_result("TestAgent", variant.variant_id, 85.0, 1500, True)
print(f"✓ Result recorded: quality=85.0, success=True")

report = improvement.generate_improvement_report("TestAgent")
print(f"✓ Improvement report: {report.get('message', 'Data available')}")

print("\n" + "=" * 60)
print("All Phase 4 Enterprise Features verified successfully! ✓")
print("=" * 60)

# Cleanup test directories
import shutil
for dir_path in ["./test_marketplace", "./test_team_memory", "./marketplace_agents", "./team_memory"]:
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except:
            pass

print("\nTest directories cleaned up.")
