"""
Demo script to test the multi-agent system including Customer Support QnA.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.qna_agent import QnAAgent

load_dotenv()

async def demo_orchestrator():
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
        orchestrator = OrchestratorAgent()
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
            
            response = await orchestrator.handle_request(question)
            print(f"🤖 Response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. Your Azure AI Foundry endpoint is correct")
        print("2. Your deployment name is correct") 
        print("3. You have the correct AZURE_OPENAI_API_KEY set")


async def demo_customer_support():
    """Run a demo of the Customer Support QnA agent."""
    print("🎯 Starting Customer Support QnA Demo")
    print("="*50)
    
    try:
        # Initialize QnA agent
        qna_agent = QnAAgent()
        
        # Check and populate sample data if needed
        stats = await qna_agent.get_database_stats()
        print(f"📊 Database Stats: {stats}")
        
        if stats["total_documents"] == 0:
            print("🌱 Populating with sample data...")
            await qna_agent.populate_sample_data()
            stats = await qna_agent.get_database_stats()
            print(f"📊 Updated Stats: {stats}")
        
        # Test customer support questions
        test_questions = [
            "How do I reset my password?",
            "I'm having billing issues with my account",
            "The application is running slowly, what can I do?",
            "How do I export my data?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔸 Question {i}: {question}")
            print("-" * 40)
            
            answer = await qna_agent.answer_question(question)
            print(f"🤖 Answer: {answer}")
            
            if i < len(test_questions):
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"❌ Customer Support Demo Error: {e}")


def print_help():
    """Print help information."""
    print("🎪 Python Agents Demo")
    print("="*50)
    print("Available commands:")
    print("  python demo.py                    - Run orchestrator demo")
    print("  python demo.py orchestrator       - Run orchestrator demo")
    print("  python demo.py customer-support   - Run customer support QnA demo") 
    print("  python demo.py help               - Show this help")
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            print_help()
        elif command == "orchestrator":
            asyncio.run(demo_orchestrator())
        elif command == "customer-support":
            asyncio.run(demo_customer_support())
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    else:
        # Default to orchestrator demo
        asyncio.run(demo_orchestrator())
