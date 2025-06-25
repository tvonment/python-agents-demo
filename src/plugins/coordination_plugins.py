"""
Coordination-related plugins for the multi-agent solution.
"""
import logging
from typing import List, Dict, Any, Optional
from semantic_kernel.functions import kernel_function
from semantic_kernel import Kernel


logger = logging.getLogger(__name__)


class TaskManagementPlugin:
    """Plugin for task management and coordination functionality."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_counter = 0
    
    @kernel_function(
        name="create_task",
        description="Create a new task with specified parameters"
    )
    def create_task(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        assigned_agent: Optional[str] = None
    ) -> str:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high)
            assigned_agent: Agent assigned to the task
            
        Returns:
            Task creation confirmation with task ID
        """
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "assigned_agent": assigned_agent,
            "status": "created",
            "created_at": "current_timestamp",  # In real implementation, use actual timestamp
            "dependencies": [],
            "progress": 0
        }
        
        self.tasks[task_id] = task
        
        logger.info(f"Created task: {task_id} - {title}")
        
        result = f"""
        Task Created Successfully:
        
        Task ID: {task_id}
        Title: {title}
        Description: {description}
        Priority: {priority}
        Assigned Agent: {assigned_agent or 'Unassigned'}
        Status: Created
        
        The task has been added to the task management system.
        """
        
        return result
    
    @kernel_function(
        name="assign_task",
        description="Assign a task to a specific agent"
    )
    def assign_task(self, task_id: str, agent_name: str) -> str:
        """
        Assign a task to an agent.
        
        Args:
            task_id: ID of the task to assign
            agent_name: Name of the agent to assign the task to
            
        Returns:
            Assignment confirmation
        """
        if task_id not in self.tasks:
            return f"Error: Task {task_id} not found"
        
        self.tasks[task_id]["assigned_agent"] = agent_name
        self.tasks[task_id]["status"] = "assigned"
        
        logger.info(f"Assigned task {task_id} to {agent_name}")
        
        return f"""
        Task Assignment Completed:
        
        Task ID: {task_id}
        Task Title: {self.tasks[task_id]['title']}
        Assigned to: {agent_name}
        Status: Assigned
        
        The agent has been notified of the assignment.
        """
    
    @kernel_function(
        name="update_task_status",
        description="Update the status of a task"
    )
    def update_task_status(self, task_id: str, status: str, progress: int = None) -> str:
        """
        Update task status and progress.
        
        Args:
            task_id: ID of the task to update
            status: New status (created, assigned, in_progress, completed, on_hold)
            progress: Progress percentage (0-100)
            
        Returns:
            Status update confirmation
        """
        if task_id not in self.tasks:
            return f"Error: Task {task_id} not found"
        
        self.tasks[task_id]["status"] = status
        if progress is not None:
            self.tasks[task_id]["progress"] = progress
        
        logger.info(f"Updated task {task_id} status to {status}")
        
        return f"""
        Task Status Updated:
        
        Task ID: {task_id}
        Task Title: {self.tasks[task_id]['title']}
        New Status: {status}
        Progress: {self.tasks[task_id]['progress']}%
        
        Status update recorded successfully.
        """
    
    @kernel_function(
        name="get_task_list",
        description="Get list of all tasks with their current status"
    )
    def get_task_list(self, filter_status: Optional[str] = None) -> str:
        """
        Get a list of all tasks.
        
        Args:
            filter_status: Optional status filter
            
        Returns:
            Formatted list of tasks
        """
        if not self.tasks:
            return "No tasks found in the system."
        
        filtered_tasks = self.tasks
        if filter_status:
            filtered_tasks = {
                tid: task for tid, task in self.tasks.items()
                if task["status"] == filter_status
            }
        
        result = f"Task List {f'(Status: {filter_status})' if filter_status else ''}:\n\n"
        
        for task_id, task in filtered_tasks.items():
            result += f"""
            Task ID: {task_id}
            Title: {task['title']}
            Status: {task['status']}
            Progress: {task['progress']}%
            Assigned Agent: {task['assigned_agent'] or 'Unassigned'}
            Priority: {task['priority']}
            ---
            """
        
        return result
    
    @kernel_function(
        name="analyze_workload",
        description="Analyze workload distribution across agents"
    )
    def analyze_workload(self) -> str:
        """
        Analyze workload distribution.
        
        Returns:
            Workload analysis report
        """
        if not self.tasks:
            return "No tasks available for workload analysis."
        
        # Count tasks by agent
        agent_workload = {}
        unassigned_count = 0
        
        for task in self.tasks.values():
            if task["assigned_agent"]:
                agent = task["assigned_agent"]
                if agent not in agent_workload:
                    agent_workload[agent] = {"total": 0, "completed": 0, "in_progress": 0}
                
                agent_workload[agent]["total"] += 1
                if task["status"] == "completed":
                    agent_workload[agent]["completed"] += 1
                elif task["status"] == "in_progress":
                    agent_workload[agent]["in_progress"] += 1
            else:
                unassigned_count += 1
        
        # Generate report
        report = "Workload Analysis Report:\n\n"
        
        for agent, workload in agent_workload.items():
            completion_rate = (workload["completed"] / workload["total"]) * 100 if workload["total"] > 0 else 0
            report += f"""
            Agent: {agent}
            Total Tasks: {workload["total"]}
            Completed: {workload["completed"]}
            In Progress: {workload["in_progress"]}
            Completion Rate: {completion_rate:.1f}%
            ---
            """
        
        if unassigned_count > 0:
            report += f"\nUnassigned Tasks: {unassigned_count}"
        
        report += f"\n\nTotal Tasks in System: {len(self.tasks)}"
        
        return report
    
    @kernel_function(
        name="set_task_dependency",
        description="Set dependencies between tasks"
    )
    def set_task_dependency(self, task_id: str, dependency_task_id: str) -> str:
        """
        Set a dependency between tasks.
        
        Args:
            task_id: ID of the task that depends on another
            dependency_task_id: ID of the task that must be completed first
            
        Returns:
            Dependency setting confirmation
        """
        if task_id not in self.tasks:
            return f"Error: Task {task_id} not found"
        
        if dependency_task_id not in self.tasks:
            return f"Error: Dependency task {dependency_task_id} not found"
        
        if dependency_task_id not in self.tasks[task_id]["dependencies"]:
            self.tasks[task_id]["dependencies"].append(dependency_task_id)
        
        logger.info(f"Set dependency: {task_id} depends on {dependency_task_id}")
        
        return f"""
        Task Dependency Set:
        
        Task: {task_id} ({self.tasks[task_id]['title']})
        Depends on: {dependency_task_id} ({self.tasks[dependency_task_id]['title']})
        
        Dependency relationship established successfully.
        """
