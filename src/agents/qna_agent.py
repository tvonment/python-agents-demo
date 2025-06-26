"""
QnA Agent - A simple Q&A agent using Azure AI Foundry.
"""

import os
import logging
import time
from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class QnAAgent:
    """A Q&A agent that answers user questions using Azure AI Foundry."""
    
    def __init__(self):
        """Initialize the QnA agent."""
        logger.info("🚀 Initializing QnA Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ QnA Kernel created successfully")
            
            self.agent = self._create_agent()
            logger.info("✅ QnA Agent created successfully")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 QnA Agent fully initialized in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize QnA Agent: {e}")
            raise
    
    def _create_kernel(self) -> Kernel:
        """Create and configure the semantic kernel."""
        logger.info("🔧 Creating QnA Kernel...")
        kernel = Kernel()
        
        # Azure AI Foundry configuration from .env
        endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        logger.info(f"📍 QnA Endpoint: {endpoint}")
        logger.info(f"🤖 QnA Deployment: {deployment_name}")
        logger.info(f"🔐 QnA API Key: {'***SET***' if api_key else 'NOT SET'}")
        
        if not endpoint:
            raise ValueError("AZURE_AI_FOUNDRY_ENDPOINT environment variable is required")
        
        if not deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable is required")
        
        # Try API key first (for local development), then managed identity (for Azure environments)
        try:
            if api_key:
                logger.info(f"🔑 QnA using API key authentication for {deployment_name}")
                chat_completion = AzureChatCompletion(
                    endpoint=endpoint,
                    deployment_name=deployment_name,
                    api_key=api_key
                )
            else:
                logger.info(f"🔐 QnA using managed identity authentication for {deployment_name}")
                # For Azure CLI or managed identity
                from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
                
                # Try Azure CLI first (for local dev), then managed identity
                credential = ChainedTokenCredential(
                    AzureCliCredential(),
                    ManagedIdentityCredential()
                )
                
                chat_completion = AzureChatCompletion(
                    endpoint=endpoint,
                    deployment_name=deployment_name,
                    ad_token_provider=credential.get_token
                )
        except Exception as e:
            logger.error(f"❌ QnA Authentication failed: {e}")
            raise ValueError(f"Failed to authenticate with Azure: {e}. Please set AZURE_OPENAI_API_KEY or ensure Azure CLI is logged in.")
        
        kernel.add_service(chat_completion)
        logger.info("✅ QnA Azure OpenAI service added to kernel")
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent with system prompt."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="QnA_Agent",
            instructions="""You are a helpful Q&A assistant. Your role is to:
            
1. Answer user questions clearly and concisely
2. Provide accurate information based on your knowledge
3. If you don't know something, admit it rather than guessing
4. Ask for clarification if the question is unclear
5. Be friendly and professional in your responses

Always aim to be helpful while being honest about the limitations of your knowledge."""
        )
    
    async def answer_question(self, question: str, thread: Optional[ChatHistory] = None) -> str:
        """Answer a user question.
        
        Args:
            question: The user's question
            thread: Optional chat thread for conversation history
            
        Returns:
            str: The agent's response
        """
        logger.info(f"❓ QNA AGENT: Answering question: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        start_time = time.time()
        
        try:
            if thread is None:
                thread = ChatHistory()
                logger.info("📝 QnA created new chat history thread")
            else:
                history_count = len([msg for msg in thread.messages])
                logger.info(f"📚 QnA using existing thread with {history_count} messages")
            
            logger.info("💭 Adding user question to thread...")
            thread.add_user_message(question)
            
            logger.info("🤖 Invoking QnA Agent...")
            invoke_start = time.time()
            responses = []
            response_count = 0
            
            async for response in self.agent.invoke(thread):
                response_count += 1
                responses.append(str(response))
                logger.debug(f"📥 QnA received response chunk #{response_count}: '{str(response)[:50]}{'...' if len(str(response)) > 50 else ''}'")
            
            result = "".join(responses)
            thread.add_assistant_message(result)
            
            invoke_time = time.time() - invoke_start
            total_time = time.time() - start_time
            
            logger.info(f"✅ QNA AGENT: Agent invocation completed in {invoke_time:.2f}s")
            logger.info(f"✅ QNA AGENT: Total question answered in {total_time:.2f}s")
            logger.info(f"📤 QnA response: '{result[:100]}{'...' if len(result) > 100 else ''}'")
            logger.info(f"📊 QnA stats: {len(result)} chars, {response_count} response chunks")
            
            return result
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ QNA AGENT: Question failed after {error_time:.2f}s: {e}")
            raise
