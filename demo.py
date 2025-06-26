"""
Simple demo script to test the multi-agent system.
"""
import asyncio
import os
from dotenv import load_dotenv
from agents import OrchestratorAgent

load_dotenv()

async def demo():
    """Run a simple demo of the multi-agent system."""
    
    # Check environment variables
    endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not endpoint or not deployment_name:
        print("❌ Missing required environment variables:")
        print(f"   AZURE_AI_FOUNDRY_ENDPOINT: {'✅' if endpoint else '❌'}")
        print(f"   AZURE_OPENAI_DEPLOYMENT_NAME: {'✅' if deployment_name else '❌'}")
        print("\nPlease check your .env file!")
        return
    
    print("🚀 Initializing Multi-Agent System...")
    print(f"📍 Endpoint: {endpoint}")
    print(f"🤖 Model: {deployment_name}")
    print()
    
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent(endpoint, deployment_name)
        print("✅ Orchestrator Agent initialized successfully!")
        
        # Test questions
        test_questions = [
            "What is artificial intelligence?",
            "How can I improve my productivity?",
            "Explain the benefits of cloud computing"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Test {i}: {question}")
            print("=" * 50)
            
            response_parts = []
            async for response in orchestrator.handle_request(question):
                if response.content:
                    response_parts.append(response.content)
            
            full_response = " ".join(response_parts)
            print(f"🤖 Response: {full_response}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your Azure AI Foundry endpoint is correct")
        print("2. Your deployment name is correct") 
        print("3. You have proper authentication (az login or managed identity)")

if __name__ == "__main__":
    asyncio.run(demo())
