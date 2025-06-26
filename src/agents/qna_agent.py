"""
QnA Agent - A simple Q&A agent with system prompt only.
"""
import asyncio
from typing import AsyncGenerator, List, Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.agent_thread import ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent


class QnAAgent:
    """A simple Question and Answer agent using Semantic Kernel ChatCompletionAgent."""
    
    def __init__(self, endpoint: str, deployment_name: str):
        """Initialize the QnA agent.
        
        Args:
            endpoint: Azure AI Foundry Resource endpoint
            deployment_name: Azure OpenAI deployment name
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.kernel = self._create_kernel()
        self.agent = self._create_agent()
        
    def _create_kernel(self) -> Kernel:
        """Create and configure the Semantic Kernel."""
        kernel = Kernel()
        
        # Create Azure OpenAI chat completion service with managed identity
        chat_completion = AzureChatCompletion(
            endpoint=self.endpoint,
            deployment_name=self.deployment_name,
            # No API key provided - will use managed identity authentication
            service_id="qna-service"
        )
        
        kernel.add_service(chat_completion)
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent with system prompt."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="QnA Agent",
            instructions="""You are a helpful Q&A assistant. Your role is to:
            
1. Answer user questions clearly and concisely
2. Provide accurate information based on your knowledge
3. If you don't know something, admit it rather than guessing
4. Ask for clarification if the question is unclear
5. Be friendly and professional in your responses

Always aim to be helpful while being honest about the limitations of your knowledge.""",
            service_id="qna-service"
        )
    
    async def answer_question(self, question: str, thread: Optional[ChatHistoryAgentThread] = None) -> AsyncGenerator[ChatMessageContent, None]:
        """Answer a user question.
        
        Args:
            question: The user's question
            thread: Optional chat thread for conversation history
            
        Yields:
            ChatMessageContent: The agent's response messages
        """
        if thread is None:
            thread = ChatHistoryAgentThread()
            
        async for response in self.agent.invoke(
            messages=question,
            thread=thread
        ):
            yield response
