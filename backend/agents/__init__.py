"""
Agent system for Newcrucib V2.
Provides base classes and registry for specialized agents.

Legacy agents for image (Together.ai) and video (Pexels) generation.
"""
from agents.base_agent import BaseAgent, AgentValidationError, AgentMetrics
from agents.registry import AgentRegistry

__all__ = ["BaseAgent", "AgentValidationError", "AgentMetrics", "AgentRegistry"]
