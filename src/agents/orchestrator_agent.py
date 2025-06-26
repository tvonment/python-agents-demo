"""
Orchestrator Agent - Coordinates and manages multiple agents.
"""
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.agent_thread import ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from .qna_agent import QnAAgent


class OrchestratorAgent:
    """Orchestrator agent that coordinates with other agents to handle complex requests."""
    
    def __init__(self, endpoint: str, deployment_name: str):
        """Initialize the Orchestrator agent.
        
        Args:
            endpoint: Azure AI Foundry Resource endpoint
            deployment_name: Azure OpenAI deployment name
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.kernel = self._create_kernel()
        self.agent = self._create_agent()
        
        # Initialize sub-agents
        self.qna_agent = QnAAgent(endpoint, deployment_name)
        
    def _create_kernel(self) -> Kernel:
        """Create and configure the Semantic Kernel."""
        kernel = Kernel()
        
        # Create Azure OpenAI chat completion service with managed identity
        chat_completion = AzureChatCompletion(
            endpoint=self.endpoint,
            deployment_name=self.deployment_name,
            # No API key provided - will use managed identity authentication
            service_id="orchestrator-service"
        )
        
        kernel.add_service(chat_completion)
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent for orchestration."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="Orchestrator Agent",
            instructions="""You are an intelligent orchestrator that coordinates multiple specialized agents to help users.

Your responsibilities:
1. Analyze user requests to understand their intent and complexity
2. Determine whether to handle requests directly or delegate to specialized agents
3. Coordinate responses from multiple agents when needed
4. Provide clear, comprehensive answers to users

Available agents:
- QnA Agent: Handles general questions and provides informational responses

Decision criteria:
- For simple questions and general inquiries: Delegate to QnA Agent
- For complex requests requiring coordination: Handle directly while consulting agents
- Always ensure the user gets a complete and helpful response

When delegating:
1. Clearly explain what you're doing
2. Present the agent's response
3. Add any additional context or follow-up suggestions if helpful

Be professional, clear, and ensure every user interaction is valuable.""",
            service_id="orchestrator-service"
        )
    
    async def _delegate_to_qna(self, question: str, thread: Optional[ChatHistoryAgentThread] = None) -> str:
        """Delegate a question to the QnA agent and return the response.
        
        Args:
            question: The question to ask the QnA agent
            thread: Optional thread for conversation context
            
        Returns:
            The QnA agent's response as a string
        """
        response_parts = []
        async for response in self.qna_agent.answer_question(question, thread):
            if response.content:
                response_parts.append(response.content)
        return " ".join(response_parts)
    
    async def handle_request(self, user_input: str, thread: Optional[ChatHistoryAgentThread] = None) -> AsyncGenerator[ChatMessageContent, None]:
        """Handle a user request, coordinating with other agents as needed.
        
        Args:
            user_input: The user's input/request
            thread: Optional chat thread for conversation history
            
        Yields:
            ChatMessageContent: The orchestrated response messages
        """
        if thread is None:
            thread = ChatHistoryAgentThread()
        
        # For this initial implementation, we'll analyze the request and decide
        # whether to delegate to the QnA agent or handle it directly
        
        # Simple heuristic: if it's a straightforward question, delegate to QnA
        question_indicators = ["what", "how", "why", "when", "where", "who", "?"]
        is_question = any(indicator in user_input.lower() for indicator in question_indicators)
        
        if is_question and len(user_input.split()) < 20:  # Simple question
            # Delegate to QnA agent
            qna_response = await self._delegate_to_qna(user_input, thread)
            
            # Create orchestrator response that includes the QnA response
            orchestrator_prompt = f"""The user asked: "{user_input}"

I've consulted with our QnA specialist who provided this response:
"{qna_response}"

Please provide a brief introduction to this response and any additional helpful context or suggestions."""
            
            async for response in self.agent.invoke(
                messages=orchestrator_prompt,
                thread=thread
            ):
                yield response
        else:
            # Handle directly as orchestrator
            async for response in self.agent.invoke(
                messages=user_input,
                thread=thread
            ):
                yield response
