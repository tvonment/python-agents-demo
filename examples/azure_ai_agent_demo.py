"""
Example demonstrating Azure AI Agent integration.
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

try:
    from semantic_kernel.agents import AzureAIAgent
    from azure.identity import DefaultAzureCredential
    AZURE_AI_AGENT_AVAILABLE = True
except ImportError:
    AZURE_AI_AGENT_AVAILABLE = False
    print("Note: AzureAIAgent features require additional Azure configuration")

from src.config import settings


async def demo_azure_ai_agent():
    """Demonstrate Azure AI Agent capabilities."""
    if not AZURE_AI_AGENT_AVAILABLE:
        print("Azure AI Agent demo skipped - requires Azure AI Foundry project setup")
        return
    
    if not settings.azure_ai_agent_endpoint:
        print("Azure AI Agent demo skipped - AZURE_AI_AGENT_ENDPOINT not configured")
        return
    
    print("=== Azure AI Agent Demo ===")
    
    try:
        # Create Azure AI Agent using Foundry project
        async with (
            DefaultAzureCredential() as creds,
            AzureAIAgent.create_client(
                credential=creds,
                endpoint=settings.azure_ai_agent_endpoint
            ) as client,
        ):
            # Define agent configuration
            agent_config = {
                "name": "Healthcare Research Assistant",
                "instructions": """
                You are a Healthcare Research Assistant specialized in analyzing
                medical literature and providing evidence-based insights.
                
                Your capabilities include:
                - Reviewing medical research papers
                - Summarizing clinical findings
                - Identifying treatment patterns
                - Providing evidence-based recommendations
                
                Always cite sources and indicate confidence levels in your responses.
                """,
                "model": {
                    "id": settings.azure_ai_agent_model_deployment_name or settings.default_model_deployment_name
                }
            }
            
            # Create the Azure AI Agent
            azure_agent = await AzureAIAgent.create(
                client=client,
                **agent_config
            )
            
            print(f"Created Azure AI Agent: {azure_agent.name}")
            print(f"Agent ID: {azure_agent.id}")
            print("-" * 50)
            
            # Test agent with healthcare research query
            research_query = """
            What are the latest developments in AI-assisted surgical procedures?
            Please provide a summary of recent advances and their clinical outcomes.
            """
            
            print(f"Query: {research_query}")
            print("\nAgent Response:")
            
            # Get response from Azure AI Agent
            response = await azure_agent.invoke(research_query)
            print(response.content)
            print("-" * 50)
            
            # Test with follow-up question
            followup_query = """
            What are the main safety considerations and regulatory requirements
            for implementing AI-assisted surgery in hospitals?
            """
            
            print(f"\nFollow-up Query: {followup_query}")
            print("\nAgent Response:")
            
            followup_response = await azure_agent.invoke(followup_query)
            print(followup_response.content)
            print("-" * 50)
            
            print("Azure AI Agent demo completed successfully!")
            
    except Exception as e:
        logger.error(f"Error in Azure AI Agent demo: {str(e)}")
        print(f"Error: {str(e)}")
        print("\nThis may be due to:")
        print("1. Missing Azure AI Foundry project configuration")
        print("2. Incorrect endpoint or model deployment name")
        print("3. Authentication issues with Azure credentials")
        print("4. Network connectivity problems")


async def demo_declarative_agent():
    """Demonstrate declarative agent creation using YAML configuration."""
    print("\n=== Declarative Agent Demo ===")
    
    # Example YAML configuration for an agent
    yaml_config = """
type: foundry_agent
name: ContentAnalyzer
instructions: |
  You are a Content Analyzer specialized in evaluating written content.
  
  Your responsibilities include:
  - Analyzing content quality and readability
  - Identifying key themes and topics
  - Providing improvement suggestions
  - Assessing target audience alignment
  
  Provide detailed, actionable feedback on all content you review.

model:
  id: ${AzureAI:ChatModelId}

tools:
  - id: ContentAnalysis.analyze_readability
    type: function
  - id: ContentAnalysis.extract_themes
    type: function
  - id: ContentAnalysis.suggest_improvements
    type: function
"""
    
    print("Example Declarative Agent Configuration:")
    print(yaml_config)
    print("-" * 50)
    
    print("Benefits of Declarative Agents:")
    print("✓ Easy configuration management")
    print("✓ Version control for agent definitions")
    print("✓ Consistent agent behavior across deployments")
    print("✓ Simplified agent creation and modification")
    print("✓ Integration with existing Azure AI Foundry projects")
    
    if not AZURE_AI_AGENT_AVAILABLE:
        print("\nNote: To use declarative agents, you need:")
        print("1. Azure AI Foundry project (GA version, created after May 19, 2025)")
        print("2. Semantic Kernel version 1.31.0 or higher")
        print("3. Properly configured Azure credentials")
        print("4. Model deployments in your Azure AI Foundry project")


async def demo_azure_integration_best_practices():
    """Demonstrate Azure integration best practices."""
    print("\n=== Azure Integration Best Practices ===")
    
    print("🔧 Configuration Management:")
    print("✓ Use environment variables for sensitive data")
    print("✓ Implement proper credential management")
    print("✓ Configure appropriate timeout and retry policies")
    print("✓ Use Azure Key Vault for production secrets")
    
    print("\n🔒 Security Best Practices:")
    print("✓ Use Azure Managed Identity when possible")
    print("✓ Implement least privilege access principles")
    print("✓ Enable audit logging and monitoring")
    print("✓ Regularly rotate API keys and secrets")
    
    print("\n📊 Performance Optimization:")
    print("✓ Implement connection pooling")
    print("✓ Use appropriate model sizes for your use case")
    print("✓ Monitor token usage and costs")
    print("✓ Implement caching for frequently requested data")
    
    print("\n🏗️ Production Deployment:")
    print("✓ Use Azure Container Instances or App Service")
    print("✓ Implement health checks and monitoring")
    print("✓ Set up CI/CD pipelines")
    print("✓ Configure auto-scaling based on demand")
    
    print("\n💰 Cost Management:")
    print("✓ Monitor API usage and costs regularly")
    print("✓ Implement usage quotas and limits")
    print("✓ Use appropriate pricing tiers")
    print("✓ Consider reserved capacity for predictable workloads")


async def main():
    """Run the Azure AI Agent demonstration."""
    try:
        print("Azure AI Agent Integration Demo")
        print("=" * 50)
        
        # Check configuration
        print("Configuration Check:")
        print(f"✓ Azure AI Inference Endpoint: {'✓' if settings.azure_ai_inference_endpoint else '✗'}")
        print(f"✓ Azure AI Agent Endpoint: {'✓' if settings.azure_ai_agent_endpoint else '✗'}")
        print(f"✓ Model Deployment Name: {settings.default_model_deployment_name}")
        print(f"✓ Using Entra ID: {'✓' if settings.use_entra_id else '✗'}")
        print("-" * 50)
        
        # Run demos
        await demo_azure_ai_agent()
        await demo_declarative_agent()
        await demo_azure_integration_best_practices()
        
        print("\n" + "=" * 50)
        print("Azure AI Agent demo completed!")
        
    except Exception as e:
        logger.error(f"Error during Azure AI Agent demo: {str(e)}")
        print(f"Error: {str(e)}")
        print("\nSetup Instructions:")
        print("1. Create an Azure AI Foundry project")
        print("2. Deploy models to your project")
        print("3. Configure environment variables in .env file")
        print("4. Ensure Azure credentials are properly set up")


if __name__ == "__main__":
    asyncio.run(main())
