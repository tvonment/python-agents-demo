"""
Plugins module for the multi-agent solution.
"""

from .research_plugins import WebSearchPlugin, DataAnalysisPlugin
from .writing_plugins import ContentCreationPlugin, EditingPlugin
from .coordination_plugins import TaskManagementPlugin

__all__ = [
    "WebSearchPlugin",
    "DataAnalysisPlugin",
    "ContentCreationPlugin", 
    "EditingPlugin",
    "TaskManagementPlugin"
]
