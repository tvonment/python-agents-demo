"""
QnA Agent - A Customer Support Q&A agent using Azure AI Foundry with vector search capabilities.
"""

import os
import logging
import time
from typing import Optional, List, Tuple
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from .customer_support_db import CustomerSupportDB, SupportDocument

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class QnAAgent:
    """A Customer Support Q&A agent that answers user questions using Azure AI Foundry with vector search."""
    
    def __init__(self):
        """Initialize the QnA agent with customer support database."""
        logger.info("🚀 Initializing Customer Support QnA Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ QnA Kernel created successfully")
            
            self.agent = self._create_agent()
            logger.info("✅ QnA Agent created successfully")
            
            # Initialize customer support database
            self.support_db = CustomerSupportDB()
            logger.info("✅ Customer Support Database initialized")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 Customer Support QnA Agent fully initialized in {init_time:.2f}s")
            
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
        
        # Use API key authentication
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
        try:
            logger.info(f"� QnA using API key authentication for {deployment_name}")
            chat_completion = AzureChatCompletion(
                endpoint=endpoint,
                deployment_name=deployment_name,
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"❌ QnA Authentication failed: {e}")
            raise ValueError(f"Failed to authenticate with Azure: {e}. Please ensure AZURE_OPENAI_API_KEY is set correctly.")
        
        kernel.add_service(chat_completion)
        logger.info("✅ QnA Azure OpenAI service added to kernel")
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent with customer support system prompt."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="Customer_Support_QnA_Agent",
            instructions="""You are a helpful Customer Support AI assistant. Your role is to:

1. **Primary Function**: Answer customer support questions using the provided knowledge base
2. **Knowledge Base**: Use the context provided from our customer support documents to give accurate answers
3. **Be Helpful**: Provide clear, step-by-step instructions when needed
4. **Be Professional**: Maintain a friendly and professional tone
5. **Be Honest**: If you don't find relevant information in the knowledge base, admit it and suggest contacting support
6. **Categorize Issues**: Help identify whether questions are about billing, account management, technical issues, or feature usage
7. **Escalation**: For complex issues not covered in the knowledge base, recommend escalation to human support

Guidelines:
- Always check the provided context first before answering
- Cite relevant information from the knowledge base when possible
- Ask for clarification if the question is unclear
- Provide actionable solutions whenever possible
- If multiple solutions exist, provide them in order of difficulty (easy first)
- Include relevant warnings or important notes about security, billing, or data

Remember: You are representing our company's customer support, so be helpful, accurate, and professional."""
        )
    
    async def search_knowledge_base(self, query: str, top_k: int = 3) -> List[Tuple[SupportDocument, float]]:
        """Search the customer support knowledge base for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of tuples (document, similarity_score)
        """
        logger.info(f"📚 Searching knowledge base for: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        try:
            results = await self.support_db.search_documents(query, top_k=top_k)
            logger.info(f"📊 Knowledge base search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"❌ Knowledge base search failed: {e}")
            return []
    
    def _format_context_from_documents(self, documents: List[Tuple[SupportDocument, float]]) -> str:
        """Format the retrieved documents as context for the agent.
        
        Args:
            documents: List of tuples (document, similarity_score)
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        context_parts.append("=== CUSTOMER SUPPORT KNOWLEDGE BASE ===")
        context_parts.append("")
        
        for i, (doc, score) in enumerate(documents, 1):
            context_parts.append(f"Document {i}: {doc.title}")
            context_parts.append(f"Category: {doc.category.title()}")
            context_parts.append(f"Priority: {doc.priority.title()}")
            context_parts.append(f"Tags: {', '.join(doc.tags)}")
            context_parts.append(f"Relevance Score: {score:.3f}")
            context_parts.append("")
            context_parts.append("Content:")
            context_parts.append(doc.content)
            context_parts.append("")
            context_parts.append("-" * 50)
            context_parts.append("")
        
        context_parts.append("=== END KNOWLEDGE BASE ===")
        context_parts.append("")
        context_parts.append("Please use the above information to answer the customer's question. If the knowledge base doesn't contain relevant information, please say so and suggest contacting support directly.")
        
        return "\n".join(context_parts)
    
    async def get_database_stats(self) -> dict:
        """Get statistics about the customer support database.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            doc_count = self.support_db.get_document_count()
            categories = self.support_db.get_categories()
            
            return {
                "total_documents": doc_count,
                "categories": categories,
                "database_status": "connected" if doc_count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {
                "total_documents": 0,
                "categories": [],
                "database_status": "error"
            }
    
    async def populate_sample_data(self):
        """Populate the database with sample customer support data."""
        logger.info("🌱 Populating customer support database with sample data...")
        try:
            await self.support_db.populate_sample_data()
            stats = await self.get_database_stats()
            logger.info(f"✅ Sample data populated. Database now has {stats['total_documents']} documents")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to populate sample data: {e}")
            return False
    async def answer_question(self, question: str, thread: Optional[ChatHistory] = None, use_knowledge_base: bool = True) -> str:
        """Answer a customer support question using the knowledge base and AI.
        
        Args:
            question: The customer's question
            thread: Optional chat thread for conversation history
            use_knowledge_base: Whether to search the knowledge base for context
            
        Returns:
            str: The agent's response
        """
        logger.info(f"❓ CUSTOMER SUPPORT QNA: Answering question: '{question[:100]}{'...' if len(question) > 100 else ''}'")
        start_time = time.time()
        
        try:
            if thread is None:
                thread = ChatHistory()
                logger.info("📝 Created new chat history thread")
            else:
                history_count = len([msg for msg in thread.messages])
                logger.info(f"📚 Using existing thread with {history_count} messages")
            
            # Search knowledge base for relevant context
            context = ""
            if use_knowledge_base:
                logger.info("� Searching knowledge base for relevant information...")
                search_start = time.time()
                
                relevant_docs = await self.search_knowledge_base(question, top_k=3)
                context = self._format_context_from_documents(relevant_docs)
                
                search_time = time.time() - search_start
                logger.info(f"📊 Knowledge base search completed in {search_time:.2f}s")
                
                if relevant_docs:
                    logger.info(f"📄 Found {len(relevant_docs)} relevant documents:")
                    for i, (doc, score) in enumerate(relevant_docs[:3]):
                        logger.info(f"   {i+1}. {doc.title} (score: {score:.3f})")
                else:
                    logger.info("📭 No relevant documents found in knowledge base")
            
            # Prepare the enhanced question with context
            if context and use_knowledge_base:
                enhanced_question = f"{context}\n\nCustomer Question: {question}"
            else:
                enhanced_question = question
            
            logger.info("💭 Adding enhanced question to thread...")
            thread.add_user_message(enhanced_question)
            
            logger.info("🤖 Invoking Customer Support QnA Agent...")
            invoke_start = time.time()
            responses = []
            response_count = 0
            
            async for response in self.agent.invoke(thread):
                response_count += 1
                responses.append(str(response))
                logger.debug(f"📥 Received response chunk #{response_count}: '{str(response)[:50]}{'...' if len(str(response)) > 50 else ''}'")
            
            result = "".join(responses)
            thread.add_assistant_message(result)
            
            invoke_time = time.time() - invoke_start
            total_time = time.time() - start_time
            
            logger.info(f"✅ CUSTOMER SUPPORT QNA: Agent invocation completed in {invoke_time:.2f}s")
            logger.info(f"✅ CUSTOMER SUPPORT QNA: Total question answered in {total_time:.2f}s")
            logger.info(f"📤 Response: '{result[:100]}{'...' if len(result) > 100 else ''}'")
            logger.info(f"📊 Stats: {len(result)} chars, {response_count} response chunks")
            
            return result
            
        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ CUSTOMER SUPPORT QNA: Question failed after {error_time:.2f}s: {e}")
            raise
