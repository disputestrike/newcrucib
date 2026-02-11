"""
10/10 Roadmap: Tests for error handling, criticality, fallbacks.
"""
import pytest
from agent_resilience import (
    get_criticality,
    get_timeout,
    generate_fallback,
    get_error_message,
    AGENT_CRITICALITY,
    AGENT_ERROR_MESSAGES,
)


def test_critical_agents():
    assert get_criticality("Planner") == "critical"
    assert get_criticality("Stack Selector") == "critical"


def test_high_agents_get_fallback():
    assert get_criticality("Frontend Generation") == "high"
    fallback = generate_fallback("Frontend Generation")
    assert "React" in fallback or "frontend" in fallback.lower()


def test_fallback_exists_for_key_agents():
    for name in ["Frontend Generation", "Backend Generation", "Planner", "Stack Selector"]:
        assert generate_fallback(name)


def test_timeouts_positive():
    assert get_timeout("Planner") >= 60
    assert get_timeout("Frontend Generation") >= 60


def test_error_messages():
    msg = get_error_message("Planner", "timeout")
    assert msg and "planning" in msg.lower() or "shorter" in msg.lower()
    msg2 = get_error_message("Unknown", "timeout")
    assert "failed" in msg2.lower() or "Unknown" in msg2
