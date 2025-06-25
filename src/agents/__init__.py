"""
Agents module for the multi-agent solution.
"""

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .writing_agent import WritingAgent
from .coordinator_agent import CoordinatorAgent

__all__ = [
    "BaseAgent",
    "ResearchAgent", 
    "WritingAgent",
    "CoordinatorAgent"
]
