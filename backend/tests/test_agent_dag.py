"""
10/10 Roadmap: Tests for Agent DAG (topological sort, phases, no cycles).
"""
import pytest
from agent_dag import AGENT_DAG, topological_sort, get_execution_phases, build_context_from_previous_agents


def test_dag_has_all_agents():
    assert len(AGENT_DAG) >= 15
    assert "Planner" in AGENT_DAG
    assert "Frontend Generation" in AGENT_DAG
    assert "Backend Generation" in AGENT_DAG


def test_topological_sort_respects_dependencies():
    order = topological_sort(AGENT_DAG)
    assert "Planner" in order
    planner_idx = order.index("Planner")
    for node, cfg in AGENT_DAG.items():
        for dep in cfg.get("depends_on", []):
            if dep in order:
                assert order.index(dep) < order.index(node), f"{dep} must run before {node}"


def test_topological_sort_returns_all_nodes():
    order = topological_sort(AGENT_DAG)
    assert len(order) == len(AGENT_DAG)
    assert set(order) == set(AGENT_DAG.keys())


def test_get_execution_phases():
    phases = get_execution_phases(AGENT_DAG)
    assert len(phases) >= 1
    all_agents = [a for p in phases for a in p]
    assert set(all_agents) == set(AGENT_DAG.keys())
    assert "Planner" in phases[0]


def test_build_context_truncates():
    previous = {
        "Planner": {"output": "x" * 5000},
        "Stack Selector": {"output": "React, FastAPI"},
    }
    out = build_context_from_previous_agents("Frontend Generation", previous, "Build a todo app")
    assert "React, FastAPI" in out
    assert len(out) < 6000
