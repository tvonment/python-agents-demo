"""
Customer Support QnA Demo - Test the enhanced QnA agent with vector search capabilities.
"""

import asyncio
import logging
from dotenv import load_dotenv
from src.agents.qna_agent import QnAAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_customer_support_qna():
    """Demonstrate the Customer Support QnA agent capabilities."""
    try:
        logger.info("🎯 Starting Customer Support QnA Demo")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize the QnA agent
        logger.info("🚀 Initializing Customer Support QnA Agent...")
        qna_agent = QnAAgent()
        
        # Check database status and populate sample data if needed
        stats = await qna_agent.get_database_stats()
        logger.info(f"📊 Database Stats: {stats}")
        
        if stats["total_documents"] == 0:
            logger.info("🌱 Database is empty, populating with sample data...")
            await qna_agent.populate_sample_data()
            stats = await qna_agent.get_database_stats()
            logger.info(f"📊 Updated Database Stats: {stats}")
        
        # Demo questions to test different scenarios
        demo_questions = [
            # Billing questions
            "How do I update my billing information?",
            "I don't understand the charges on my invoice",
            
            # Account management
            "I forgot my password, how can I reset it?",
            "How do I set up two-factor authentication?",
            
            # Technical issues
            "The application is running very slowly",
            "What are the API rate limits?",
            
            # Features
            "How can I export my data?",
            "How do I invite team members to collaborate?",
            
            # Test question not in knowledge base
            "What's the weather like today?",
            
            # Complex question requiring multiple documents
            "I'm having trouble with my account security and billing at the same time"
        ]
        
        print("\n" + "="*80)
        print("🎪 CUSTOMER SUPPORT QNA AGENT DEMO")
        print("="*80)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n🔸 Question {i}: {question}")
            print("-" * 60)
            
            try:
                # Answer with knowledge base
                answer = await qna_agent.answer_question(question, use_knowledge_base=True)
                print(f"🤖 Answer: {answer}")
                
                # Add some spacing between questions
                if i < len(demo_questions):
                    print("\n" + "⏳ Waiting before next question...")
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error answering question {i}: {e}")
                print(f"❌ Error: {e}")
        
        print("\n" + "="*80)
        print("🎉 Demo completed successfully!")
        print("="*80)
        
        # Show final database stats
        final_stats = await qna_agent.get_database_stats()
        print(f"\n📊 Final Database Stats:")
        print(f"   Total Documents: {final_stats['total_documents']}")
        print(f"   Categories: {', '.join(final_stats['categories'])}")
        print(f"   Status: {final_stats['database_status']}")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


async def interactive_demo():
    """Interactive demo where users can ask questions."""
    try:
        logger.info("🎯 Starting Interactive Customer Support QnA Demo")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize the QnA agent
        qna_agent = QnAAgent()
        
        # Check and populate sample data if needed
        stats = await qna_agent.get_database_stats()
        if stats["total_documents"] == 0:
            logger.info("🌱 Populating sample data...")
            await qna_agent.populate_sample_data()
        
        print("\n" + "="*80)
        print("🎪 INTERACTIVE CUSTOMER SUPPORT QNA AGENT")
        print("="*80)
        print("Ask me any customer support questions!")
        print("Type 'quit', 'exit', or 'bye' to end the session.")
        print("Type 'stats' to see database statistics.")
        print("="*80)
        
        while True:
            try:
                question = input("\n🔸 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye! Thanks for using Customer Support QnA!")
                    break
                
                if question.lower() == 'stats':
                    stats = await qna_agent.get_database_stats()
                    print(f"\n📊 Database Statistics:")
                    print(f"   Total Documents: {stats['total_documents']}")
                    print(f"   Categories: {', '.join(stats['categories'])}")
                    print(f"   Status: {stats['database_status']}")
                    continue
                
                if not question:
                    print("⚠️ Please enter a question.")
                    continue
                
                print(f"\n🤖 Processing your question...")
                answer = await qna_agent.answer_question(question, use_knowledge_base=True)
                print(f"\n💬 Answer: {answer}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error processing question: {e}")
                print(f"❌ Sorry, I encountered an error: {e}")
    
    except Exception as e:
        logger.error(f"❌ Interactive demo failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_demo())
    else:
        asyncio.run(demo_customer_support_qna())
