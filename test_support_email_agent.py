#!/usr/bin/env python3
"""
Test script for the Support Email Agent
"""

import asyncio
import logging
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.support_email_agent import SupportEmailAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_support_email_agent():
    """Test the Support Email Agent with various email formats."""
    
    print("🚀 Testing Support Email Agent")
    print("=" * 60)
    
    try:
        agent = SupportEmailAgent()
        print("✅ Support Email Agent initialized successfully\n")
        
        # Test cases
        test_cases = [
            {
                "name": "Formal Support Email",
                "content": """
Subject: Account Login Issues

Dear Support Team,

I hope this email finds you well. I'm writing to report an issue I'm experiencing with my account login. 

Every time I try to log in with my credentials, I receive an error message stating "Invalid credentials" even though I'm confident that my username and password are correct. I've tried resetting my password twice, but the problem persists.

Could you please help me resolve this issue? I need to access my account urgently for an important project.

Thank you for your time and assistance.

Best regards,
John Smith
john.smith@company.com
"""
            },
            {
                "name": "Casual Support Request",
                "content": """
Hi there!

I'm having trouble with my billing. The payment didn't go through last month and now my account is suspended. Can you help me fix this?

Thanks!
Sarah
"""
            },
            {
                "name": "Technical Issue Email",
                "content": """
Subject: API Integration Problems

Hello Support,

I'm a developer trying to integrate with your API, but I keep getting 401 errors even with the correct API key. I've checked the documentation multiple times.

Here are the details:
- API Key: [REDACTED]
- Endpoint: /api/v1/users
- Error: 401 Unauthorized

Can someone from the technical team help me with this?

Best,
Mike Developer
mike@techcompany.com
"""
            },
            {
                "name": "Non-Email Format (for comparison)",
                "content": "How do I reset my password?"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"📧 Test Case {i}: {test_case['name']}")
            print("-" * 40)
            print("INPUT:")
            print(test_case['content'])
            print("\nRESPONSE:")
            
            try:
                response = await agent.invoke(test_case['content'])
                print(response)
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "=" * 60 + "\n")
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Failed to initialize or test Support Email Agent: {e}")
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_support_email_agent())
