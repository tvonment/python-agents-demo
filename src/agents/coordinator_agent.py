"""
Coordinator agent for orchestrating multi-agent interactions.
"""
import logging
from typing import Dict, List, Optional, Any
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, AgentGroupChatSettings
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy, KernelFunctionTerminationStrategy
from semantic_kernel.contents import ChatHistory

from .base_agent import BaseAgent
from ..plugins.coordination_plugins import TaskManagementPlugin


logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """Agent responsible for coordinating multi-agent interactions."""
    
    def __init__(self, name: str = "CoordinatorAgent"):
        instructions = """
        You are a Coordinator Agent responsible for orchestrating multi-agent collaborations.
        
        Your responsibilities include:
        - Analyzing complex tasks and breaking them down into subtasks
        - Assigning appropriate agents to specific tasks
        - Coordinating communication between agents
        - Ensuring task completion and quality
        - Synthesizing results from multiple agents
        
        Always consider the strengths of each agent and assign tasks accordingly.
        Monitor progress and adjust coordination as needed.
        """
        
        super().__init__(
            name=name,
            instructions=instructions,
            description="Specialized agent for coordinating multi-agent interactions"
        )
        
        self.available_agents: Dict[str, BaseAgent] = {}
        self.group_chat: Optional[AgentGroupChat] = None
    
    def _register_plugins(self, kernel: Kernel) -> None:
        """Register coordination-specific plugins."""
        # Add task management plugin
        task_plugin = TaskManagementPlugin()
        kernel.add_plugin(task_plugin, plugin_name="TaskManagement")
        
        logger.info(f"Registered plugins for {self.name}")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent for coordination."""
        self.available_agents[agent.name] = agent
        logger.info(f"Registered agent {agent.name} with coordinator")
    
    def create_group_chat(self, agents: List[BaseAgent]) -> AgentGroupChat:
        """Create a group chat with specified agents."""
        # Register all agents
        for agent in agents:
            self.register_agent(agent)
        
        # Add coordinator to the group
        all_agents = [self.agent] + [agent.agent for agent in agents]
        
        # Create group chat settings
        settings = AgentGroupChatSettings(
            selection_strategy=KernelFunctionSelectionStrategy(
                function=self._create_selection_function(),
                kernel=self.kernel,
                arguments={"agents": [agent.name for agent in all_agents]},
                result_parser=lambda result: result.value[0].name,
                agent_variable_name="agents",
                history_variable_name="history"
            ),
            termination_strategy=KernelFunctionTerminationStrategy(
                function=self._create_termination_function(),
                kernel=self.kernel,
                arguments={"max_rounds": 10},
                result_parser=lambda result: "terminate" in result.value[0].lower(),
                agent_variable_name="agents",
                history_variable_name="history"
            )
        )
        
        self.group_chat = AgentGroupChat(
            agents=all_agents,
            settings=settings
        )
        
        return self.group_chat
    
    def _create_selection_function(self):
        """Create function for agent selection strategy."""
        @self.kernel.function(
            name="select_next_agent",
            description="Select the next agent to speak in the conversation"
        )
        def select_next_agent(
            agents: List[str],
            history: ChatHistory
        ) -> str:
            """Select the most appropriate agent for the next turn."""
            if not history.messages:
                return agents[0] if agents else "CoordinatorAgent"
            
            last_message = history.messages[-1].content
            
            # Simple selection logic - can be enhanced
            if "research" in last_message.lower() or "analyze" in last_message.lower():
                return "ResearchAgent" if "ResearchAgent" in agents else agents[0]
            elif "write" in last_message.lower() or "content" in last_message.lower():
                return "WritingAgent" if "WritingAgent" in agents else agents[0]
            else:
                return "CoordinatorAgent"
        
        return select_next_agent
    
    def _create_termination_function(self):
        """Create function for termination strategy."""
        @self.kernel.function(
            name="should_terminate",
            description="Determine if the conversation should terminate"
        )
        def should_terminate(
            agents: List[str],
            history: ChatHistory,
            max_rounds: int = 10
        ) -> str:
            """Determine if the conversation should end."""
            if len(history.messages) >= max_rounds * 2:  # Rough estimate
                return "terminate - maximum rounds reached"
            
            if not history.messages:
                return "continue"
            
            last_message = history.messages[-1].content.lower()
            
            # Check for completion indicators
            if any(word in last_message for word in ["complete", "finished", "done", "final"]):
                return "terminate - task completed"
            
            return "continue"
        
        return should_terminate
    
    async def coordinate_task(
        self,
        task_description: str,
        agents: List[BaseAgent],
        max_rounds: int = 10
    ) -> List[str]:
        """Coordinate a complex task using multiple agents."""
        # Create group chat
        group_chat = self.create_group_chat(agents)
        
        # Start the conversation
        chat_history = ChatHistory()
        
        coordination_prompt = f"""
        Task to coordinate: {task_description}
        
        Available agents: {[agent.name for agent in agents]}
        
        Please break down this task and coordinate with the appropriate agents to complete it.
        Each agent has specific capabilities:
        - ResearchAgent: Information gathering and analysis
        - WritingAgent: Content creation and editing
        
        Begin coordination now.
        """
        
        responses = []
        
        try:
            async for response in group_chat.invoke(coordination_prompt):
                responses.append(f"{response.agent.name}: {response.content}")
                logger.info(f"Group chat response from {response.agent.name}")
                
                if len(responses) >= max_rounds:
                    break
            
            return responses
            
        except Exception as e:
            logger.error(f"Error during task coordination: {str(e)}")
            raise
    
    async def analyze_task_requirements(self, task: str) -> Dict[str, Any]:
        """Analyze task requirements and suggest agent assignments."""
        analysis_prompt = f"""
        Analyze the following task and provide recommendations:
        
        Task: {task}
        
        Please provide:
        1. Task complexity assessment
        2. Required capabilities
        3. Recommended agent assignments
        4. Estimated timeline
        5. Success criteria
        
        Available agents and their capabilities:
        - ResearchAgent: Information gathering, data analysis, fact-checking
        - WritingAgent: Content creation, editing, summarization
        
        Format your response as a structured analysis.
        """
        
        response = await self.invoke(analysis_prompt)
        return {"analysis": response.content}
