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
from .ai_ethics_agent import AIEthicsAgent
from .weather_agent import WeatherAgent
from .support_email_agent import SupportEmailAgent

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
            
            self.ai_ethics_agent = AIEthicsAgent()
            logger.info("✅ AI Ethics Agent initialized")
            
            self.weather_agent = WeatherAgent()
            logger.info("✅ Weather Agent initialized")
            
            self.support_email_agent = SupportEmailAgent()
            logger.info("✅ Support Email Agent initialized")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 Orchestrator Agent fully initialized in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Orchestrator Agent: {e}")
            raise
    
    async def initialize_async_components(self):
        """Initialize async components after the main initialization."""
        logger.info("🔄 Initializing async components...")
        try:
            await self.ai_ethics_agent.initialize_documents()
            logger.info("✅ All async components initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize async components: {e}")
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
            instructions="""You are an intelligent orchestrator that coordinates multiple specialized agents to help users. When no specialized agent is suitable, you handle requests directly with a friendly, helpful, and conversational tone.

Your responsibilities:
1. Analyze user requests to understand their intent and domain
2. Always try to delegate to the most appropriate specialized agent first
3. Handle requests directly only when no agent is suitable (chit chat, general conversation, simple questions outside agent domains)
4. Provide engaging, personable responses for casual conversation
5. Coordinate responses from multiple agents when needed

Available specialized agents:
- QnA Agent: Customer support questions, product information, technical help, how-to questions
- AI Ethics Agent: AI ethics, human-AI dependency, AI societal impact, AI governance, AI bias/fairness
- Weather Agent: Weather conditions, forecasts, temperature, climate information for any location
- Support Email Agent: Email-format support requests requiring professional email responses

Delegation priority (always try these first):
1. Email format or formal support requests → Support Email Agent
2. Weather-related questions → Weather Agent  
3. AI ethics/societal impact questions → AI Ethics Agent
4. Customer support/technical questions → QnA Agent

Handle directly when NO agent is suitable:
- Casual greetings ("hello", "hi", "how are you")
- Personal questions about yourself
- General chit chat and conversation
- Jokes, riddles, or entertainment
- Simple math, basic facts not covered by agents
- Philosophical questions (non-AI related)
- Creative requests (stories, poems, etc.)
- General life advice or opinions

When handling directly:
- Be warm, friendly, and conversational
- Show personality and engage naturally
- Provide helpful and thoughtful responses
- Ask follow-up questions to keep conversation flowing
- Be honest about your capabilities and limitations

When delegating:
- Briefly mention which agent you're consulting
- Present the specialist's response clearly
- Add follow-up suggestions if helpful

Always prioritize delegating to specialists for their domains, but be a great conversationalist for everything else!"""
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
    
    async def _delegate_to_ai_ethics(self, question: str, thread: Optional[ChatHistory] = None) -> str:
        """Delegate a question to the AI Ethics agent and return the response.
        
        Args:
            question: The question to ask the AI Ethics agent
            thread: Optional thread for conversation context
            
        Returns:
            The AI Ethics agent's response as a string
        """
        logger.info(f"🔄 Delegating to AI Ethics Agent: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        start_time = time.time()
        
        try:
            response = await self.ai_ethics_agent.answer_question(question, thread)
            response_time = time.time() - start_time
            logger.info(f"✅ AI Ethics Agent responded in {response_time:.2f}s: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            return response
        except Exception as e:
            logger.error(f"❌ AI Ethics Agent delegation failed: {e}")
            raise
    
    async def _delegate_to_weather(self, question: str, thread: Optional[ChatHistory] = None) -> str:
        """Delegate a question to the Weather agent and return the response.
        
        Args:
            question: The question to ask the Weather agent
            thread: Optional thread for conversation context
            
        Returns:
            The Weather agent's response as a string
        """
        logger.info(f"🔄 Delegating to Weather Agent: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        start_time = time.time()
        
        try:
            response = await self.weather_agent.invoke(question, thread)
            response_time = time.time() - start_time
            logger.info(f"✅ Weather Agent responded in {response_time:.2f}s: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            return response
        except Exception as e:
            logger.error(f"❌ Weather Agent delegation failed: {e}")
            raise
    
    async def _delegate_to_support_email(self, message: str, thread: Optional[ChatHistory] = None) -> str:
        """Delegate a message to the Support Email agent and return the response.
        
        Args:
            message: The message to send to the Support Email agent
            thread: Optional thread for conversation context
            
        Returns:
            The Support Email agent's response as a string
        """
        logger.info(f"🔄 Delegating to Support Email Agent: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        start_time = time.time()
        
        try:
            response = await self.support_email_agent.invoke(message, thread)
            response_time = time.time() - start_time
            logger.info(f"✅ Support Email Agent responded in {response_time:.2f}s: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            return response
        except Exception as e:
            logger.error(f"❌ Support Email Agent delegation failed: {e}")
            raise
    
    def _analyze_request_type(self, user_input: str) -> dict:
        """Analyze the user's request to determine the best routing strategy.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            dict: Analysis results with routing recommendations
        """
        user_lower = user_input.lower().strip()
        
        # Check for email format
        is_email_format = self.support_email_agent.is_email_format(user_input)
        
        # Weather keywords
        weather_keywords = [
            "weather", "temperature", "rain", "snow", "sunny", "cloudy", "wind",
            "humidity", "forecast", "climate", "precipitation", "storm", "sunshine",
            "degrees", "celsius", "fahrenheit", "hot", "cold", "warm", "cool",
            "weather in", "weather for", "how's the weather", "what's the weather",
            "meteorology", "atmospheric", "barometric"
        ]
        
        # AI Ethics keywords
        ai_ethics_keywords = [
            "ai ethics", "artificial intelligence ethics", "ai bias", "ai fairness",
            "human ai dependency", "human dependence", "ai dependency", "ai dependence",
            "ai impact", "ai society", "ai societal", "ethical ai", "ai governance",
            "ai regulation", "ai policy", "ai philosophy", "ai consciousness",
            "human ai relationship", "ai and humanity", "ai risk", "ai safety",
            "algorithmic bias", "machine learning ethics", "ai accountability",
            "automation ethics", "ai employment", "ai education", "ai healthcare ethics",
            "algorithmic fairness", "ai transparency"
        ]
        
        # Customer support keywords
        support_keywords = [
            "help", "support", "problem", "issue", "error", "bug", "troubleshoot",
            "how do i", "how to", "can't", "won't", "doesn't work", "not working",
            "login", "password", "account", "billing", "subscription", "cancel",
            "refund", "technical", "feature", "tutorial", "guide", "instructions"
        ]
        
        # Chit chat / casual conversation keywords
        chitchat_keywords = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "nice to meet", "thanks", "thank you",
            "bye", "goodbye", "see you", "have a great", "who are you",
            "what are you", "tell me about yourself", "joke", "funny", "story",
            "what do you think", "opinion", "favorite", "like", "love", "hate"
        ]
        
        # Simple math/facts keywords
        simple_keywords = [
            "what is", "calculate", "math", "add", "subtract", "multiply", "divide",
            "convert", "translate", "define", "meaning", "capital of", "population",
            "when was", "who is", "where is"
        ]
        
        # Analyze matches
        weather_score = sum(1 for keyword in weather_keywords if keyword in user_lower)
        ai_ethics_score = sum(1 for keyword in ai_ethics_keywords if keyword in user_lower)
        support_score = sum(1 for keyword in support_keywords if keyword in user_lower)
        chitchat_score = sum(1 for keyword in chitchat_keywords if keyword in user_lower)
        simple_score = sum(1 for keyword in simple_keywords if keyword in user_lower)
        
        # Additional analysis
        has_question_words = any(word in user_lower for word in ["what", "how", "why", "when", "where", "who", "?"])
        word_count = len(user_input.split())
        is_greeting = any(greeting in user_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"])
        
        return {
            "is_email_format": is_email_format,
            "weather_score": weather_score,
            "ai_ethics_score": ai_ethics_score,
            "support_score": support_score,
            "chitchat_score": chitchat_score,
            "simple_score": simple_score,
            "has_question_words": has_question_words,
            "word_count": word_count,
            "is_greeting": is_greeting,
            "user_lower": user_lower
        }

    async def handle_request(self, user_input: str, thread: Optional[ChatHistory] = None) -> str:
        """Handle a user request, always trying to delegate to appropriate agents first.
        
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
        
        # Analyze the request
        logger.info("🔍 Analyzing request for optimal routing...")
        analysis = self._analyze_request_type(user_input)
        
        logger.info(f"📊 Analysis: email={analysis['is_email_format']}, weather={analysis['weather_score']}, "
                   f"ai_ethics={analysis['ai_ethics_score']}, support={analysis['support_score']}, "
                   f"chitchat={analysis['chitchat_score']}, simple={analysis['simple_score']}")
        
        try:
            # Priority 1: Email format support requests
            if analysis["is_email_format"]:
                logger.info("🎯 DECISION: Delegating to Support Email Agent (email format detected)")
                response = await self._delegate_to_support_email(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed Support Email delegation in {response_time:.2f}s")
                return response
            
            # Priority 2: Weather requests (strong indicator)
            elif analysis["weather_score"] >= 2:
                logger.info("🎯 DECISION: Delegating to Weather Agent (weather keywords detected)")
                response = await self._delegate_to_weather(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed Weather delegation in {response_time:.2f}s")
                return response
            
            # Priority 3: AI Ethics requests (strong indicator)
            elif analysis["ai_ethics_score"] >= 2:
                logger.info("🎯 DECISION: Delegating to AI Ethics Agent (AI ethics keywords detected)")
                response = await self._delegate_to_ai_ethics(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed AI Ethics delegation in {response_time:.2f}s")
                return response
            
            # Priority 4: Customer support requests
            elif analysis["support_score"] >= 2 or (analysis["support_score"] >= 1 and analysis["has_question_words"]):
                logger.info("🎯 DECISION: Delegating to QnA Agent (support keywords detected)")
                response = await self._delegate_to_qna(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed QnA delegation in {response_time:.2f}s")
                return response
            
            # Priority 5: Single keyword matches (weaker signals but still worth trying)
            elif analysis["weather_score"] >= 1:
                logger.info("🎯 DECISION: Delegating to Weather Agent (weather keyword detected)")
                response = await self._delegate_to_weather(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed Weather delegation in {response_time:.2f}s")
                return response
                
            elif analysis["ai_ethics_score"] >= 1:
                logger.info("🎯 DECISION: Delegating to AI Ethics Agent (AI ethics keyword detected)")
                response = await self._delegate_to_ai_ethics(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed AI Ethics delegation in {response_time:.2f}s")
                return response
                
            elif analysis["support_score"] >= 1 and analysis["has_question_words"]:
                logger.info("🎯 DECISION: Delegating to QnA Agent (support-related question)")
                response = await self._delegate_to_qna(user_input, thread)
                response_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Completed QnA delegation in {response_time:.2f}s")
                return response
            
            # Fallback: Handle directly (chit chat, general conversation, simple questions)
            else:
                logger.info("🎯 DECISION: Handling directly - chit chat, general conversation, or non-agent domain")
                thread.add_user_message(user_input)
                
                logger.info("🤖 Invoking Orchestrator Agent for direct handling...")
                invoke_start = time.time()
                responses = []
                async for response in self.agent.invoke(thread):
                    responses.append(str(response))
                    logger.debug(f"📥 Received response chunk: '{str(response)[:50]}{'...' if len(str(response)) > 50 else ''}'")
                
                result = "".join(responses)
                thread.add_assistant_message(result)
                
                invoke_time = time.time() - invoke_start
                total_time = time.time() - start_time
                logger.info(f"✅ ORCHESTRATOR: Direct handling completed in {invoke_time:.2f}s")
                logger.info(f"✅ ORCHESTRATOR: Total request handled in {total_time:.2f}s")
                logger.info(f"📤 Final response: '{result[:100]}{'...' if len(result) > 100 else ''}'")
                
                return result
                
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ ORCHESTRATOR: Request failed after {error_time:.2f}s: {e}")
            raise
    
    async def invoke(self, user_input: str, thread: Optional[ChatHistory] = None) -> str:
        """Public interface to invoke the orchestrator agent.
        
        Args:
            user_input: The user's input/request
            thread: Optional chat thread for conversation history
            
        Returns:
            str: The orchestrated response
        """
        return await self.handle_request(user_input, thread)
    
    def get_available_agents(self) -> list:
        """Get list of available agent capabilities.
        
        Returns:
            list: List of agent descriptions
        """
        return [
            {
                "name": "Support Email Agent",
                "description": "Handles email-format support requests with professional email responses",
                "domains": ["email support", "formal inquiries", "customer service emails"]
            },
            {
                "name": "Weather Agent", 
                "description": "Provides current weather information for any location worldwide",
                "domains": ["weather", "temperature", "forecasts", "climate conditions"]
            },
            {
                "name": "AI Ethics Agent",
                "description": "Specialized in AI ethics, human-AI dependency, and ethical analysis",
                "domains": ["AI ethics", "algorithmic bias", "AI governance", "human-AI relationships"]
            },
            {
                "name": "QnA Agent",
                "description": "Handles general customer support questions and informational responses", 
                "domains": ["customer support", "technical help", "product information", "how-to guides"]
            },
            {
                "name": "Orchestrator (Direct)",
                "description": "Handles chit chat, general conversation, and questions outside specialist domains",
                "domains": ["greetings", "casual conversation", "general knowledge", "creative requests"]
            }
        ]
    
    def get_routing_statistics(self) -> dict:
        """Get statistics about agent routing decisions (placeholder for future implementation).
        
        Returns:
            dict: Routing statistics
        """
        # This could be expanded to track routing decisions over time
        return {
            "total_requests": 0,
            "agent_usage": {
                "support_email": 0,
                "weather": 0, 
                "ai_ethics": 0,
                "qna": 0,
                "direct": 0
            },
            "success_rate": 0.0
        }
