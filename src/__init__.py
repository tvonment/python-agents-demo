"""
Main module for the multi-agent solution.
"""

from .agents import BaseAgent, ResearchAgent, WritingAgent, CoordinatorAgent
from .plugins import (
    WebSearchPlugin, DataAnalysisPlugin,
    ContentCreationPlugin, EditingPlugin,
    TaskManagementPlugin
)
from .config import settings

__all__ = [
    "BaseAgent",
    "ResearchAgent", 
    "WritingAgent",
    "CoordinatorAgent",
    "WebSearchPlugin",
    "DataAnalysisPlugin",
    "ContentCreationPlugin",
    "EditingPlugin", 
    "TaskManagementPlugin",
    "settings"
]
