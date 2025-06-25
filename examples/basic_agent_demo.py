"""
Basic example demonstrating individual agent capabilities.
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import agents
from src.agents import ResearchAgent, WritingAgent, CoordinatorAgent


async def demo_research_agent():
    """Demonstrate ResearchAgent capabilities."""
    print("=== Research Agent Demo ===")
    
    research_agent = ResearchAgent()
    
    # Conduct research on a topic
    topic = "artificial intelligence in healthcare"
    research_result = await research_agent.conduct_research(topic, depth="basic")
    
    print(f"Research on '{topic}':")
    print(research_result)
    print("-" * 50)
    
    # Analyze some data
    data_description = "Patient recovery times after implementing AI-assisted diagnosis"
    analysis_result = await research_agent.analyze_data(data_description)
    
    print(f"Data Analysis: {data_description}")
    print(analysis_result)
    print("-" * 50)


async def demo_writing_agent():
    """Demonstrate WritingAgent capabilities."""
    print("\n=== Writing Agent Demo ===")
    
    writing_agent = WritingAgent()
    
    # Write an article
    topic = "The Future of AI in Healthcare"
    article = await writing_agent.write_article(
        topic=topic,
        audience="healthcare professionals",
        style="informative",
        length="medium"
    )
    
    print(f"Article on '{topic}':")
    print(article)
    print("-" * 50)
    
    # Create a summary
    content_to_summarize = """
    Artificial Intelligence is revolutionizing healthcare through various applications.
    Machine learning algorithms can analyze medical images with high accuracy,
    helping radiologists detect diseases earlier. Natural language processing
    enables better analysis of patient records and clinical notes.
    AI-powered chatbots provide 24/7 patient support and initial triage.
    Predictive analytics help hospitals optimize resource allocation and
    anticipate patient needs. However, challenges remain in terms of
    data privacy, algorithm bias, and regulatory compliance.
    """
    
    summary = await writing_agent.create_summary(content_to_summarize, "executive")
    
    print("Executive Summary:")
    print(summary)
    print("-" * 50)


async def demo_coordinator_agent():
    """Demonstrate CoordinatorAgent capabilities."""
    print("\n=== Coordinator Agent Demo ===")
    
    coordinator = CoordinatorAgent()
    
    # Analyze task requirements
    task = "Create a comprehensive report on AI implementation in hospitals"
    analysis = await coordinator.analyze_task_requirements(task)
    
    print(f"Task Analysis for: {task}")
    print(analysis["analysis"])
    print("-" * 50)


async def main():
    """Run all agent demonstrations."""
    try:
        print("Multi-Agent System Demo")
        print("=" * 50)
        
        await demo_research_agent()
        await demo_writing_agent()
        await demo_coordinator_agent()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during demo: {str(e)}")
        print(f"Error: {str(e)}")
        print("\nPlease check your configuration:")
        print("1. Copy .env.example to .env")
        print("2. Set your Azure AI Foundry endpoint and API key")
        print("3. Ensure all required packages are installed")


if __name__ == "__main__":
    asyncio.run(main())
