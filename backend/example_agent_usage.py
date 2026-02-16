"""
Example usage of the specialized agents system.

This script demonstrates how to use the 10 specialized agents to build a complete project.
Note: Requires OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable to be set.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.registry import AgentRegistry
from agents.planner_agent import PlannerAgent
from agents.stack_selector_agent import StackSelectorAgent


async def example_planner():
    """Example: Use PlannerAgent to create a project plan."""
    print("\n" + "="*60)
    print("EXAMPLE 1: PlannerAgent")
    print("="*60)
    
    # Get agent from registry
    PlannerAgentClass = AgentRegistry.get_agent("PlannerAgent")
    planner = PlannerAgentClass(llm_client=None, config={})
    
    # Define context
    context = {
        "user_prompt": "Build a full-stack todo application with user authentication, task management, and real-time updates"
    }
    
    print(f"\nInput: {context['user_prompt']}")
    print("\nNote: This example shows the structure. To run with real LLM:")
    print("  - Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
    print("  - Call: result = await planner.run(context)")
    print("\nExpected output structure:")
    print("""
    {
        "project_summary": "Brief description",
        "estimated_duration": "2-3 hours",
        "complexity": "medium",
        "tasks": [
            {
                "id": 1,
                "title": "Select technology stack",
                "description": "Choose appropriate technologies",
                "agent": "StackSelectorAgent",
                "dependencies": [],
                "estimated_complexity": "low"
            },
            ...
        ]
    }
    """)


async def example_stack_selector():
    """Example: Use StackSelectorAgent to select technology stack."""
    print("\n" + "="*60)
    print("EXAMPLE 2: StackSelectorAgent")
    print("="*60)
    
    StackSelectorAgentClass = AgentRegistry.get_agent("StackSelectorAgent")
    stack_selector = StackSelectorAgentClass(llm_client=None, config={})
    
    context = {
        "user_prompt": "E-commerce platform with product catalog, shopping cart, and payment processing",
        "planner_output": {
            "project_summary": "E-commerce platform",
            "complexity": "high"
        }
    }
    
    print(f"\nInput: {context['user_prompt']}")
    print("\nExpected output structure:")
    print("""
    {
        "frontend": {
            "framework": "Next.js",
            "language": "TypeScript",
            "styling": "TailwindCSS",
            "state_management": "Zustand",
            "reasoning": "Next.js for SSR and SEO benefits"
        },
        "backend": {
            "framework": "FastAPI",
            "language": "Python",
            "reasoning": "High performance API framework"
        },
        "database": {
            "primary": "PostgreSQL",
            "caching": "Redis",
            "reasoning": "ACID compliance for transactions"
        },
        "deployment": {
            "frontend": "Vercel",
            "backend": "Railway",
            "reasoning": "Easy deployment and scaling"
        },
        "additional_tools": ["Stripe", "Docker", "Prisma"],
        "overall_reasoning": "Modern, scalable stack for e-commerce"
    }
    """)


async def example_agent_chain():
    """Example: Chain multiple agents together."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Chaining Multiple Agents")
    print("="*60)
    
    print("\nAgent chaining workflow:")
    print("1. PlannerAgent → Creates project plan")
    print("2. StackSelectorAgent → Selects tech stack (uses planner output)")
    print("3. DesignAgent → Creates UI/UX design (uses stack output)")
    print("4. DatabaseAgent → Designs schema (uses stack output)")
    print("5. BackendAgent → Generates backend code (uses stack + database)")
    print("6. FrontendAgent → Generates frontend code (uses stack + design)")
    print("7. TestGenerationAgent → Creates tests (uses frontend + backend)")
    print("8. SecurityAgent → Security audit (uses frontend + backend)")
    print("9. DeploymentAgent → Creates deployment configs (uses stack)")
    print("10. DocumentationAgent → Generates docs (uses all outputs)")
    
    print("\nExample code:")
    print("""
    # Step 1: Plan
    planner_result = await planner.run({"user_prompt": prompt})
    
    # Step 2: Select stack (uses planner output)
    stack_result = await stack_selector.run({
        "user_prompt": prompt,
        "planner_output": planner_result
    })
    
    # Step 3: Design (uses stack output)
    design_result = await design_agent.run({
        "user_prompt": prompt,
        "stack_output": stack_result
    })
    
    # Step 4: Database schema (uses stack output)
    database_result = await database_agent.run({
        "user_prompt": prompt,
        "stack_output": stack_result
    })
    
    # Step 5: Backend code (uses stack + database)
    backend_result = await backend_agent.run({
        "user_prompt": prompt,
        "stack_output": stack_result,
        "database_output": database_result
    })
    
    # Continue chaining...
    """)


def list_all_agents():
    """List all registered agents."""
    print("\n" + "="*60)
    print("REGISTERED AGENTS")
    print("="*60)
    
    agents = AgentRegistry.get_all_agents()
    print(f"\nTotal agents: {len(agents)}\n")
    
    for i, (agent_name, agent_class) in enumerate(agents.items(), 1):
        doc = agent_class.__doc__ or ""
        description = doc.strip().split('\n')[0] if doc else "No description"
        print(f"{i:2d}. {agent_name:25s} - {description}")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("SPECIALIZED AGENTS SYSTEM - USAGE EXAMPLES")
    print("="*60)
    
    # List all agents
    list_all_agents()
    
    # Run examples
    await example_planner()
    await example_stack_selector()
    await example_agent_chain()
    
    print("\n" + "="*60)
    print("GETTING STARTED")
    print("="*60)
    print("""
To use these agents in your code:

1. Import the registry:
   from agents.registry import AgentRegistry

2. Get an agent:
   AgentClass = AgentRegistry.get_agent("PlannerAgent")
   agent = AgentClass(llm_client=None, config={})

3. Prepare context:
   context = {"user_prompt": "Your project description"}

4. Run the agent:
   result = await agent.run(context)

5. Access the output:
   print(result)  # Structured JSON output

For API usage:
- GET /api/agents/v2 - List all registered agents
- Each agent validates input and output automatically
- Agents can be chained by passing output as context
    """)
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
