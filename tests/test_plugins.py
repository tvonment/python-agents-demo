"""
Tests for plugin classes.
"""
import pytest
from unittest.mock import Mock, patch

from src.plugins import (
    WebSearchPlugin, DataAnalysisPlugin,
    ContentCreationPlugin, EditingPlugin,
    TaskManagementPlugin
)


class TestWebSearchPlugin:
    """Test cases for WebSearchPlugin."""
    
    def test_search_web(self):
        """Test web search functionality."""
        plugin = WebSearchPlugin()
        
        result = plugin.search_web("AI in healthcare", max_results=3)
        
        assert "AI in healthcare" in result
        assert "Search result" in result
        assert len(result.split("\n\n")) <= 3
    
    def test_get_recent_news(self):
        """Test recent news functionality."""
        plugin = WebSearchPlugin()
        
        result = plugin.get_recent_news("healthcare AI", days=7)
        
        assert "healthcare AI" in result
        assert "Recent news" in result
        assert "7 days" in result


class TestDataAnalysisPlugin:
    """Test cases for DataAnalysisPlugin."""
    
    def test_analyze_trends(self):
        """Test trend analysis functionality."""
        plugin = DataAnalysisPlugin()
        
        result = plugin.analyze_trends("hospital efficiency data", "quarterly")
        
        assert "hospital efficiency data" in result
        assert "quarterly" in result
        assert "Trend Analysis" in result
        assert "Key Findings" in result
    
    def test_statistical_summary(self):
        """Test statistical summary functionality."""
        plugin = DataAnalysisPlugin()
        
        result = plugin.statistical_summary("patient satisfaction scores")
        
        assert "patient satisfaction scores" in result
        assert "Statistical Summary" in result
        assert "Mean" in result
        assert "Standard Deviation" in result
    
    def test_fact_check(self):
        """Test fact checking functionality."""
        plugin = DataAnalysisPlugin()
        
        result = plugin.fact_check("AI reduces medical errors by 50%")
        
        assert "AI reduces medical errors by 50%" in result
        assert "Fact-Check Report" in result
        assert "Verification Status" in result


class TestContentCreationPlugin:
    """Test cases for ContentCreationPlugin."""
    
    def test_generate_outline(self):
        """Test outline generation functionality."""
        plugin = ContentCreationPlugin()
        
        result = plugin.generate_outline("Machine Learning in Diagnostics", "article")
        
        assert "Machine Learning in Diagnostics" in result
        assert "article" in result
        assert "Content Outline" in result
        assert "Introduction" in result
        assert "Conclusion" in result
    
    def test_format_content(self):
        """Test content formatting functionality."""
        plugin = ContentCreationPlugin()
        
        content = "This is sample content for formatting."
        result = plugin.format_content(content, "professional")
        
        assert content in result
        assert "professional" in result.upper()
        assert "FORMATTED CONTENT" in result
    
    def test_generate_title_options(self):
        """Test title generation functionality."""
        plugin = ContentCreationPlugin()
        
        result = plugin.generate_title_options("Article about AI benefits", count=3)
        
        assert "AI benefits" in result
        assert "Title Options" in result
        assert "Title Option 1" in result
        assert "Title Option 3" in result


class TestEditingPlugin:
    """Test cases for EditingPlugin."""
    
    def test_check_grammar(self):
        """Test grammar checking functionality."""
        plugin = EditingPlugin()
        
        content = "This is a sample text for grammar checking."
        result = plugin.check_grammar(content)
        
        assert "Grammar and Spelling Check" in result
        assert "Content Length" in result
        assert str(len(content)) in result
    
    def test_improve_readability(self):
        """Test readability improvement functionality."""
        plugin = EditingPlugin()
        
        content = "Complex technical content that needs readability analysis."
        result = plugin.improve_readability(content)
        
        assert "Readability Analysis" in result
        assert "Improvement Suggestions" in result
        assert "Current Assessment" in result
    
    def test_style_consistency(self):
        """Test style consistency checking functionality."""
        plugin = EditingPlugin()
        
        content = "Content for style consistency checking."
        result = plugin.style_consistency(content, "academic")
        
        assert "Style Consistency Analysis" in result
        assert "academic" in result
        assert "Consistency Check" in result


class TestTaskManagementPlugin:
    """Test cases for TaskManagementPlugin."""
    
    def test_create_task(self):
        """Test task creation functionality."""
        plugin = TaskManagementPlugin()
        
        result = plugin.create_task(
            title="Test Task",
            description="This is a test task",
            priority="high",
            assigned_agent="TestAgent"
        )
        
        assert "Task Created Successfully" in result
        assert "Test Task" in result
        assert "high" in result
        assert "TestAgent" in result
        assert len(plugin.tasks) == 1
    
    def test_assign_task(self):
        """Test task assignment functionality."""
        plugin = TaskManagementPlugin()
        
        # First create a task
        plugin.create_task("Test Task", "Description")
        task_id = "task_1"
        
        result = plugin.assign_task(task_id, "NewAgent")
        
        assert "Task Assignment Completed" in result
        assert "NewAgent" in result
        assert plugin.tasks[task_id]["assigned_agent"] == "NewAgent"
        assert plugin.tasks[task_id]["status"] == "assigned"
    
    def test_update_task_status(self):
        """Test task status update functionality."""
        plugin = TaskManagementPlugin()
        
        # Create a task first
        plugin.create_task("Test Task", "Description")
        task_id = "task_1"
        
        result = plugin.update_task_status(task_id, "in_progress", 50)
        
        assert "Task Status Updated" in result
        assert "in_progress" in result
        assert plugin.tasks[task_id]["status"] == "in_progress"
        assert plugin.tasks[task_id]["progress"] == 50
    
    def test_get_task_list(self):
        """Test task list functionality."""
        plugin = TaskManagementPlugin()
        
        # Test empty task list
        result = plugin.get_task_list()
        assert "No tasks found" in result
        
        # Create some tasks
        plugin.create_task("Task 1", "Description 1", "high")
        plugin.create_task("Task 2", "Description 2", "low")
        
        result = plugin.get_task_list()
        
        assert "Task List" in result
        assert "Task 1" in result
        assert "Task 2" in result
    
    def test_analyze_workload(self):
        """Test workload analysis functionality."""
        plugin = TaskManagementPlugin()
        
        # Test empty workload
        result = plugin.analyze_workload()
        assert "No tasks available" in result
        
        # Create tasks with different agents
        plugin.create_task("Task 1", "Description", assigned_agent="Agent1")
        plugin.create_task("Task 2", "Description", assigned_agent="Agent1")
        plugin.create_task("Task 3", "Description", assigned_agent="Agent2")
        
        # Update some task statuses
        plugin.update_task_status("task_1", "completed")
        plugin.update_task_status("task_2", "in_progress")
        
        result = plugin.analyze_workload()
        
        assert "Workload Analysis Report" in result
        assert "Agent1" in result
        assert "Agent2" in result
        assert "Total Tasks" in result
    
    def test_set_task_dependency(self):
        """Test task dependency functionality."""
        plugin = TaskManagementPlugin()
        
        # Create two tasks
        plugin.create_task("Task 1", "First task")
        plugin.create_task("Task 2", "Second task")
        
        result = plugin.set_task_dependency("task_2", "task_1")
        
        assert "Task Dependency Set" in result
        assert "task_1" in plugin.tasks["task_2"]["dependencies"]
    
    def test_task_not_found_error(self):
        """Test error handling for non-existent tasks."""
        plugin = TaskManagementPlugin()
        
        result = plugin.assign_task("nonexistent_task", "Agent")
        assert "Error: Task nonexistent_task not found" in result
        
        result = plugin.update_task_status("nonexistent_task", "completed")
        assert "Error: Task nonexistent_task not found" in result
