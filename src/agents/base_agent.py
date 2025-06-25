"""
Base agent class for the multi-agent solution.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion
from semantic_kernel.contents import ChatHistory, ChatMessageContent
from azure.identity import DefaultAzureCredential

from ..config import settings


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent solution."""
    
    def __init__(
        self,
        name: str,
        instructions: str,
        description: Optional[str] = None,
        model_deployment_name: Optional[str] = None
    ):
        self.name = name
        self.instructions = instructions
        self.description = description or f"Agent: {name}"
        self.model_deployment_name = model_deployment_name or settings.default_model_deployment_name
        
        self._kernel: Optional[Kernel] = None
        self._agent: Optional[ChatCompletionAgent] = None
        
    @property
    def kernel(self) -> Kernel:
        """Get or create the kernel for this agent."""
        if self._kernel is None:
            self._kernel = self._create_kernel()
        return self._kernel
    
    @property
    def agent(self) -> ChatCompletionAgent:
        """Get or create the chat completion agent."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent
    
    def _create_kernel(self) -> Kernel:
        """Create and configure the kernel with AI services."""
        kernel = Kernel()
        
        # Check if we have the required configuration
        if not settings.primary_endpoint:
            raise ValueError(
                "No Azure AI endpoint configured. Please set either "
                "AZURE_AI_INFERENCE_ENDPOINT or AZURE_AI_FOUNDRY_PROJECT_ENDPOINT "
                "in your .env file"
            )
        
        # Add chat completion service
        if settings.use_entra_id:
            # Use Entra ID authentication
            credential = DefaultAzureCredential()
            chat_service = AzureAIInferenceChatCompletion(
                ai_model_id=self.model_deployment_name,
                endpoint=settings.primary_endpoint,
                credential=credential
            )
        else:
            # Use API key authentication
            if not settings.primary_api_key:
                raise ValueError(
                    "No API key configured. Please set either "
                    "AZURE_AI_INFERENCE_API_KEY or AZURE_AI_FOUNDRY_API_KEY "
                    "in your .env file, or configure Entra ID authentication"
                )
            
            chat_service = AzureAIInferenceChatCompletion(
                ai_model_id=self.model_deployment_name,
                endpoint=settings.primary_endpoint,
                api_key=settings.primary_api_key
            )
        
        kernel.add_service(chat_service)
        
        # Add any plugins
        self._register_plugins(kernel)
        
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the chat completion agent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name=self.name,
            instructions=self.instructions,
            description=self.description
        )
    
    @abstractmethod
    def _register_plugins(self, kernel: Kernel) -> None:
        """Register plugins specific to this agent."""
        pass
    
    async def invoke(
        self,
        message: str,
        chat_history: Optional[ChatHistory] = None
    ) -> ChatMessageContent:
        """Invoke the agent with a message."""
        try:
            if chat_history is None:
                chat_history = ChatHistory()
            
            chat_history.add_user_message(message)
            
            response = await self.agent.invoke(chat_history)
            
            logger.info(f"Agent {self.name} responded to: {message[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error invoking agent {self.name}: {str(e)}")
            raise
    
    async def get_response_stream(
        self,
        message: str,
        chat_history: Optional[ChatHistory] = None
    ):
        """Get streaming response from the agent."""
        try:
            if chat_history is None:
                chat_history = ChatHistory()
            
            chat_history.add_user_message(message)
            
            async for response in self.agent.invoke_stream(chat_history):
                yield response
                
        except Exception as e:
            logger.error(f"Error streaming from agent {self.name}: {str(e)}")
            raise
