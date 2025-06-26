"""
Support Email Formatting Agent - A specialized agent for formatting responses as professional support emails.
This agent focuses ONLY on email formatting and does NOT perform knowledge retrieval to avoid orchestration loops.
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

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SupportEmailAgent:
    """A specialized agent for formatting responses as professional support emails. 
    This agent focuses ONLY on email formatting and does NOT perform knowledge retrieval."""
    
    def __init__(self):
        """Initialize the Support Email Formatting agent."""
        logger.info("📧 Initializing Support Email Formatting Agent...")
        start_time = time.time()
        
        try:
            self.kernel = self._create_kernel()
            logger.info("✅ Support Email Kernel created successfully")
            
            self.agent = self._create_agent()
            logger.info("✅ Support Email Formatting Agent created successfully")
            
            init_time = time.time() - start_time
            logger.info(f"🎉 Support Email Formatting Agent fully initialized in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Support Email Formatting Agent: {e}")
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
            name="Support_Email_Formatter",
            instructions="""You are a Professional Email Formatting Specialist. Your ONLY role is to format given content as professional support emails.

🚨 IMPORTANT: You do NOT retrieve knowledge or answer questions. You ONLY format provided content into proper email structure.

**Your Responsibilities:**
1. **Email Structure Only**: Format provided content into proper email structure
2. **Professional Tone**: Maintain friendly, helpful, professional email tone  
3. **Email Components**:
   - Professional greeting (use customer name if provided)
   - Well-structured body with clear paragraphs
   - Professional closing
   - Required signature (see below)

4. **Email Best Practices**:
   - Clear, concise language
   - Logical paragraph structure
   - Acknowledge customer concerns when mentioned
   - Professional formatting

5. **Required Signature**: Always end emails with this exact signature:

Best regards,  
Thomas von Mentlen
Customer Support Team  
Nakamo
tvm@nakamo.io

**Input Format Expectations:**
You will receive content that may include:
- Customer information (name, email, subject)
- Question/issue description
- Answer/solution content (already provided by other agents)

**Your Task**: Format this into a complete, professional email response ready to send.

**You do NOT:**
- Look up information
- Answer questions yourself
- Make decisions about content
- Call other agents or services

**You DO:**
- Format provided content professionally
- Structure emails properly
- Apply professional tone
- Add required signature"""
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
    
    async def format_email_response(self, content: str, customer_info: Optional[Dict[str, Any]] = None) -> str:
        """Format provided content as a professional support email response.
        
        Args:
            content: The content to format (question + answer provided by orchestration)
            customer_info: Optional customer information (name, email, subject)
            
        Returns:
            Professionally formatted email response
        """
        try:
            logger.info("� Formatting content as professional email response...")
            
            # Create formatting prompt
            customer_name = customer_info.get('customer_name', 'Valued Customer') if customer_info else 'Valued Customer'
            subject = customer_info.get('subject', 'Support Request') if customer_info else 'Support Request'
            
            formatting_prompt = f"""Please format the following content as a professional support email response:

Customer Name: {customer_name}
Subject: {subject}

Content to format:
{content}

Format this as a complete professional email response with:
1. Professional greeting using customer name
2. Well-structured body 
3. Professional closing
4. Required signature

Make it ready to send directly to the customer."""
            
            chat_history = ChatHistory()
            chat_history.add_user_message(formatting_prompt)
            
            # Invoke the agent and collect response
            response_content = ""
            async for response in self.agent.invoke(chat_history):
                if hasattr(response, 'content'):
                    response_content += str(response.content)
                else:
                    response_content += str(response)
            
            logger.info("✅ Email formatting completed successfully")
            return response_content
            
        except Exception as e:
            logger.error(f"❌ Error formatting email response: {e}")
            return self._create_fallback_email(content, customer_name)
    
    def _create_fallback_email(self, content: str, customer_name: str = "Valued Customer") -> str:
        """Create a fallback email when formatting fails."""
        return f"""Dear {customer_name},

Thank you for contacting our support team.

{content}

If you have any additional questions, please don't hesitate to reach out.

Best regards,  
Thomas von Mentlen
Customer Support Team  
Nakamo
tvm@nakamo.io"""
    
    async def invoke(self, content: str, customer_info: Optional[Dict[str, Any]] = None, chat_history: Optional[ChatHistory] = None) -> str:
        """Main method to invoke the email formatting agent.
        
        Args:
            content: The content to format as an email (typically question + answer from other agents)
            customer_info: Optional customer information extracted from original request
            chat_history: Optional chat history (not used in formatting but kept for compatibility)
            
        Returns:
            Professionally formatted email response
        """
        return await self.format_email_response(content, customer_info)


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_email_formatting_agent():
        """Test the Email Formatting Agent with sample content."""
        try:
            agent = SupportEmailAgent()
            
            # Test formatting with content already provided
            content = """Question: I'm having trouble logging into my account. I keep getting an error message that says "Invalid credentials" even though I'm sure my password is correct.

Answer: This is usually caused by one of the following issues:

1. **Password Reset Needed**: Your password may have expired or been reset for security reasons.
2. **Browser Cache**: Clear your browser cache and cookies, then try again.
3. **Caps Lock**: Ensure Caps Lock is off when entering your password.
4. **Account Lock**: Your account may be temporarily locked after multiple failed attempts.

**Solution Steps:**
1. Try resetting your password using the "Forgot Password" link
2. Clear your browser cache and cookies
3. Wait 15 minutes if account is locked, then try again
4. Contact support if issues persist

We're here to help ensure you can access your account securely."""
            
            customer_info = {
                'customer_name': 'John Smith',
                'subject': 'Account Login Issues',
                'sender_email': 'john.smith@email.com'
            }
            
            print("Testing Email Formatting Agent...")
            print("=" * 50)
            
            response = await agent.format_email_response(content, customer_info)
            print("Formatted Email Response:")
            print(response)
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run the test
    asyncio.run(test_email_formatting_agent())
