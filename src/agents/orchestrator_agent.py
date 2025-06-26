"""
Orchestrator Agent - Coordinates and manages multiple agents using Magentic workflows.
"""
import os
import logging
import time
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, MagenticOrchestration, StandardMagenticManager
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import json
from .qna_agent import QnAAgent
from .ai_ethics_agent import AIEthicsAgent
from .weather_agent import WeatherAgent
from .support_email_agent import SupportEmailAgent

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class AgentResponse:
    """Response from an individual agent."""
    agent_name: str
    response: str
    execution_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class RoutingDecision:
    """Decision about which agents to involve."""
    agents_to_call: List[str]
    reasoning: str
    is_multi_agent: bool
    primary_agent: Optional[str] = None

class OrchestratorAgent:
    """Orchestrator agent that coordinates with other agents to handle complex requests."""
    
    def __init__(self):
        """Initialize the orchestrator agent."""
        logger.info("🚀 Initializing Orchestrator Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ Kernel created successfully")
            
            # Create ChatCompletion agent and routing agent
            self.agent = self._create_agent()
            logger.info("✅ Orchestrator Agent created successfully")
            
            self.routing_agent = self._create_routing_agent()
            logger.info("✅ Routing Agent created successfully")
            
            # Initialize Magentic orchestration
            chat_service = self.kernel.get_service("default")  # Get the Azure OpenAI service
            self.magentic_manager = StandardMagenticManager(chat_completion_service=chat_service)
            
            # Create member agents for Magentic orchestration
            self.magentic_members = self._create_magentic_members()
            
            self.magentic_orchestration = MagenticOrchestration(
                members=self.magentic_members,
                manager=self.magentic_manager,
                agent_response_callback=self._agent_response_callback
            )
            logger.info("✅ Magentic Orchestration initialized successfully")
            
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
    
    def _create_routing_agent(self) -> ChatCompletionAgent:
        """Create the routing agent for intelligent request analysis."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="Routing_Agent",
            instructions="""You are an intelligent routing system for a multi-agent platform. Your job is to analyze user requests and make smart decisions about which agents should handle them.

Available specialized agents:
- weather_agent: Weather conditions, forecasts, temperature, climate for any location
- ai_ethics_agent: AI ethics, bias, human-AI dependency, AI governance, algorithmic fairness  
- qna_agent: Customer support, technical help, product information, how-to questions
- support_email_agent: Professional email formatting (use with other agents for content + formatting)
- orchestrator_direct: Casual conversation, greetings, general knowledge, creative requests

**Email Formatting Logic:**
- If request needs EMAIL FORMAT (has email indicators like "Subject:", "Dear", formal language), use TWO agents:
  1. Content agent (weather_agent, ai_ethics_agent, qna_agent, or orchestrator_direct) 
  2. support_email_agent for professional formatting
- This creates is_multi_agent: true workflows where content is retrieved first, then formatted as email

**Single Agent Logic:**
- Use single agents for regular requests that don't need email formatting

When given a user request, analyze it and respond with a JSON object in exactly this format:
{
    "agents_to_call": ["agent_name"] or ["content_agent", "support_email_agent"],
    "reasoning": "Brief explanation of why these agents were chosen",
    "is_multi_agent": false or true,
    "primary_agent": "primary_agent_name"
}

Examples:
- "What's the weather in Paris?" → {"agents_to_call": ["weather_agent"], "reasoning": "Weather query", "is_multi_agent": false, "primary_agent": "weather_agent"}
- "Subject: Weather Request\nDear Support,\nWhat's the weather in Paris?" → {"agents_to_call": ["weather_agent", "support_email_agent"], "reasoning": "Weather query requiring email format", "is_multi_agent": true, "primary_agent": "weather_agent"}
- AI ethics topics → {"agents_to_call": ["ai_ethics_agent"], "reasoning": "AI ethics topic", "is_multi_agent": false, "primary_agent": "ai_ethics_agent"}
- Casual chat → {"agents_to_call": ["orchestrator_direct"], "reasoning": "Casual conversation", "is_multi_agent": false, "primary_agent": "orchestrator_direct"}

Always respond with valid JSON only."""
        )

    async def _route_with_magentic(self, user_input: str) -> RoutingDecision:
        """Use Magentic orchestration to intelligently route and handle requests.
        
        Args:
            user_input: The user's request to analyze
            
        Returns:
            RoutingDecision object
        
        Note:
            Email-formatted requests are automatically routed to direct routing
            to prevent orchestration loops. This ensures email formatting only
            happens as the final step, never as input to Magentic orchestration.
        """
        try:
            # Check if the request is suitable for Magentic orchestration
            # Email requests are blocked to prevent loops - they use direct routing only
            if self._should_use_magentic_orchestration(user_input):
                logger.info("🧠 Using Magentic orchestration for complex task")
                return await self._use_magentic_orchestration(user_input)
            else:
                logger.info("🎯 Using direct routing for simple request")
                return await self._use_direct_routing(user_input)
                
        except Exception as e:
            logger.warning(f"⚠️ Magentic routing failed: {e}")
            raise
    
    def _should_use_magentic_orchestration(self, user_input: str) -> bool:
        """Determine if a request should use Magentic orchestration.
        
        Args:
            user_input: The user's input
            
        Returns:
            bool: True if Magentic orchestration should be used
        """
        user_input_lower = user_input.lower()
        
        # IMPORTANT: Never use Magentic orchestration for email-formatted requests
        # Email formatting should only happen at the final step via direct routing
        # This prevents loops where Magentic processes email content and creates more email content
        email_indicators = ['email', 'formal', 'professional', 'subject:', 'dear ', 'best regards', '@']
        is_email_request = any(indicator in user_input_lower for indicator in email_indicators)
        
        if is_email_request:
            logger.info("📧 Email request detected - blocking Magentic orchestration to prevent loops")
            return False
        
        # Use Magentic for complex, multi-step tasks that might benefit from multiple agents
        complex_indicators = [
            "compare", "analyze", "research", "investigate", "study", "examine",
            "evaluate", "assess", "report", "comprehensive", "detailed",
            "multiple", "various", "different", "both", "all", "several"
        ]
        
        # Check if this is a complex task (only for non-email requests)
        is_complex_task = any(indicator in user_input_lower for indicator in complex_indicators) and len(user_input.split()) > 10
        
        if is_complex_task:
            logger.info("🧠 Complex task detected - using Magentic orchestration")
            return True
        
        logger.info("🎯 Simple task - using direct routing")
        return False
    
    async def _use_magentic_orchestration(self, user_input: str) -> RoutingDecision:
        """Use full Magentic orchestration for complex requests.
        
        Args:
            user_input: The user's request
            
        Returns:
            RoutingDecision object
        """
        # Note: This method is only called for non-email requests
        # Email requests are blocked in _should_use_magentic_orchestration()
        # to prevent orchestration loops
        
        return RoutingDecision(
            agents_to_call=["magentic_orchestration"],
            reasoning="Complex task suitable for Magentic multi-agent orchestration",
            is_multi_agent=True,
            primary_agent="magentic_orchestration"
        )
    
    async def _use_direct_routing(self, user_input: str) -> RoutingDecision:
        """Use direct routing agent for simpler requests.
        
        Args:
            user_input: The user's request
            
        Returns:
            RoutingDecision object
        """
        # Create a routing prompt for the routing agent
        routing_prompt = f"""Analyze this user request and determine which agents should handle it:

User request: "{user_input}"

Available agents:
- weather_agent: Weather conditions, forecasts, temperature, climate
- ai_ethics_agent: AI ethics, bias, human-AI dependency, AI governance
- qna_agent: Customer support, technical help, product information
- support_email_agent: Professional email formatting (use with other agents for content + formatting)
- orchestrator_direct: Casual conversation, greetings, general knowledge

**Email Formatting Logic:**
- If request needs EMAIL FORMAT (has email indicators like "Subject:", "Dear", formal language), use TWO agents:
  1. Content agent (weather_agent, ai_ethics_agent, qna_agent, or orchestrator_direct) 
  2. support_email_agent for professional formatting
- This creates is_multi_agent: true workflows where content is retrieved first, then formatted as email

**Single Agent Logic:**
- Use single agents for regular requests that don't need email formatting

Return a JSON object with exactly this format:
{{
    "agents_to_call": ["agent_name"] or ["content_agent", "support_email_agent"],
    "reasoning": "Brief explanation of why these agents were chosen",
    "is_multi_agent": false or true,
    "primary_agent": "primary_agent_name"
}}

Examples:
- "What's the weather in Paris?" → {{"agents_to_call": ["weather_agent"], "reasoning": "Weather query", "is_multi_agent": false, "primary_agent": "weather_agent"}}
- "Subject: Weather Request\nDear Support,\nWhat's the weather in Paris?" → {{"agents_to_call": ["weather_agent", "support_email_agent"], "reasoning": "Weather query requiring email format", "is_multi_agent": true, "primary_agent": "weather_agent"}}
- AI ethics topics → {{"agents_to_call": ["ai_ethics_agent"], "reasoning": "AI ethics topic", "is_multi_agent": false, "primary_agent": "ai_ethics_agent"}}
- Casual chat → {{"agents_to_call": ["orchestrator_direct"], "reasoning": "Casual conversation", "is_multi_agent": false, "primary_agent": "orchestrator_direct"}}

Always respond with valid JSON only."""

        # Create a thread for the routing request
        routing_thread = ChatHistory()
        routing_thread.add_user_message(routing_prompt)
        
        # Use the routing agent for intelligent routing
        routing_responses = []
        async for response in self.routing_agent.invoke(routing_thread):
            routing_responses.append(str(response))
        
        routing_result = "".join(routing_responses)
        return self._parse_routing_decision(routing_result, user_input)
    
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
    
    async def _delegate_to_support_email(self, content: str, customer_info: Optional[Dict[str, Any]] = None, thread: Optional[ChatHistory] = None) -> str:
        """Delegate content to the Support Email Formatting agent for professional email formatting.
        
        Args:
            content: The content to format (typically question + answer from other agents)
            customer_info: Optional customer information (name, email, subject)
            thread: Optional thread for conversation context (not used in formatting)
            
        Returns:
            The Support Email agent's professionally formatted response
        """
        logger.info(f"🔄 Delegating to Support Email Formatting Agent for email formatting...")
        start_time = time.time()
        
        try:
            response = await self.support_email_agent.format_email_response(content, customer_info)
            response_time = time.time() - start_time
            logger.info(f"✅ Email formatting completed in {response_time:.2f}s")
            return response
        except Exception as e:
            logger.error(f"❌ Email formatting failed: {e}")
            raise
    
    async def handle_request(self, user_input: str, thread: Optional[ChatHistory] = None) -> str:
        """Handle a user request using Magentic orchestration for intelligent multi-agent coordination.
        
        Args:
            user_input: The user's input/request
            thread: Optional chat thread for conversation history
            
        Returns:
            str: The orchestrated response
        """
        logger.info(f"🎯 ORCHESTRATOR: Handling request with Magentic workflow: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
        start_time = time.time()
        
        if thread is None:
            thread = ChatHistory()
            logger.info("📝 Created new chat history thread")
        else:
            history_count = len([msg for msg in thread.messages])
            logger.info(f"📚 Using existing thread with {history_count} messages")
        
        try:
            # Step 1: Use Magentic orchestration to intelligently route the request
            logger.info("🧠 Using Magentic orchestration to analyze and route request...")
            routing_start = time.time()
            
            try:
                # Use Magentic orchestration for intelligent routing
                routing_decision = await self._route_with_magentic(user_input)
                
            except Exception as e:
                logger.warning(f"⚠️ Magentic routing failed: {e}, falling back to rule-based routing")
                routing_decision = self._fallback_routing(user_input)
            routing_time = time.time() - routing_start
            logger.info(f"🎯 Magentic routing completed in {routing_time:.2f}s")
            logger.info(f"📋 Routing decision: {routing_decision.agents_to_call}")
            logger.info(f"💭 Reasoning: {routing_decision.reasoning}")
            logger.info(f"🔀 Multi-agent: {routing_decision.is_multi_agent}")
            
            # Step 2: Execute agent calls based on routing decision
            if routing_decision.is_multi_agent and len(routing_decision.agents_to_call) > 1:
                logger.info(f"🚀 Executing multi-agent workflow with {len(routing_decision.agents_to_call)} agents")
                response = await self._execute_multi_agent_workflow(user_input, routing_decision, thread)
            else:
                logger.info(f"🎯 Executing single agent workflow: {routing_decision.agents_to_call[0]}")
                response = await self._execute_single_agent_workflow(user_input, routing_decision.agents_to_call[0], thread)
            
            total_time = time.time() - start_time
            logger.info(f"✅ ORCHESTRATOR: Request completed in {total_time:.2f}s")
            logger.info(f"📤 Final response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            
            return response
                
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ ORCHESTRATOR: Request failed after {error_time:.2f}s: {e}")
            raise

    async def _execute_single_agent_workflow(self, user_input: str, agent_name: str, thread: ChatHistory) -> str:
        """Execute a single agent workflow.
        
        Args:
            user_input: The user's input
            agent_name: Name of the agent to call
            thread: Chat history thread
            
        Returns:
            str: The agent's response
        """
        logger.info(f"🎯 Executing single agent: {agent_name}")
        
        if agent_name == "weather_agent":
            return await self._delegate_to_weather(user_input, thread)
        elif agent_name == "ai_ethics_agent":
            return await self._delegate_to_ai_ethics(user_input, thread)
        elif agent_name == "qna_agent":
            return await self._delegate_to_qna(user_input, thread)
        elif agent_name == "support_email_agent":
            # Email agent should not be called alone - it needs content to format
            logger.warning("⚠️ Email formatting agent called without content, handling directly first")
            content = await self._handle_directly(user_input, thread)
            customer_info = self._extract_customer_info(user_input)
            return await self._delegate_to_support_email(f"Question: {user_input}\n\nAnswer: {content}", customer_info, thread)
        elif agent_name == "orchestrator_direct":
            return await self._handle_directly(user_input, thread)
        elif agent_name == "magentic_orchestration":
            return await self._execute_magentic_orchestration(user_input, thread)
        else:
            logger.error(f"❌ Unknown agent: {agent_name}")
            return await self._handle_directly(user_input, thread)

    async def _execute_multi_agent_workflow(self, user_input: str, routing_decision: RoutingDecision, thread: ChatHistory) -> str:
        """Execute a multi-agent workflow with proper sequencing for email formatting.
        
        Args:
            user_input: The user's input
            routing_decision: The routing decision from Magentic
            thread: Chat history thread
            
        Returns:
            str: The final response (formatted as email if email agent is involved)
        """
        logger.info(f"🚀 Executing multi-agent workflow with {len(routing_decision.agents_to_call)} agents")
        multi_start = time.time()
        
        # Check if email formatting is involved
        needs_email_formatting = "support_email_agent" in routing_decision.agents_to_call
        has_magentic_orchestration = "magentic_orchestration" in routing_decision.agents_to_call
        
        # Note: Magentic + Email workflow should never happen because email requests
        # are blocked from using Magentic orchestration in _should_use_magentic_orchestration()
        
        if needs_email_formatting and has_magentic_orchestration:
            logger.error("� UNEXPECTED: Magentic + Email workflow detected - this should be prevented!")
            logger.error("🚨 Email requests should be blocked from Magentic orchestration")
            logger.error("🚨 Falling back to direct routing with email formatting")
            
            # Fallback: use direct routing with email formatting
            fallback_content = await self._handle_directly(user_input, thread)
            customer_info = self._extract_customer_info(user_input)
            return await self._delegate_to_support_email(f"Question: {user_input}\n\nAnswer: {fallback_content}", customer_info, thread)
        
        elif needs_email_formatting:
            logger.info("📧 Email formatting workflow: First get content, then format as email")
            # Standard email workflow (content agents + email formatting)
            content_agents = [agent for agent in routing_decision.agents_to_call if agent != "support_email_agent"]
            return await self._execute_content_then_email_workflow(user_input, content_agents, thread)
        
        else:
            # Standard multi-agent workflow without email formatting
            logger.info("🔄 Standard multi-agent workflow (no email formatting)")
            return await self._execute_standard_multi_agent_workflow(user_input, routing_decision, thread)

    async def _execute_content_then_email_workflow(self, user_input: str, content_agents: List[str], thread: ChatHistory) -> str:
        """Execute workflow where content agents run first, then email formatting is applied.
        
        Args:
            user_input: The user's input
            content_agents: List of content agent names
            thread: Chat history thread
            
        Returns:
            str: Email-formatted response
        """
        # Step 1: Get content from knowledge agents
        logger.info(f"📚 Step 1: Getting content from {len(content_agents)} knowledge agents")
        content_tasks = []
        for agent_name in content_agents:
            if agent_name == "weather_agent":
                content_tasks.append(self._call_agent_with_metrics("weather_agent", self._delegate_to_weather(user_input, thread)))
            elif agent_name == "ai_ethics_agent":
                content_tasks.append(self._call_agent_with_metrics("ai_ethics_agent", self._delegate_to_ai_ethics(user_input, thread)))
            elif agent_name == "qna_agent":
                content_tasks.append(self._call_agent_with_metrics("qna_agent", self._delegate_to_qna(user_input, thread)))
            elif agent_name == "orchestrator_direct":
                content_tasks.append(self._call_agent_with_metrics("orchestrator_direct", self._handle_directly(user_input, thread)))
        
        # Execute content agents in parallel
        content_responses = await asyncio.gather(*content_tasks, return_exceptions=True)
        
        # Process content responses
        successful_content = []
        for response in content_responses:
            if isinstance(response, AgentResponse) and response.success:
                successful_content.append(response)
                logger.info(f"✅ {response.agent_name} provided content in {response.execution_time:.2f}s")
        
        if not successful_content:
            logger.error("❌ No content agents succeeded, falling back to direct handling")
            fallback_content = await self._handle_directly(user_input, thread)
            customer_info = self._extract_customer_info(user_input)
            return await self._delegate_to_support_email(f"Question: {user_input}\n\nAnswer: {fallback_content}", customer_info, thread)
        
        # Step 2: Combine content and prepare for email formatting
        if len(successful_content) == 1:
            combined_content = f"Question: {user_input}\n\nAnswer: {successful_content[0].response}"
        else:
            # Multiple content sources - create comprehensive response
            content_parts = [f"Question: {user_input}\n\nComprehensive Answer:"]
            for i, response in enumerate(successful_content, 1):
                agent_name_clean = response.agent_name.replace("_", " ").title()
                content_parts.append(f"\n**From {agent_name_clean}:**\n{response.response}")
            combined_content = "\n".join(content_parts)
        
        # Step 3: Extract customer info and format as email
        customer_info = self._extract_customer_info(user_input)
        
        logger.info("📧 Step 2: Formatting content as professional email")
        email_start = time.time()
        
        try:
            email_response = await self._delegate_to_support_email(combined_content, customer_info, thread)
            email_time = time.time() - email_start
            logger.info(f"✅ Email formatting completed in {email_time:.2f}s")
            return email_response
            
        except Exception as e:
            logger.error(f"❌ Email formatting failed: {e}, returning content without formatting")
            return combined_content

    async def _execute_standard_multi_agent_workflow(self, user_input: str, routing_decision: RoutingDecision, thread: ChatHistory) -> str:
        """Execute standard multi-agent workflow with parallel calls and response synthesis.
        
        Args:
            user_input: The user's input
            routing_decision: The routing decision
            thread: Chat history thread
            
        Returns:
            str: The synthesized response from multiple agents
        """
        # Create tasks for parallel execution
        tasks = []
        for agent_name in routing_decision.agents_to_call:
            if agent_name == "weather_agent":
                tasks.append(self._call_agent_with_metrics("weather_agent", self._delegate_to_weather(user_input, thread)))
            elif agent_name == "ai_ethics_agent":
                tasks.append(self._call_agent_with_metrics("ai_ethics_agent", self._delegate_to_ai_ethics(user_input, thread)))
            elif agent_name == "qna_agent":
                tasks.append(self._call_agent_with_metrics("qna_agent", self._delegate_to_qna(user_input, thread)))
            elif agent_name == "orchestrator_direct":
                tasks.append(self._call_agent_with_metrics("orchestrator_direct", self._handle_directly(user_input, thread)))
        
        # Execute all agent calls in parallel
        logger.info(f"⚡ Executing {len(tasks)} agent calls in parallel...")
        parallel_start = time.time()
        
        agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        parallel_time = time.time() - parallel_start
        logger.info(f"⚡ Parallel execution completed in {parallel_time:.2f}s")
        
        # Process results and handle any errors
        successful_responses = []
        failed_responses = []
        
        for response in agent_responses:
            if isinstance(response, Exception):
                logger.error(f"❌ Agent call failed: {response}")
                failed_responses.append(str(response))
            elif isinstance(response, AgentResponse):
                if response.success:
                    successful_responses.append(response)
                    logger.info(f"✅ {response.agent_name} completed in {response.execution_time:.2f}s")
                else:
                    logger.error(f"❌ {response.agent_name} failed: {response.error}")
                    failed_responses.append(f"{response.agent_name}: {response.error}")
        
        if not successful_responses:
            logger.error("❌ All agent calls failed, falling back to direct handling")
            return await self._handle_directly(user_input, thread)
        
        # Synthesize responses
        return await self._synthesize_agent_responses(user_input, successful_responses, failed_responses)

    def _extract_customer_info(self, user_input: str) -> Dict[str, Any]:
        """Extract customer information from user input for email formatting.
        
        Args:
            user_input: The user's input
            
        Returns:
            Dict containing customer information
        """
        import re
        
        customer_info = {
            'customer_name': 'Valued Customer',
            'subject': 'Support Request',
            'sender_email': None
        }
        
        lines = user_input.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            
            # Extract subject
            if line_lower.startswith('subject:'):
                customer_info["subject"] = line.split(':', 1)[1].strip()
            
            # Extract sender email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            if email_match and not customer_info["sender_email"]:
                customer_info["sender_email"] = email_match.group()
            
            # Extract customer name (simple heuristic)
            if any(greeting in line_lower for greeting in ["dear", "hello", "hi"]):
                words = line.split()
                if len(words) > 1:
                    customer_info["customer_name"] = words[-1].rstrip(',').strip()
        
        return customer_info

    async def _synthesize_agent_responses(self, user_input: str, successful_responses: List[AgentResponse], failed_responses: List[str]) -> str:
        """Synthesize responses from multiple agents.
        
        Args:
            user_input: Original user input
            successful_responses: List of successful agent responses
            failed_responses: List of failed response descriptions
            
        Returns:
            str: Synthesized response
        """
        logger.info("🧠 Synthesizing agent responses...")
        synthesis_start = time.time()
        
        # Format agent responses for synthesis
        formatted_responses = []
        for response in successful_responses:
            formatted_responses.append(f"**{response.agent_name}**: {response.response}")
        
        agent_responses_text = "\n\n".join(formatted_responses)
        
        if failed_responses:
            agent_responses_text += f"\n\n**Failed agents**: {'; '.join(failed_responses)}"
        
        # Use the orchestrator agent to synthesize responses
        try:
            synthesis_prompt = f"""Synthesize these agent responses into a coherent, helpful answer:

Original request: "{user_input}"

Agent responses:
{agent_responses_text}

Create a single, well-structured response that:
1. Addresses all aspects of the user's request
2. Flows naturally without feeling like separate responses
3. Maintains the expertise and tone from each agent
4. Provides clear organization if covering multiple topics

Return only the final synthesized response."""

            synthesis_thread = ChatHistory()
            synthesis_thread.add_user_message(synthesis_prompt)
            
            synthesis_responses = []
            async for response in self.agent.invoke(synthesis_thread):
                synthesis_responses.append(str(response))
            
            synthesized_response = "".join(synthesis_responses)
            
        except Exception as e:
            logger.warning(f"⚠️ Response synthesis failed: {e}, using simple concatenation")
            synthesized_response = self._simple_synthesis(user_input, successful_responses)
        
        synthesis_time = time.time() - synthesis_start
        logger.info(f"🧠 Response synthesis completed in {synthesis_time:.2f}s")
        
        return synthesized_response

    async def _call_agent_with_metrics(self, agent_name: str, agent_call) -> AgentResponse:
        """Wrap agent calls with metrics and error handling.
        
        Args:
            agent_name: Name of the agent
            agent_call: The async agent call
            
        Returns:
            AgentResponse: Response with metrics and error handling
        """
        start_time = time.time()
        try:
            response = await agent_call
            execution_time = time.time() - start_time
            return AgentResponse(
                agent_name=agent_name,
                response=response,
                execution_time=execution_time,
                success=True
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return AgentResponse(
                agent_name=agent_name,
                response="",
                execution_time=execution_time,
                success=False,
                error=str(e)
            )

    async def _handle_directly(self, user_input: str, thread: ChatHistory) -> str:
        """Handle request directly with the orchestrator agent.
        
        Args:
            user_input: The user's input
            thread: Chat history thread
            
        Returns:
            str: The orchestrator's direct response
        """
        logger.info("🎯 Handling directly with orchestrator agent")
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
        logger.info(f"✅ Direct handling completed in {invoke_time:.2f}s")
        
        return result
    
    async def invoke(self, user_input: str, thread: Optional[ChatHistory] = None) -> str:
        """Public interface to invoke the orchestrator agent.
        
        Args:
            user_input: The user's input/request
            thread: Optional chat thread for conversation history
            
        Returns:
            str: The orchestrated response
        """
        return await self.handle_request(user_input, thread)
    
    def _parse_routing_decision(self, routing_result: str, user_input: str) -> RoutingDecision:
        """Parse the routing decision from the agent's JSON response.
        
        Args:
            routing_result: JSON string from the routing agent
            user_input: Original user input for fallback
            
        Returns:
            RoutingDecision object
        """
        try:
            # Clean up the response to extract JSON
            routing_result = routing_result.strip()
            
            # Find JSON object in the response
            start_idx = routing_result.find('{')
            end_idx = routing_result.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = routing_result[start_idx:end_idx + 1]
                routing_data = json.loads(json_str)
                
                return RoutingDecision(
                    agents_to_call=routing_data.get("agents_to_call", ["orchestrator_direct"]),
                    reasoning=routing_data.get("reasoning", "Default routing"),
                    is_multi_agent=routing_data.get("is_multi_agent", False),
                    primary_agent=routing_data.get("primary_agent")
                )
            else:
                logger.warning("⚠️ No valid JSON found in routing response, using fallback")
                return self._fallback_routing(user_input)
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"⚠️ Failed to parse routing decision: {e}, using fallback")
            return self._fallback_routing(user_input)
    
    def _fallback_routing(self, user_input: str) -> RoutingDecision:
        """Fallback routing logic using simple keyword matching.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            RoutingDecision object
        """
        user_input_lower = user_input.lower()
        
        # Check for email format requests (these need special handling)
        email_indicators = ['email', 'formal', 'professional', 'subject:', 'dear ', 'best regards', '@']
        is_email_request = any(indicator in user_input_lower for indicator in email_indicators)
        
        # Simple keyword-based routing
        if any(word in user_input_lower for word in ['weather', 'temperature', 'forecast', 'rain', 'snow', 'sunny', 'cloudy']):
            if is_email_request:
                return RoutingDecision(
                    agents_to_call=["weather_agent", "support_email_agent"],
                    reasoning="Weather question requiring email format",
                    is_multi_agent=True,
                    primary_agent="weather_agent"
                )
            else:
                return RoutingDecision(
                    agents_to_call=["weather_agent"],
                    reasoning="Weather-related keywords detected",
                    is_multi_agent=False,
                    primary_agent="weather_agent"
                )
        elif any(word in user_input_lower for word in ['ai ethics', 'bias', 'fairness', 'human dependence', 'algorithmic']):
            if is_email_request:
                return RoutingDecision(
                    agents_to_call=["ai_ethics_agent", "support_email_agent"],
                    reasoning="AI ethics question requiring email format",
                    is_multi_agent=True,
                    primary_agent="ai_ethics_agent"
                )
            else:
                return RoutingDecision(
                    agents_to_call=["ai_ethics_agent"],
                    reasoning="AI ethics keywords detected",
                    is_multi_agent=False,
                    primary_agent="ai_ethics_agent"
                )
        elif any(word in user_input_lower for word in ['support', 'help', 'problem', 'issue', 'error', 'question']):
            if is_email_request:
                return RoutingDecision(
                    agents_to_call=["qna_agent", "support_email_agent"],
                    reasoning="Support question requiring email format",
                    is_multi_agent=True,
                    primary_agent="qna_agent"
                )
            else:
                return RoutingDecision(
                    agents_to_call=["qna_agent"],
                    reasoning="Support-related keywords detected",
                    is_multi_agent=False,
                    primary_agent="qna_agent"
                )
        elif is_email_request:
            return RoutingDecision(
                agents_to_call=["orchestrator_direct", "support_email_agent"],
                reasoning="Email format request for general inquiry",
                is_multi_agent=True,
                primary_agent="orchestrator_direct"
            )
        else:
            return RoutingDecision(
                agents_to_call=["orchestrator_direct"],
                reasoning="No specific agent keywords found, handling directly",
                is_multi_agent=False,
                primary_agent="orchestrator_direct"
            )
    
    def _simple_synthesis(self, user_input: str, successful_responses: List[AgentResponse]) -> str:
        """Simple response synthesis when Magentic synthesis fails.
        
        Args:
            user_input: Original user input
            successful_responses: List of successful agent responses
            
        Returns:
            str: Concatenated response
        """
        if len(successful_responses) == 1:
            return successful_responses[0].response
        
        # Multiple responses - create a simple synthesis
        synthesis_parts = [f"Based on your request about '{user_input}', here's what I found:\n"]
        
        for i, response in enumerate(successful_responses, 1):
            agent_name_clean = response.agent_name.replace("_", " ").title()
            synthesis_parts.append(f"\n**{agent_name_clean}:**\n{response.response}")
            
            if i < len(successful_responses):
                synthesis_parts.append("\n" + "="*50)
        
        return "".join(synthesis_parts)

    def get_available_agents(self) -> list:
        """Get list of available agent capabilities.
        
        Returns:
            list: List of agent descriptions
        """
        return [
            {
                "name": "QnA Agent",
                "description": "Handles customer support questions, product information, and technical help",
                "keywords": ["support", "help", "question", "problem", "issue"]
            },
            {
                "name": "AI Ethics Agent", 
                "description": "Provides insights on AI ethics, bias, human-AI dependency, and AI governance",
                "keywords": ["ai ethics", "bias", "fairness", "human dependence", "algorithmic"]
            },
            {
                "name": "Weather Agent",
                "description": "Provides weather information, forecasts, and climate data for any location",
                "keywords": ["weather", "temperature", "forecast", "climate"]
            },
            {
                "name": "Support Email Agent",
                "description": "Creates professional email responses for support requests",
                "keywords": ["email", "formal", "professional", "request"]
            },
            {
                "name": "Orchestrator (Direct)",
                "description": "Handles casual conversation, general knowledge, and creative requests",
                "keywords": ["chat", "conversation", "general", "creative"]
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
    
    def _create_magentic_members(self) -> List[ChatCompletionAgent]:
        """Create the member agents for Magentic orchestration.
        
        Returns:
            List[ChatCompletionAgent]: List of agents for Magentic orchestration
        
        Note:
            Email formatting agent is intentionally NOT included here to prevent loops.
            Email formatting should only happen as the final step via direct routing.
            This ensures Magentic orchestration never processes email-formatted content.
        """
        # Create specialized agents for Magentic orchestration
        # IMPORTANT: Email formatting agent is NOT included here as it's for formatting only,
        # not for knowledge retrieval or content generation. Magentic should NEVER handle email formatting.
        
        weather_magentic_agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="WeatherSpecialist",
            description="A weather specialist that provides weather information, forecasts, and climate data for any location.",
            instructions="""You are a weather specialist agent. Your role is to provide accurate, up-to-date weather information including:
- Current weather conditions
- Weather forecasts
- Temperature data
- Climate information
- Weather-related advice

Always provide specific, actionable weather information. If location is not specified, ask for clarification.

IMPORTANT: You provide content only. You do NOT format emails or create professional correspondence. 
Your responses should be informative content that can be used directly or formatted later by other systems."""
        )
        
        ai_ethics_magentic_agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="AIEthicsSpecialist", 
            description="An AI ethics specialist that provides insights on AI ethics, bias, human-AI dependency, and AI governance.",
            instructions="""You are an AI ethics specialist. Your role is to provide insights on:
- AI ethics and moral implications
- AI bias and fairness issues
- Human-AI dependency concerns
- AI governance and regulation
- Algorithmic accountability
- Responsible AI development

Provide balanced, thoughtful analysis of AI ethical considerations with practical recommendations.

IMPORTANT: You provide content only. You do NOT format emails or create professional correspondence. 
Your responses should be informative content that can be used directly or formatted later by other systems."""
        )
        
        support_knowledge_agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="SupportKnowledgeSpecialist",
            description="A customer support knowledge specialist that provides technical information, troubleshooting, and product guidance.",
            instructions="""You are a customer support knowledge specialist. Your role is to provide:
- Technical help and troubleshooting guidance
- Product information and feature explanations
- How-to instructions and step-by-step guides
- Problem resolution strategies
- Best practices and recommendations

Focus on providing accurate, helpful knowledge content. Be clear, detailed, and solution-oriented.

IMPORTANT: You provide content only. You do NOT format emails or create professional correspondence. 
Your responses should be informative content that can be used directly or formatted later by other systems."""
        )
        
        return [weather_magentic_agent, ai_ethics_magentic_agent, support_knowledge_agent]
    
    def _agent_response_callback(self, message) -> None:
        """Callback function to observe agent responses in Magentic orchestration.
        
        Args:
            message: The message from an agent in the orchestration
        """
        # Log the agent response for monitoring
        logger.info(f"🤖 Magentic Agent Response - {message.name}: {str(message.content)[:100]}{'...' if len(str(message.content)) > 100 else ''}")
        
        # IMPORTANT: Do not process this message further. 
        # This is just for monitoring, not for triggering additional actions.
        # The Magentic orchestration will handle the coordination internally.

    async def _execute_magentic_orchestration(self, user_input: str, thread: ChatHistory) -> str:
        """Execute Magentic orchestration for complex multi-agent tasks.
        
        Args:
            user_input: The user's input
            thread: Chat history thread
            
        Returns:
            str: The orchestrated response from Magentic
        """
        logger.info("🧠 Executing Magentic orchestration for complex task")
        magentic_start = time.time()
        
        try:
            # Create and start runtime
            runtime = InProcessRuntime()
            runtime.start()
            
            # Invoke Magentic orchestration
            logger.info(f"🚀 Invoking Magentic orchestration with task: '{user_input[:100]}{'...' if len(user_input) > 100 else ''}'")
            orchestration_result = await self.magentic_orchestration.invoke(
                task=user_input,
                runtime=runtime
            )
            
            # Wait for results
            result = await orchestration_result.get()
            
            # Stop runtime
            await runtime.stop_when_idle()
            
            magentic_time = time.time() - magentic_start
            logger.info(f"✅ Magentic orchestration completed in {magentic_time:.2f}s")
            
            # Convert result to string and return directly
            # IMPORTANT: Magentic orchestration should NEVER include email formatting
            # The result should be treated as final content, not processed further
            final_result = str(result)
            logger.info(f"📤 Magentic final result: '{final_result[:100]}{'...' if len(final_result) > 100 else ''}'")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Magentic orchestration failed: {e}")
            # Fallback to direct handling
            logger.info("🔄 Falling back to direct handling")
            return await self._handle_directly(user_input, thread)
        finally:
            # Ensure runtime is stopped even if there's an error
            try:
                if 'runtime' in locals():
                    await runtime.stop_when_idle()
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Runtime cleanup warning: {cleanup_error}")


