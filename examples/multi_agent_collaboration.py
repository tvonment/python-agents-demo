"""
Advanced example demonstrating multi-agent collaboration.
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


async def collaborative_content_creation():
    """Demonstrate collaborative content creation using multiple agents."""
    print("=== Collaborative Content Creation Demo ===")
    
    # Initialize agents
    coordinator = CoordinatorAgent()
    research_agent = ResearchAgent()
    writing_agent = WritingAgent()
    
    # Define the collaborative task
    task_description = """
    Create a comprehensive white paper on 'The Impact of AI on Modern Healthcare'.
    The document should include:
    1. Current state analysis
    2. Key trends and developments
    3. Benefits and challenges
    4. Future outlook and recommendations
    5. Well-written, professional presentation
    """
    
    print(f"Collaborative Task: {task_description}")
    print("-" * 50)
    
    # Step 1: Coordinator analyzes the task
    print("\n1. Task Analysis by Coordinator...")
    task_analysis = await coordinator.analyze_task_requirements(task_description)
    print("Task Analysis:")
    print(task_analysis["analysis"])
    print("-" * 50)
    
    # Step 2: Research Agent gathers information
    print("\n2. Research Agent gathering information...")
    research_topics = [
        "AI applications in healthcare",
        "Healthcare AI market trends 2024",
        "AI healthcare implementation challenges"
    ]
    
    research_results = []
    for topic in research_topics:
        result = await research_agent.conduct_research(topic, depth="comprehensive")
        research_results.append(f"Research on {topic}:\n{result}")
    
    combined_research = "\n\n".join(research_results)
    print("Research completed. Key findings gathered.")
    print("-" * 50)
    
    # Step 3: Writing Agent creates the white paper structure
    print("\n3. Writing Agent creating document structure...")
    outline_request = f"""
    Based on this research: {combined_research[:500]}...
    
    Create a detailed outline for a white paper on 'The Impact of AI on Modern Healthcare'
    """
    
    # Get basic response for outline
    outline_response = await writing_agent.invoke(outline_request)
    print("Document Outline:")
    print(outline_response.content)
    print("-" * 50)
    
    # Step 4: Writing Agent creates the white paper content
    print("\n4. Writing Agent creating white paper content...")
    content_request = f"""
    Using this research: {combined_research[:800]}...
    
    Write a professional white paper on 'The Impact of AI on Modern Healthcare'.
    Include executive summary, main sections, and conclusion.
    Target audience: Healthcare executives and IT decision makers.
    """
    
    white_paper_response = await writing_agent.invoke(content_request)
    print("White Paper Draft:")
    print(white_paper_response.content[:1000] + "..." if len(white_paper_response.content) > 1000 else white_paper_response.content)
    print("-" * 50)
    
    # Step 5: Coordinator reviews and provides feedback
    print("\n5. Coordinator reviewing final output...")
    review_request = f"""
    Review this white paper draft for completeness and quality:
    {white_paper_response.content[:500]}...
    
    Provide feedback on:
    - Content completeness
    - Structure and flow
    - Professional quality
    - Recommendations for improvement
    """
    
    review_response = await coordinator.invoke(review_request)
    print("Coordinator Review:")
    print(review_response.content)
    print("-" * 50)
    
    return {
        "task_analysis": task_analysis,
        "research_results": combined_research,
        "white_paper": white_paper_response.content,
        "review": review_response.content
    }


async def multi_agent_group_chat_demo():
    """Demonstrate group chat coordination between agents."""
    print("\n=== Multi-Agent Group Chat Demo ===")
    
    try:
        # Initialize agents
        coordinator = CoordinatorAgent()
        research_agent = ResearchAgent()
        writing_agent = WritingAgent()
        
        # Define a complex task requiring collaboration
        complex_task = """
        Develop a strategic plan for implementing AI chatbots in a hospital system.
        Consider technical requirements, staff training, patient experience,
        and compliance requirements.
        """
        
        print(f"Complex Task: {complex_task}")
        print("-" * 50)
        
        # Coordinate the task using multiple agents
        agents = [research_agent, writing_agent]
        
        print("\nInitiating multi-agent coordination...")
        coordination_results = await coordinator.coordinate_task(
            task_description=complex_task,
            agents=agents,
            max_rounds=6
        )
        
        print("\nCoordination Results:")
        for i, result in enumerate(coordination_results, 1):
            print(f"\nRound {i}: {result}")
            print("-" * 30)
        
        return coordination_results
        
    except Exception as e:
        logger.error(f"Error in group chat demo: {str(e)}")
        print(f"Group chat demo encountered an error: {str(e)}")
        print("This is expected if group chat features are not fully configured.")
        return []


async def main():
    """Run the advanced multi-agent collaboration demo."""
    try:
        print("Advanced Multi-Agent Collaboration Demo")
        print("=" * 60)
        
        # Run collaborative content creation
        collaboration_results = await collaborative_content_creation()
        
        # Run group chat demo
        group_chat_results = await multi_agent_group_chat_demo()
        
        print("\n" + "=" * 60)
        print("Advanced demo completed!")
        print("\nDemo Summary:")
        print("✓ Task analysis and breakdown")
        print("✓ Research data gathering")
        print("✓ Content creation and editing")
        print("✓ Multi-agent coordination")
        print("✓ Quality review and feedback")
        
        if collaboration_results:
            print(f"\n📊 Generated white paper: {len(collaboration_results['white_paper'])} characters")
        
        if group_chat_results:
            print(f"💬 Group chat rounds: {len(group_chat_results)}")
        
    except Exception as e:
        logger.error(f"Error during advanced demo: {str(e)}")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure .env file is configured with Azure AI Foundry credentials")
        print("2. Check network connectivity to Azure services")
        print("3. Verify model deployment names match your Azure configuration")
        print("4. Review logs for detailed error information")


if __name__ == "__main__":
    asyncio.run(main())
