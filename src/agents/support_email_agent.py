"""
Support Email Agent - A specialized agent for handling support request emails with proper email formatting.
"""

import os
import logging
import time
import re
from typing import Optional, Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from agents.qna_agent import QnAAgent

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SupportEmailAgent:
    """A specialized agent for handling support request emails with proper email formatting."""
    
    def __init__(self):
        """Initialize the Support Email agent with QnA agent integration."""
        logger.info("📧 Initializing Support Email Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ Support Email Kernel created successfully")
            
            self.agent = self._create_agent()
            logger.info("✅ Support Email Agent created successfully")
            
            # Initialize QnA agent for knowledge retrieval
            self.qna_agent = QnAAgent()
            logger.info("✅ QnA Agent integration initialized")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 Support Email Agent fully initialized in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Support Email Agent: {e}")
            raise
    
    def _create_kernel(self) -> Kernel:
        """Create and configure the semantic kernel."""
        logger.info("🔧 Creating Support Email Kernel...")
        kernel = Kernel()
        
        # Azure AI Foundry configuration from .env
        endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        logger.info(f"📍 Support Email Endpoint: {endpoint}")
        logger.info(f"🤖 Support Email Deployment: {deployment_name}")
        logger.info(f"🔐 Support Email API Key: {'***SET***' if api_key else 'NOT SET'}")
        
        if not endpoint:
            raise ValueError("AZURE_AI_FOUNDRY_ENDPOINT environment variable is required")
        
        if not deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable is required")
        
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
        try:
            chat_completion = AzureChatCompletion(
                endpoint=endpoint,
                deployment_name=deployment_name,
                api_key=api_key
            )
        except Exception as e:
            logger.error(f"❌ Support Email Authentication failed: {e}")
            raise ValueError(f"Failed to authenticate with Azure: {e}. Please ensure AZURE_OPENAI_API_KEY is set correctly.")
        
        kernel.add_service(chat_completion)
        logger.info("✅ Support Email Azure OpenAI service added to kernel")
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent with email formatting instructions."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="Support_Email_Agent",
            instructions="""You are a professional Customer Support Email Specialist. Your role is to:

1. **Email Formatting Expert**: Format responses as professional support emails with proper structure
2. **Professional Tone**: Maintain a friendly, helpful, and professional email tone
3. **Email Structure**: Use proper email formatting including:
   - Professional greeting
   - Clear subject line suggestions when needed
   - Well-structured body with paragraphs
   - Professional closing
   - Signature line placeholder

4. **Support Integration**: Use knowledge base information to provide accurate answers
5. **Email Best Practices**:
   - Use clear, concise language
   - Include actionable steps when applicable
   - Acknowledge the customer's issue/concern
   - Provide next steps or follow-up information
   - Include relevant case/ticket references when needed

6. **Response Guidelines**:
   - Always start with a professional greeting
   - Acknowledge the customer's inquiry
   - Provide the requested information clearly
   - Offer additional help
   - End with a professional closing

7. **Required Signature**: Always end your email responses with this exact signature:

Best regards,  
Thomas von Mentlen
Customer Support Team  
Nakamo
tvm@nakamo.io

Format your responses as complete email replies that can be sent directly to customers."""
        )
    
    def is_email_format(self, message: str) -> bool:
        """Check if the message appears to be in email format."""
        email_indicators = [
            r"subject\s*:",
            r"dear\s+\w+",
            r"hello\s+\w+",
            r"hi\s+\w+",
            r"to\s*:",
            r"from\s*:",
            r"@\w+\.\w+",  # email address
            r"best\s+regards",
            r"sincerely",
            r"thank\s+you\s+for\s+contacting",
            r"we\s+received\s+your\s+email",
        ]
        
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in email_indicators)
    
    def extract_email_info(self, email_content: str) -> Dict[str, Any]:
        """Extract relevant information from email content."""
        info = {
            "subject": None,
            "customer_name": None,
            "main_question": None,
            "sender_email": None
        }
        
        lines = email_content.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            
            # Extract subject
            if line_lower.startswith('subject:'):
                info["subject"] = line.split(':', 1)[1].strip()
            
            # Extract sender email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            if email_match and not info["sender_email"]:
                info["sender_email"] = email_match.group()
            
            # Extract customer name (simple heuristic)
            if any(greeting in line_lower for greeting in ["dear", "hello", "hi"]):
                words = line.split()
                if len(words) > 1:
                    info["customer_name"] = words[-1].rstrip(',').strip()
        
        # Extract main content as the question
        content_lines = [line for line in lines if line.strip() and 
                        not any(line.lower().strip().startswith(prefix) for prefix in 
                               ['subject:', 'from:', 'to:', 'dear', 'hello', 'hi', 'best regards', 'sincerely'])]
        
        if content_lines:
            info["main_question"] = ' '.join(content_lines).strip()
        
        return info
    
    async def get_support_answer(self, question: str) -> str:
        """Get answer from QnA agent for the support question."""
        try:
            logger.info(f"📋 Getting support answer for: {question[:100]}...")
            answer = await self.qna_agent.invoke(question)
            logger.info("✅ Support answer retrieved successfully")
            return answer
        except Exception as e:
            logger.error(f"❌ Error getting support answer: {e}")
            return "I apologize, but I'm currently unable to access our knowledge base. Please contact our support team directly for assistance."
    
    async def invoke(self, user_message: str, chat_history: Optional[ChatHistory] = None) -> str:
        """Main method to invoke the support email agent.
        
        Args:
            user_message: The user's message (potentially in email format)
            chat_history: Optional chat history
            
        Returns:
            Professionally formatted email response
        """
        try:
            if chat_history is None:
                chat_history = ChatHistory()
            
            logger.info(f"📧 Processing support email request...")
            
            # Check if this is an email format
            if not self.is_email_format(user_message):
                logger.info("📝 Message not in email format, treating as regular support question")
                # For non-email format, still provide email-style response
                support_answer = await self.get_support_answer(user_message)
                
                # Create email-formatted response
                email_prompt = f"""
The customer asked: {user_message}

Our support information: {support_answer}

Please format this as a professional support email response.
"""
            else:
                logger.info("📧 Email format detected, extracting information...")
                email_info = self.extract_email_info(user_message)
                
                # Get answer from QnA agent
                question = email_info.get("main_question", user_message)
                support_answer = await self.get_support_answer(question)
                
                # Create contextualized email response
                email_prompt = f"""
Customer Email Information:
- Subject: {email_info.get('subject', 'Support Request')}
- Customer Name: {email_info.get('customer_name', 'Valued Customer')}
- Email: {email_info.get('sender_email', 'N/A')}
- Question: {question}

Our support information: {support_answer}

Please format this as a professional support email reply, addressing the customer by name when available.
"""
            
            # Add the prompt to chat history
            chat_history.add_user_message(email_prompt)
            
            # Invoke the agent and collect response
            response_content = ""
            async for response in self.agent.invoke(chat_history):
                if hasattr(response, 'content'):
                    response_content += str(response.content)
                else:
                    response_content += str(response)
            
            # Add agent response to chat history
            chat_history.add_assistant_message(response_content)
            
            logger.info("✅ Support email response generated successfully")
            return response_content
            
        except Exception as e:
            logger.error(f"❌ Error processing support email request: {e}")
            return f"""
Dear Valued Customer,

Thank you for contacting our support team.

I apologize, but I'm currently experiencing technical difficulties and unable to process your request at this time. Please contact our support team directly, and we'll be happy to assist you promptly.

Best regards,
Customer Support Team

---
If this issue persists, please contact support@company.com
"""


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_support_email_agent():
        """Test the Support Email Agent with sample emails."""
        try:
            agent = SupportEmailAgent()
            
            # Test email format
            sample_email = """
Subject: Account Login Issues

Dear Support Team,

I'm having trouble logging into my account. I keep getting an error message that says "Invalid credentials" even though I'm sure my password is correct. Can you please help me resolve this?

Best regards,
John Smith
john.smith@email.com
"""
            
            print("Testing Support Email Agent...")
            print("=" * 50)
            
            response = await agent.invoke(sample_email)
            print("Email Response:")
            print(response)
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run the test
    asyncio.run(test_support_email_agent())
