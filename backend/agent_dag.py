"""
Agent DAG: dependency graph and parallel execution phases.
Used by run_orchestration_v2 for output chaining and parallel runs.
Token optimization: set USE_TOKEN_OPTIMIZED_PROMPTS=1 for shorter prompts and smaller context.
"""
import os
from collections import deque
from typing import Dict, List, Any

# Agent names must match _ORCHESTRATION_AGENTS in server.py
# depends_on = list of agent names that must complete before this one
AGENT_DAG: Dict[str, Dict[str, Any]] = {
    "Planner": {"depends_on": [], "system_prompt": "You are a Planner. Decompose the request into 3-7 executable tasks. Numbered list only."},
    "Requirements Clarifier": {"depends_on": ["Planner"], "system_prompt": "You are a Requirements Clarifier. Ask 2-4 clarifying questions. One per line."},
    "Stack Selector": {"depends_on": ["Requirements Clarifier"], "system_prompt": "You are a Stack Selector. Recommend tech stack (frontend, backend, DB). Short bullets."},
    "Frontend Generation": {"depends_on": ["Stack Selector"], "system_prompt": "You are Frontend Generation. Output only complete React/JSX code. No markdown."},
    "Backend Generation": {"depends_on": ["Stack Selector"], "system_prompt": "You are Backend Generation. Output only backend code (e.g. FastAPI/Express). No markdown."},
    "Database Agent": {"depends_on": ["Backend Generation"], "system_prompt": "You are a Database Agent. Output schema and migration steps. Plain text or SQL."},
    "API Integration": {"depends_on": ["Stack Selector"], "system_prompt": "You are API Integration. Output only code that calls an API. No markdown."},
    "Test Generation": {"depends_on": ["Backend Generation"], "system_prompt": "You are Test Generation. Output only test code. No markdown."},
    "Image Generation": {"depends_on": ["Stack Selector"], "system_prompt": "You are Image Generation. Output a detailed image prompt (style, composition, colors) for the request."},
    "Security Checker": {"depends_on": ["Frontend Generation", "Backend Generation"], "system_prompt": "You are a Security Checker. List 3-5 security checklist items with PASS/FAIL."},
    "Test Executor": {"depends_on": ["Test Generation"], "system_prompt": "You are a Test Executor. Give the test command and one line of what to check."},
    "UX Auditor": {"depends_on": ["Frontend Generation"], "system_prompt": "You are a UX Auditor. List 2-4 accessibility/UX checklist items with PASS/FAIL."},
    "Performance Analyzer": {"depends_on": ["Frontend Generation", "Backend Generation"], "system_prompt": "You are a Performance Analyzer. List 2-4 performance tips for the project."},
    "Deployment Agent": {"depends_on": ["Backend Generation"], "system_prompt": "You are a Deployment Agent. Give step-by-step deploy instructions."},
    "Error Recovery": {"depends_on": ["Backend Generation"], "system_prompt": "You are Error Recovery. List 2-3 common failure points and how to recover."},
    "Memory Agent": {"depends_on": ["Deployment Agent"], "system_prompt": "You are a Memory Agent. Summarize the project in 2-3 lines for reuse."},
    "PDF Export": {"depends_on": ["Deployment Agent"], "system_prompt": "You are PDF Export. Describe what a one-page project summary PDF would include."},
    "Excel Export": {"depends_on": ["Deployment Agent"], "system_prompt": "You are Excel Export. Suggest 3-5 columns for a project tracking spreadsheet."},
    "Scraping Agent": {"depends_on": ["Stack Selector"], "system_prompt": "You are a Scraping Agent. Suggest 2-3 data sources or URLs to scrape for this project."},
    "Automation Agent": {"depends_on": ["Stack Selector"], "system_prompt": "You are an Automation Agent. Suggest 2-3 automated tasks or cron jobs for this project."},
}

# Max chars of previous output to inject (avoid token overflow)
CONTEXT_MAX_CHARS = 2000
CONTEXT_MAX_CHARS_OPTIMIZED = 1200

# Shorter system prompts when USE_TOKEN_OPTIMIZED_PROMPTS=1 (~10–12K vs ~20K tokens per build)
OPTIMIZED_SYSTEM_PROMPTS: Dict[str, str] = {
    "Planner": "Planner. 3–7 tasks. Numbered list only.",
    "Requirements Clarifier": "Requirements. 2–4 clarifying questions. One per line.",
    "Stack Selector": "Stack. Recommend frontend, backend, DB. Short bullets.",
    "Frontend Generation": "Frontend. React/JSX code only. No markdown.",
    "Backend Generation": "Backend. FastAPI/Express code only. No markdown.",
    "Database Agent": "Database. Schema and migrations. Plain text or SQL.",
    "API Integration": "API. Code that calls an API. No markdown.",
    "Test Generation": "Tests. Test code only. No markdown.",
    "Image Generation": "Image. One detailed image prompt (style, composition, colors).",
    "Security Checker": "Security. 3–5 items PASS/FAIL.",
    "Test Executor": "Test run. Command + one line to check.",
    "UX Auditor": "UX. 2–4 accessibility items PASS/FAIL.",
    "Performance Analyzer": "Performance. 2–4 tips.",
    "Deployment Agent": "Deploy. Step-by-step instructions.",
    "Error Recovery": "Errors. 2–3 failure points + recovery.",
    "Memory Agent": "Memory. 2–3 line project summary.",
    "PDF Export": "PDF. One-page summary description.",
    "Excel Export": "Excel. 3–5 columns for tracking.",
    "Scraping Agent": "Scraping. 2–3 data sources or URLs.",
    "Automation Agent": "Automation. 2–3 cron/automated tasks.",
}


def _use_token_optimized() -> bool:
    return os.environ.get("USE_TOKEN_OPTIMIZED_PROMPTS", "").strip().lower() in ("1", "true", "yes")


def get_context_max_chars() -> int:
    """Max chars per previous output; smaller when token-optimized."""
    return CONTEXT_MAX_CHARS_OPTIMIZED if _use_token_optimized() else CONTEXT_MAX_CHARS


def get_system_prompt_for_agent(agent_name: str) -> str:
    """System prompt for agent; uses short version when USE_TOKEN_OPTIMIZED_PROMPTS=1."""
    if agent_name not in AGENT_DAG:
        return ""
    if _use_token_optimized() and agent_name in OPTIMIZED_SYSTEM_PROMPTS:
        return OPTIMIZED_SYSTEM_PROMPTS[agent_name]
    return AGENT_DAG[agent_name].get("system_prompt", "")


def topological_sort(dag: Dict[str, Dict[str, Any]]) -> List[str]:
    """Kahn's algorithm: return execution order respecting dependencies. Raises if cycle."""
    in_degree = {n: 0 for n in dag}
    for node, cfg in dag.items():
        for dep in cfg.get("depends_on", []):
            if dep in dag:
                in_degree[node] += 1
    # Actually we need deps to point TO the node, so "node depends on dep" => edge dep -> node
    # So in_degree[node] = number of deps that must run first = len(depends_on)
    in_degree = {n: len(cfg.get("depends_on", [])) for n, cfg in dag.items()}
    q = deque([n for n, d in in_degree.items() if d == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for node, cfg in dag.items():
            if u in cfg.get("depends_on", []):
                in_degree[node] -= 1
                if in_degree[node] == 0:
                    q.append(node)
    if len(order) != len(dag):
        raise ValueError("Cycle in agent DAG")
    return order


def get_execution_phases(dag: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """Group agents into phases: each phase can run in parallel (no dep within phase)."""
    order = topological_sort(dag)
    phases: List[List[str]] = []
    completed = set()
    while len(completed) < len(order):
        ready = []
        for node in order:
            if node in completed:
                continue
            deps = set(dag[node].get("depends_on", []))
            if deps <= completed:
                ready.append(node)
        if not ready:
            raise ValueError("DAG cycle or missing nodes")
        phases.append(ready)
        completed.update(ready)
    return phases


def build_context_from_previous_agents(
    current_agent: str,
    previous_outputs: Dict[str, Dict[str, Any]],
    project_prompt: str,
) -> str:
    """Build enhanced prompt with previous agents' outputs. Truncates to get_context_max_chars() per output."""
    max_chars = get_context_max_chars()
    parts = [project_prompt]
    for agent_name, data in previous_outputs.items():
        out = data.get("output") or data.get("result") or data.get("code") or ""
        if isinstance(out, str) and out.strip():
            snippet = out.strip()[:max_chars]
            if len(out.strip()) > max_chars:
                snippet += "\n... (truncated)"
            parts.append(f"--- Output from {agent_name} ---\n{snippet}")
    return "\n\n".join(parts)
