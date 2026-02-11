"""
Agent error handling, retry, criticality, timeouts, and fallbacks.
"""
from typing import Dict, Optional

# Criticality: critical = stop build; high = continue with fallback; low/medium = skip
AGENT_CRITICALITY: Dict[str, str] = {
    "Planner": "critical",
    "Requirements Clarifier": "high",
    "Stack Selector": "critical",
    "Frontend Generation": "high",
    "Backend Generation": "high",
    "Database Agent": "high",
    "API Integration": "medium",
    "Test Generation": "medium",
    "Image Generation": "low",
    "Security Checker": "medium",
    "Test Executor": "medium",
    "UX Auditor": "low",
    "Performance Analyzer": "low",
    "Deployment Agent": "medium",
    "Error Recovery": "low",
    "Memory Agent": "low",
    "PDF Export": "low",
    "Excel Export": "low",
    "Scraping Agent": "low",
    "Automation Agent": "low",
}

# Timeout in seconds per agent (complex ones get more)
AGENT_TIMEOUTS: Dict[str, int] = {
    "Planner": 120,
    "Requirements Clarifier": 90,
    "Stack Selector": 60,
    "Frontend Generation": 180,
    "Backend Generation": 180,
    "Database Agent": 90,
    "API Integration": 90,
    "Test Generation": 120,
    "Image Generation": 60,
    "Security Checker": 90,
    "Test Executor": 60,
    "UX Auditor": 60,
    "Performance Analyzer": 60,
    "Deployment Agent": 90,
    "Error Recovery": 60,
    "Memory Agent": 45,
    "PDF Export": 45,
    "Excel Export": 45,
    "Scraping Agent": 90,
    "Automation Agent": 60,
}

DEFAULT_TIMEOUT = 120


class AgentError(Exception):
    def __init__(self, agent_name: str, reason: str, severity: str = "high"):
        self.agent_name = agent_name
        self.reason = reason
        self.severity = severity
        super().__init__(f"{agent_name}: {reason}")


def get_criticality(agent_name: str) -> str:
    return AGENT_CRITICALITY.get(agent_name, "medium")


def get_timeout(agent_name: str) -> int:
    return AGENT_TIMEOUTS.get(agent_name, DEFAULT_TIMEOUT)


# User-facing error messages (for UI / logs)
AGENT_ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "Planner": {
        "timeout": "Planning is taking longer than expected. Try a shorter description.",
        "empty_output": "Planning failed. Make sure your app description is clear and specific.",
    },
    "Stack Selector": {
        "timeout": "Tech stack selection timed out. Try again.",
        "empty_output": "Could not select stack. Refine your requirements.",
    },
    "Frontend Generation": {
        "timeout": "Frontend generation takes time for complex apps.",
        "empty_output": "Frontend generation failed. Using default template.",
    },
    "Backend Generation": {
        "timeout": "Backend generation is taking longer than usual.",
        "empty_output": "Backend generation failed. Using default template.",
    },
    "Security Checker": {
        "timeout": "Security hardening takes time for large apps.",
        "empty_output": "Security check found no improvements needed.",
    },
    "Performance Analyzer": {
        "timeout": "Performance analysis skipped (timeout).",
        "empty_output": "No optimization suggestions.",
    },
}


def get_error_message(agent_name: str, error_code: str) -> Optional[str]:
    """Return user-friendly message for agent failure."""
    msgs = AGENT_ERROR_MESSAGES.get(agent_name, {})
    return msgs.get(error_code) or msgs.get("empty_output") or f"Agent {agent_name} failed."


def generate_fallback(agent_name: str) -> str:
    """Minimal valid output when an agent fails."""
    fallbacks = {
        "Frontend Generation": "// Generated frontend (failed, using default React template)\nconst App = () => <div>Generated app placeholder</div>;\nexport default App;",
        "Backend Generation": "# Generated backend (failed, using default)\nfrom fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root(): return {'message': 'Hello'}",
        "Database Agent": "-- Schema placeholder\n-- Tables: users, sessions",
        "Test Generation": "# Test generation failed, skipped",
        "Security Checker": "Security check skipped.",
        "Performance Analyzer": "Performance analysis skipped.",
        "Planner": "1. Implement core feature 2. Add tests 3. Deploy",
        "Stack Selector": "Frontend: React, Backend: FastAPI, DB: MongoDB",
        "Requirements Clarifier": "Clarifications skipped.",
    }
    return fallbacks.get(agent_name, f"// {agent_name} generated no output (failed).")
