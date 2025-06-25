"""
Test script to verify Azure AI Foundry connection and configuration.
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


async def test_configuration():
    """Test the Azure AI Foundry configuration."""
    print("Testing Azure AI Foundry Configuration")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'AZURE_AI_FOUNDRY_PROJECT_ENDPOINT',
        'AZURE_AI_FOUNDRY_API_KEY',
        'DEFAULT_MODEL_DEPLOYMENT_NAME'
    ]
    
    print("1. Checking environment variables...")
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required variables: {', '.join(missing_vars)}")
        print("Please run: python setup_azure.py")
        return False
    
    # Test imports
    print("\n2. Testing imports...")
    try:
        from src.config import settings
        print("   ✅ Configuration module imported")
        
        from src.agents import ResearchAgent
        print("   ✅ Agent modules imported")
        
        from semantic_kernel import Kernel
        from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion
        print("   ✅ Semantic Kernel modules imported")
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False
    
    # Test configuration loading
    print("\n3. Testing configuration loading...")
    try:
        print(f"   ✅ Primary endpoint: {settings.primary_endpoint}")
        print(f"   ✅ Default model: {settings.default_model_deployment_name}")
        print(f"   ✅ Authentication method: {'Entra ID' if settings.use_entra_id else 'API Key'}")
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test agent creation
    print("\n4. Testing agent creation...")
    try:
        research_agent = ResearchAgent()
        print("   ✅ Research agent created")
        
        # Test kernel creation (this will validate the Azure connection parameters)
        kernel = research_agent.kernel
        print("   ✅ Kernel created with Azure AI services")
        
    except Exception as e:
        print(f"   ❌ Agent creation error: {e}")
        print("   Check your Azure AI Foundry credentials and endpoint")
        return False
    
    # Test basic agent invocation
    print("\n5. Testing basic agent invocation...")
    try:
        # Simple test message
        test_message = "Hello! Please respond with a brief greeting."
        response = await research_agent.invoke(test_message)
        
        print(f"   ✅ Agent response received: {response.content[:100]}...")
        print("   ✅ Azure AI Foundry connection working!")
        
    except Exception as e:
        print(f"   ❌ Agent invocation error: {e}")
        print("   This could be due to:")
        print("   - Invalid API key")
        print("   - Incorrect model deployment name")
        print("   - Network connectivity issues")
        print("   - Model deployment not ready")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your Azure AI Foundry setup is working correctly.")
    print("\nNext steps:")
    print("- Run: python examples/basic_agent_demo.py")
    print("- Try: python examples/multi_agent_collaboration.py")
    
    return True


async def main():
    """Main test function."""
    try:
        success = await test_configuration()
        if not success:
            print("\n🔧 Setup help:")
            print("1. Run: python setup_azure.py")
            print("2. Verify your Azure AI Foundry project is active")
            print("3. Check your model deployments in Azure AI Foundry portal")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Test failed with unexpected error")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
