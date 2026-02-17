#!/usr/bin/env python3
"""
Demo script for Phase 4 Enterprise Features

This script demonstrates the usage of:
1. Agent Marketplace
2. Team Memory
3. Observability Dashboard
4. Self-Improvement System
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime
import asyncio

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from marketplace.agent_store import AgentMarketplace, CustomAgentDefinition
from memory.team_memory import TeamMemory, BuildHistory
from observability.dashboard import Dashboard
from optimization.self_improvement import SelfImprovement, PromptVariant


def demo_marketplace():
    """Demonstrate Agent Marketplace features"""
    print("\n" + "="*60)
    print("AGENT MARKETPLACE DEMO")
    print("="*60)
    
    marketplace = AgentMarketplace(store_path="/tmp/demo_marketplace")
    
    # 1. Publish a custom agent
    print("\n1. Publishing a custom agent...")
    agent = CustomAgentDefinition(
        name="ReactExpert",
        author="demo@crucibai.com",
        description="Expert React component generator with TypeScript support",
        version="1.0.0",
        category="frontend",
        system_prompt="You are an expert React developer with 10+ years experience. Generate clean, production-ready React components with TypeScript, hooks, and best practices.",
        input_schema={"type": "object", "properties": {"component_type": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"code": {"type": "string"}}},
        dependencies=[]
    )
    
    result = marketplace.publish_agent(agent)
    print(f"   Result: {result['message']}")
    
    # 2. Publish more agents
    for name, category in [("FastAPIExpert", "backend"), ("DesignWizard", "design")]:
        agent = CustomAgentDefinition(
            name=name,
            author="demo@crucibai.com",
            description=f"Expert {name} agent",
            version="1.0.0",
            category=category,
            system_prompt=f"You are a {name}.",
            input_schema={},
            output_schema={},
            dependencies=[]
        )
        marketplace.publish_agent(agent)
    
    # 3. List all agents
    print("\n2. Listing all agents in marketplace...")
    agents = marketplace.list_agents()
    for agent in agents:
        print(f"   - {agent['name']} ({agent['category']}) - v{agent['version']} by {agent['author']}")
    
    # 4. Rate an agent
    print("\n3. Rating ReactExpert...")
    marketplace.rate_agent("ReactExpert", 5.0)
    marketplace.rate_agent("ReactExpert", 4.5)
    result = marketplace.rate_agent("ReactExpert", 4.8)
    print(f"   New rating: {result['new_rating']:.2f} ⭐")
    
    # 5. Install an agent
    print("\n4. Installing ReactExpert...")
    result = marketplace.install_agent("ReactExpert")
    print(f"   {result['message']}")
    print(f"   Downloads: 1")


def demo_team_memory():
    """Demonstrate Team Memory features"""
    print("\n" + "="*60)
    print("TEAM MEMORY DEMO")
    print("="*60)
    
    memory = TeamMemory(memory_path="/tmp/demo_memory")
    team_id = "demo_team_123"
    
    # 1. Record multiple builds
    print("\n1. Recording build history...")
    builds = [
        ("todo-app", {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}, True, 85.0, 120.0, 15),
        ("blog-platform", {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}, True, 88.0, 150.0, 22),
        ("chat-app", {"frontend": "Vue", "backend": "Express", "database": "MongoDB"}, False, 65.0, 200.0, 18),
        ("dashboard", {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}, True, 92.0, 110.0, 20),
        ("ecommerce", {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}, True, 87.0, 180.0, 35),
    ]
    
    for i, (prompt, stack, success, quality, duration, files) in enumerate(builds):
        build = BuildHistory(
            id=f"build_{i+1}",
            user_id="demo_user",
            team_id=team_id,
            prompt=f"Build a {prompt}",
            workflow="standard",
            tech_stack=stack,
            success=success,
            quality_score=quality,
            duration_seconds=duration,
            files_generated=files,
            timestamp=datetime.utcnow().isoformat()
        )
        memory.record_build(build)
        status = "✓" if success else "✗"
        print(f"   {status} {prompt}: Quality {quality}/100, {duration}s, {files} files")
    
    # 2. Get stack suggestion
    print("\n2. Getting stack suggestion for new project...")
    suggestion = memory.suggest_stack("Build a social media app", team_id)
    if suggestion['suggestion']:
        print(f"   Recommended Stack:")
        for key, value in suggestion['suggestion'].items():
            print(f"     - {key}: {value}")
        print(f"   Reason: {suggestion['reason']}")
    
    # 3. Get team insights
    print("\n3. Team insights:")
    insights = memory.get_insights(team_id)
    print(f"   Total Builds: {insights['total_builds']}")
    print(f"   Success Rate: {insights['success_rate']:.1f}%")
    print(f"   Avg Quality: {insights['avg_quality']:.1f}/100")
    print(f"   Key Insights:")
    for insight in insights['insights']:
        print(f"     - {insight}")


def demo_dashboard():
    """Demonstrate Observability Dashboard"""
    print("\n" + "="*60)
    print("OBSERVABILITY DASHBOARD DEMO")
    print("="*60)
    
    dashboard = Dashboard()
    
    # 1. Record executions for various agents
    print("\n1. Recording agent executions...")
    agents_data = [
        ("Frontend Generation", [(True, 2340, 1520), (True, 2150, 1480), (False, 3200, 2000), (True, 2280, 1550)]),
        ("Backend Generation", [(True, 3120, 2145), (True, 2980, 2100), (True, 3050, 2120)]),
        ("Security Checker", [(True, 450, 320), (True, 480, 340), (True, 460, 330)]),
        ("Test Generation", [(True, 1850, 1200), (False, 2500, 1800), (True, 1920, 1250)]),
    ]
    
    for agent_name, executions in agents_data:
        for success, duration_ms, tokens in executions:
            dashboard.record_execution(
                agent_name=agent_name,
                success=success,
                duration_ms=duration_ms,
                tokens=tokens,
                quality_score=85.0 if success else 60.0
            )
        status = "✓" if all(s for s, _, _ in executions) else "⚠"
        print(f"   {status} {agent_name}: {len(executions)} executions")
    
    # 2. Get dashboard data
    print("\n2. Dashboard Summary:")
    data = dashboard.get_dashboard_data()
    summary = data['summary']
    print(f"   Total Agents: {summary['total_agents']}")
    print(f"   Total Executions: {summary['total_executions']}")
    print(f"   Overall Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"   Avg Duration: {summary['overall_avg_duration_ms']:.1f}ms")
    
    # 3. Show top agents
    print("\n3. Top Agents by Activity:")
    for agent in data['agents'][:3]:
        print(f"   {agent['agent_name']}:")
        print(f"     - Executions: {agent['total_executions']}")
        print(f"     - Success Rate: {agent['success_rate']:.1f}%")
        print(f"     - Avg Duration: {agent['avg_duration_ms']:.1f}ms")
        print(f"     - Avg Quality: {agent['avg_quality_score']:.1f}/100")


def demo_self_improvement():
    """Demonstrate Self-Improvement System"""
    print("\n" + "="*60)
    print("SELF-IMPROVEMENT SYSTEM DEMO")
    print("="*60)
    
    optimizer = SelfImprovement()
    
    # 1. Add prompt variants
    print("\n1. Adding prompt variants for testing...")
    variants = [
        PromptVariant(
            id="v1_baseline",
            agent_name="Frontend Generation",
            prompt="Generate React code."
        ),
        PromptVariant(
            id="v2_detailed",
            agent_name="Frontend Generation",
            prompt="You are an expert React developer with 10+ years experience. Generate production-ready React code with TypeScript, hooks, and best practices."
        ),
        PromptVariant(
            id="v3_concise",
            agent_name="Frontend Generation",
            prompt="You are a senior React engineer. Write clean, maintainable React code with modern patterns."
        ),
    ]
    
    for variant in variants:
        optimizer.add_variant("Frontend Generation", variant)
        print(f"   Added variant: {variant.id}")
    
    # 2. Simulate testing with different success rates
    print("\n2. Simulating A/B testing (30 executions)...")
    import random
    
    # v1: baseline (70% success, quality 75)
    # v2: best (95% success, quality 88)
    # v3: good (85% success, quality 82)
    variant_performance = {
        "v1_baseline": (0.70, 75.0),
        "v2_detailed": (0.95, 88.0),
        "v3_concise": (0.85, 82.0),
    }
    
    for _ in range(30):
        # Get a variant (epsilon-greedy)
        variant = optimizer.get_prompt("Frontend Generation")
        success_rate, avg_quality = variant_performance[variant.id]
        
        # Simulate execution
        success = random.random() < success_rate
        quality = avg_quality + random.uniform(-5, 5)
        duration = 2000 + random.uniform(-500, 500)
        
        optimizer.record_result(variant.id, success, quality, duration)
    
    print("   ✓ Completed 30 A/B test executions")
    
    # 3. Get best prompts
    print("\n3. Best performing prompt:")
    best = optimizer.get_best_prompts()
    if "Frontend Generation" in best:
        best_variant = best["Frontend Generation"]
        print(f"   Variant: {best_variant.id}")
        print(f"   Score: {best_variant.score:.3f}")
        print(f"   Success Rate: {best_variant.success_rate:.1f}%")
        print(f"   Executions: {best_variant.executions}")
        print(f"   Avg Quality: {best_variant.avg_quality:.1f}/100")
    
    # 4. Generate optimization report
    print("\n4. Optimization Report:")
    report = optimizer.get_optimization_report()
    print(f"   Agents Optimized: {report['agents_optimized']}")
    if report['improvements']:
        for imp in report['improvements']:
            print(f"   {imp['agent']}:")
            print(f"     - Baseline Score: {imp['baseline_score']:.3f}")
            print(f"     - Best Score: {imp['best_score']:.3f}")
            print(f"     - Improvement: +{imp['improvement_percent']:.1f}%")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("PHASE 4: ENTERPRISE FEATURES DEMO")
    print("="*60)
    print("\nThis demo showcases the four major enterprise features:")
    print("1. Agent Marketplace - Create and share custom agents")
    print("2. Team Memory - Learn from past builds")
    print("3. Observability Dashboard - Monitor performance")
    print("4. Self-Improvement - A/B test and optimize")
    
    try:
        demo_marketplace()
        demo_team_memory()
        demo_dashboard()
        demo_self_improvement()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE ✓")
        print("="*60)
        print("\nAll enterprise features demonstrated successfully!")
        print("Check backend/ENTERPRISE_FEATURES.md for full documentation.")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
