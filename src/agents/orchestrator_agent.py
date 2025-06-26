"""
Orchestrator Agent - Coordinates and manages multiple agents.
"""
import os
import logging
import time
from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from .qna_agent import QnAAgent

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OrchestratorAgent:
    """Orchestrator agent that coordinates with other agents to handle complex requests."""
    
    def __init__(self):
        """Initialize the orchestrator agent."""
        logger.info("🚀 Initializing Orchestrator Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ Kernel created successfully")
            
            self.agent = self._create_agent()
            logger.info("✅ Orchestrator Agent created successfully")
            
            # Initialize sub-agents
            logger.info("🔧 Initializing sub-agents...")
            self.qna_agent = QnAAgent()
            logger.info("✅ QnA Agent initialized")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 Orchestrator Agent fully initialized in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Orchestrator Agent: {e}")
            raise
        
    def _create_kernel(self) -> Kernel:
        """Create and configure the semantic kernel."""
        logger.info("🔧 Creating Semantic Kernel...")
        kernel = Kernel()
        
        # Azure AI Foundry configuration from .env
        endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        logger.info(f"📍 Endpoint: {endpoint}")
        logger.info(f"🤖 Deployment: {deployment_name}")
        logger.info(f"🔐 API Key: {'***SET***' if api_key else 'NOT SET'}")
        
        if not endpoint:
            raise ValueError("AZURE_AI_FOUNDRY_ENDPOINT environment variable is required")
        
        if not deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable is required")
        
        # Use API key authentication
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
        try:
            logger.info(f"� Using API key authentication for {deployment_name}")
            chat_completion = AzureChatCompletion(
                endpoint=endpoint,
                deployment_name=deployment_name,
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise ValueError(f"Failed to authenticate with Azure: {e}. Please ensure AZURE_OPENAI_API_KEY is set correctly.")
        
        kernel.add_service(chat_completion)
        logger.info("✅ Azure OpenAI service added to kernel")
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent for orchestration."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="Orchestrator_Agent",
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

Be professional, clear, and ensure every user interaction is valuable."""
        )
    
    async def _delegate_to_qna(self, question: str, thread: Optional[ChatHistory] = None) -> str:
        """Delegate a question to the QnA agent and return the response.
        
        Args:
            question: The question to ask the QnA agent
            thread: Optional thread for conversation context
            
        Returns:
            The QnA agent's response as a string
        """
        logger.info(f"🔄 Delegating to QnA Agent: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        start_time = time.time()
        
        try:
            response = await self.qna_agent.answer_question(question, thread)
            response_time = time.time() - start_time
            logger.info(f"✅ QnA Agent responded in {response_time:.2f}s: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            return response
        except Exception as e:
            logger.error(f"❌ QnA Agent delegation failed: {e}")
            raise
    
    async def handle_request(self, user_input: str, thread: Optional[ChatHistory] = None) -> str:
        """Handle a user request, coordinating with other agents as needed.
        
        Args:
            user_input: The user's input/request
            thread: Optional chat thread for conversation history
            
        Returns:
            str: The orchestrated response
        """
        logger.info(f"🎯 ORCHESTRATOR: Handling request: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
        start_time = time.time()
        
        if thread is None:
            thread = ChatHistory()
            logger.info("📝 Created new chat history thread")
        else:
            history_count = len([msg for msg in thread.messages])
            logger.info(f"📚 Using existing thread with {history_count} messages")
        
        # Analyze the request type
        logger.info("🔍 Analyzing request type...")
        question_indicators = ["what", "how", "why", "when", "where", "who", "?"]
        is_question = any(indicator in user_input.lower() for indicator in question_indicators)
        word_count = len(user_input.split())
        
        logger.info(f"📊 Analysis: is_question={is_question}, word_count={word_count}")
        
        try:
            if is_question and word_count < 20:  # Simple question
                logger.info("🎯 DECISION: Delegating to QnA Agent (simple question)")
                qna_response = await self._delegate_to_qna(user_input, thread)
                final_response = f"Based on your question, here's what I found:\n\n{qna_response}"
                
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed delegation in {response_time:.2f}s")
                return final_response
                
            else:
                logger.info("🎯 DECISION: Handling directly with Orchestrator Agent (complex request)")
                thread.add_user_message(user_input)
                
                logger.info("🤖 Invoking Orchestrator Agent...")
                invoke_start = time.time()
                responses = []
                async for response in self.agent.invoke(thread):
                    responses.append(str(response))
                    logger.debug(f"📥 Received response chunk: '{str(response)[:50]}{'...' if len(str(response)) > 50 else ''}'")
                
                result = "".join(responses)
                thread.add_assistant_message(result)
                
                invoke_time = time.time() - invoke_start
                total_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Agent invocation completed in {invoke_time:.2f}s")
                logger.info(f"✅ ORCHESTRATOR: Total request handled in {total_time:.2f}s")
                logger.info(f"📤 Final response: '{result[:100]}{'...' if len(result) > 100 else ''}'")
                
                return result
                
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ ORCHESTRATOR: Request failed after {error_time:.2f}s: {e}")
            raise
