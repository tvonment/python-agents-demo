"""
AI Ethics Agent - An AI assistant specialized in AI ethics and human-AI dependency topics.
Uses Azure Document Intelligence to analyze ethical papers and provide insights.
"""

import os
import logging
import time
from typing import Optional, List, Tuple, Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from support.ai_ethics_db import AIEthicsDB, AIEthicsDocument

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AIEthicsAgent:
    """An AI Ethics agent that answers questions about AI ethics and human-AI dependency using processed documents."""
    
    def __init__(self):
        """Initialize the AI Ethics agent with document database."""
        logger.info("🚀 Initializing AI Ethics Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ AI Ethics Kernel created successfully")
            
            self.agent = self._create_agent()
            logger.info("✅ AI Ethics Agent created successfully")
            
            # Initialize AI ethics document database
            logger.info("📚 Initializing AI Ethics Document Database...")
            self.ethics_db = AIEthicsDB()
            logger.info("✅ AI Ethics Document Database initialized")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 AI Ethics Agent fully initialized in {init_time:.2f}s (documents will process async)")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Ethics Agent: {e}")
            raise
    
    def _create_kernel(self) -> Kernel:
        """Create and configure the semantic kernel."""
        logger.info("🔧 Creating AI Ethics Kernel...")
        kernel = Kernel()
        
        # Azure AI Foundry configuration from .env
        endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        logger.info(f"📍 AI Ethics Endpoint: {endpoint}")
        logger.info(f"🤖 AI Ethics Deployment: {deployment_name}")
        logger.info(f"🔐 AI Ethics API Key: {'***SET***' if api_key else 'NOT SET'}")
        
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
            logger.error(f"❌ AI Ethics Authentication failed: {e}")
            raise ValueError(f"Failed to authenticate with Azure: {e}. Please ensure AZURE_OPENAI_API_KEY is set correctly.")
        
        kernel.add_service(chat_completion)
        logger.info("✅ AI Ethics Azure OpenAI service added to kernel")
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent with AI ethics system prompt."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="AI_Ethics_Scholar_Agent",
            instructions="""You are an AI Ethics Scholar - a specialized AI assistant with deep expertise in artificial intelligence ethics, particularly focusing on human-AI dependency and related societal implications.

**Your Primary Role:**
- Analyze and discuss AI ethics topics using the provided academic documents and papers
- Provide thoughtful insights on human-AI dependency, AI's impact on society, and ethical considerations
- Help users understand complex ethical frameworks and philosophical arguments about AI

**Your Knowledge Base:**
- You have access to academic papers and documents about AI ethics, particularly focusing on human dependence on AI
- Use the provided document context to give well-informed, academically grounded responses
- Reference specific sections, studies, or arguments from the documents when relevant

**Your Expertise Areas:**
1. **Human-AI Dependency**: Discuss the psychological, social, and practical aspects of human reliance on AI systems
2. **AI Ethics Frameworks**: Explain various ethical theories and how they apply to AI development and deployment
3. **Societal Impact**: Analyze how AI affects different aspects of society, including employment, education, healthcare, and social interactions
4. **Risk Assessment**: Identify potential risks and benefits of increasing AI integration in human life
5. **Policy and Governance**: Discuss regulatory approaches and governance models for AI systems
6. **Philosophical Implications**: Explore deeper questions about consciousness, agency, and what it means to be human in an AI-integrated world

**Your Communication Style:**
- Academic yet accessible - use scholarly language but explain complex concepts clearly
- Evidence-based - always ground your arguments in research and documented evidence
- Balanced perspective - present multiple viewpoints and acknowledge nuances in ethical debates
- Thoughtful analysis - go beyond surface-level responses to provide deep insights
- Citation-aware - when referencing the provided documents, mention specific sections or findings

**Guidelines:**
- If a question is outside your ethics expertise, acknowledge the limitation and suggest consultation with domain experts
- Always consider multiple stakeholder perspectives (users, developers, society, vulnerable populations)
- Be sensitive to cultural and contextual differences in ethical considerations
- Encourage critical thinking rather than providing definitive moral judgments
- When discussing risks, balance them with potential benefits and mitigation strategies

**Response Format:**
- Start with a brief overview of the ethical dimensions of the question
- Provide detailed analysis using document evidence
- Include relevant examples or case studies when appropriate
- Conclude with thought-provoking questions or considerations for further reflection

Remember: Your goal is to foster informed, nuanced discussions about AI ethics while helping users navigate the complex landscape of human-AI relationships in our evolving technological society."""
        )
    
    async def get_relevant_context(self, query: str, max_documents: int = 3) -> str:
        """Get relevant context from the AI ethics documents for a query.
        
        Args:
            query: The user's question or topic
            max_documents: Maximum number of documents to include in context
            
        Returns:
            Formatted context string with relevant document excerpts
        """
        try:
            logger.info(f"🔍 Searching AI ethics documents for: {query}")
            
            # Search for relevant documents
            search_results = await self.ethics_db.search_documents(query, limit=max_documents)
            
            if not search_results:
                logger.warning("⚠️ No relevant documents found in AI ethics database")
                return "No relevant documents found in the AI ethics knowledge base."
            
            # Format context
            context_parts = []
            context_parts.append("=== RELEVANT AI ETHICS DOCUMENT EXCERPTS ===\n")
            
            for i, (document, similarity) in enumerate(search_results, 1):
                context_parts.append(f"**Document {i}: {document.title}**")
                context_parts.append(f"Source: {document.filename}, {document.section}")
                context_parts.append(f"Relevance Score: {similarity:.3f}")
                context_parts.append(f"Content: {document.content}")
                context_parts.append("---\n")
            
            context = "\n".join(context_parts)
            
            logger.info(f"✅ Found {len(search_results)} relevant documents (similarity: {search_results[0][1]:.3f} - {search_results[-1][1]:.3f})")
            return context
            
        except Exception as e:
            logger.error(f"❌ Error getting relevant context: {e}")
            return f"Error retrieving context from AI ethics documents: {e}"
    
    async def answer_question(self, question: str, chat_history: Optional[ChatHistory] = None) -> str:
        """Answer a question about AI ethics using the document knowledge base.
        
        Args:
            question: The user's question
            chat_history: Optional chat history for context
            
        Returns:
            AI-generated response based on the ethics documents
        """
        try:
            logger.info(f"🤔 AI Ethics Agent answering question: {question}")
            
            # Get relevant context from documents
            context = await self.get_relevant_context(question)
            
            # Create enhanced prompt with context
            enhanced_question = f"""Based on the following AI ethics documents and research, please answer this question:

{context}

**User Question:** {question}

Please provide a comprehensive answer that:
1. References specific information from the provided documents
2. Offers scholarly analysis and insights
3. Considers multiple perspectives and implications
4. Suggests areas for further consideration or research

Your response should be academically rigorous yet accessible to someone interested in AI ethics."""
            
            # Create or use provided chat history
            if chat_history is None:
                chat_history = ChatHistory()
            
            # Add the enhanced question to chat history
            chat_history.add_user_message(enhanced_question)
            
            # Get response from the agent (invoke returns an async generator)
            logger.info("🤖 Invoking AI Ethics Agent...")
            responses = []
            response_count = 0
            
            async for response in self.agent.invoke(chat_history):
                response_count += 1
                responses.append(str(response))
                logger.debug(f"📥 Received response chunk #{response_count}: '{str(response)[:50]}{'...' if len(str(response)) > 50 else ''}'")
            
            # Join all response chunks
            if responses:
                answer = "".join(responses)
                chat_history.add_assistant_message(answer)
                logger.info("✅ AI Ethics Agent provided response")
                return answer
            else:
                logger.warning("⚠️ No response received from AI Ethics Agent")
                return "I apologize, but I wasn't able to generate a response. Please try rephrasing your question."
                
        except Exception as e:
            logger.error(f"❌ Error in AI Ethics Agent answer_question: {e}")
            return f"I encountered an error while processing your question about AI ethics: {e}. Please try again."
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Get a summary of available documents in the AI ethics database.
        
        Returns:
            Dictionary with document statistics and information
        """
        try:
            documents = self.ethics_db.get_all_documents()
            
            # Group by filename
            files_info = {}
            for doc in documents:
                if doc.filename not in files_info:
                    files_info[doc.filename] = {
                        'title': doc.title,
                        'chunks': 0,
                        'pages': set()
                    }
                
                files_info[doc.filename]['chunks'] += 1
                if doc.page_number:
                    files_info[doc.filename]['pages'].add(doc.page_number)
            
            # Convert sets to sorted lists for JSON serialization
            for file_info in files_info.values():
                file_info['pages'] = sorted(list(file_info['pages']))
                file_info['page_count'] = len(file_info['pages'])
            
            summary = {
                'total_documents': len(documents),
                'total_files': len(files_info),
                'files': files_info,
                'database_status': 'Ready'
            }
            
            logger.info(f"📊 AI Ethics DB Summary: {summary['total_documents']} chunks from {summary['total_files']} files")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting document summary: {e}")
            return {
                'total_documents': 0,
                'total_files': 0,
                'files': {},
                'database_status': f'Error: {e}'
            }
    
    async def initialize_documents(self):
        """Initialize documents asynchronously. Call this after creating the instance."""
        logger.info("📄 Starting async document initialization...")
        await self.ethics_db.initialize_documents()
        logger.info("✅ AI Ethics Agent documents fully initialized")
