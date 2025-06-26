"""
Customer Support Email Demo - Demonstrates the Support Email Agent functionality.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.support_email_agent import SupportEmailAgent
from agents.orchestrator_agent import OrchestratorAgent

load_dotenv()


async def demo_support_email_agent():
    """Demo the Support Email Agent directly."""
    
    print("📧 Customer Support Email Agent Demo")
    print("=" * 60)
    
    try:
        agent = SupportEmailAgent()
        print("✅ Support Email Agent initialized successfully!\n")
        
        # Sample support emails
        sample_emails = [
            {
                "title": "Login Issues",
                "email": """Subject: Can't Access My Account

Dear Support,

I've been trying to log into my account for the past hour but keep getting an "Invalid credentials" error. I'm sure I'm using the right password because I wrote it down.

Can you help me get back into my account? I have important work to do.

Thank you,
Jennifer Martinez
j.martinez@company.com"""
            },
            {
                "title": "Billing Question", 
                "email": """Subject: Question about my invoice

Hi there,

I received my monthly bill today and noticed a charge I don't recognize. There's a $15.99 fee labeled "Premium Features" but I don't remember signing up for any premium features.

Could someone explain what this charge is for?

Best,
Robert Chen
robert.c@email.com"""
            },
            {
                "title": "Feature Request",
                "email": """Subject: Feature Request - Dark Mode

Hello Support Team,

I love using your application, but I was wondering if you have any plans to add a dark mode option? I work late hours and the bright interface can be hard on my eyes.

Many of my colleagues have also expressed interest in this feature.

Thanks for considering this!

Warm regards,
Lisa Thompson
lisa.t@techcorp.com"""
            }
        ]
        
        for i, sample in enumerate(sample_emails, 1):
            print(f"📨 Email {i}: {sample['title']}")
            print("-" * 40)
            print("INCOMING EMAIL:")
            print(sample['email'])
            print("\n📤 GENERATED RESPONSE:")
            print("-" * 40)
            
            try:
                response = await agent.invoke(sample['email'])
                print(response)
            except Exception as e:
                print(f"❌ Error processing email: {e}")
            
            print("\n" + "=" * 60 + "\n")
            
    except Exception as e:
        print(f"❌ Failed to initialize Support Email Agent: {e}")


async def demo_orchestrator_with_emails():
    """Demo the Orchestrator Agent handling email formats."""
    
    print("🎭 Orchestrator with Email Support Demo")
    print("=" * 60)
    
    try:
        orchestrator = OrchestratorAgent()
        await orchestrator.initialize_async_components()
        print("✅ Orchestrator initialized successfully!\n")
        
        # Mixed request types
        test_requests = [
            {
                "type": "Regular Question",
                "content": "How do I reset my password?"
            },
            {
                "type": "Email Format",
                "content": """Subject: Technical Support Needed

Dear Support Team,

I'm experiencing issues with the API integration. I keep getting 500 errors when making requests to the /api/users endpoint.

Can someone from your technical team help me debug this?

Best regards,
David Kim
david@startup.com"""
            },
            {
                "type": "Weather Question",
                "content": "What's the weather like in Paris today?"
            },
            {
                "type": "Email with Weather Question",
                "content": """Subject: Travel Weather Inquiry

Hi Support,

I'm planning a business trip to Tokyo next week. Could you help me check the current weather conditions there?

Thanks!
Maria Santos
maria.santos@consulting.com"""
            }
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"🔍 Request {i}: {request['type']}")
            print("-" * 40)
            print("INPUT:")
            print(request['content'])
            print("\n🤖 ORCHESTRATOR RESPONSE:")
            print("-" * 40)
            
            try:
                response = await orchestrator.handle_request(request['content'])
                print(response)
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "=" * 60 + "\n")
            
    except Exception as e:
        print(f"❌ Failed to initialize Orchestrator: {e}")


async def main():
    """Run both demos."""
    
    # Check environment variables
    endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not all([endpoint, deployment_name, api_key]):
        print("❌ Missing required environment variables:")
        print(f"   AZURE_AI_FOUNDRY_ENDPOINT: {'✅' if endpoint else '❌'}")
        print(f"   AZURE_OPENAI_DEPLOYMENT_NAME: {'✅' if deployment_name else '❌'}")
        print(f"   AZURE_OPENAI_API_KEY: {'✅' if api_key else '❌'}")
        print("\nPlease check your .env file!")
        return
    
    print("🚀 Customer Support System Demo")
    print("=" * 60)
    print(f"📍 Endpoint: {endpoint}")
    print(f"🤖 Model: {deployment_name}")
    print(f"🔐 API Key: {'***SET***' if api_key else 'NOT SET'}")
    print()
    
    # Run the Support Email Agent demo first
    await demo_support_email_agent()
    
    # Then run the Orchestrator demo
    await demo_orchestrator_with_emails()
    
    print("🎉 All demos completed!")


if __name__ == "__main__":
    asyncio.run(main())
