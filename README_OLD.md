# Microsoft Semantic Kernel Multi-Agent Solution with Azure AI Foundry

A comprehensive multi-agent solution built with Microsoft Semantic Kernel and Azure AI Foundry models. This project demonstrates how to create, coordinate, and deploy intelligent agents that can collaborate to solve complex tasks.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for research, writing, and coordination
- **Azure AI Foundry Integration**: Native support for Azure AI Foundry projects and models (GA version)
- **Flexible Plugin System**: Extensible plugins for web search, data analysis, content creation, and task management
- **Advanced Coordination**: Sophisticated agent orchestration with group chat capabilities
- **Multiple Authentication Methods**: Support for API keys and Azure Entra ID authentication
- **Production Ready**: Comprehensive configuration, logging, and error handling
- **Fully Tested**: Complete test suite with mocking for Azure services

## 🏗️ Architecture

### Core Agents

- **ResearchAgent**: Specializes in information gathering, data analysis, and fact-checking
- **WritingAgent**: Focuses on content creation, editing, and summarization
- **CoordinatorAgent**: Orchestrates multi-agent interactions and task management

### Plugin System

- **Research Plugins**: Web search, trend analysis, and fact-checking
- **Writing Plugins**: Content creation, editing, and formatting
- **Coordination Plugins**: Task management and workload distribution

## 📋 Prerequisites

- Python 3.10 or later
- Azure subscription with AI Foundry access
- Azure AI Foundry project with deployed models

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-agents-demo
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AI Foundry credentials
   ```

## 🔧 Azure AI Foundry Setup

### Prerequisites
- Python 3.10 or later
- Azure AI Foundry project (created after May 19, 2025 for GA support)
- Access to deployed models in your Azure AI Foundry project

### Your Project Configuration
Based on your Azure AI Foundry project URL:
```
https://tvonment-ai-resource.services.ai.azure.com/api/projects/tvonment-ai
```

### Getting Started

1. **Automated Setup** (Recommended):
   ```bash
   python setup_azure.py
   ```
   This will guide you through the configuration process.

2. **Manual Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AI Foundry credentials
   ```

### Azure AI Foundry Credentials

To get your credentials:
1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Navigate to your project: `tvonment-ai`
3. Go to **"Models + endpoints"** section
4. Note your:
   - API key
   - Model deployment names (e.g., `gpt-4o-mini`, `gpt-4o`)
   - Specific model endpoints (if using serverless deployments)

### Required Environment Variables

Create a `.env` file with the following configuration:

```bash
# Azure AI Foundry Configuration
AZURE_AI_INFERENCE_ENDPOINT=https://your-model-endpoint.inference.ml.azure.com
AZURE_AI_INFERENCE_API_KEY=your-api-key-here

# Azure AI Agent Configuration (optional, for AzureAIAgent features)
AZURE_AI_AGENT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=your-model-deployment

# Model Configuration
DEFAULT_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
EMBEDDING_MODEL_DEPLOYMENT_NAME=text-embedding-ada-002

# Application Settings
LOG_LEVEL=INFO
MAX_TOKENS=1000
TEMPERATURE=0.7
```

### Azure Authentication Options

**Option 1: API Key Authentication** (Recommended for development)
```bash
AZURE_AI_INFERENCE_API_KEY=your-api-key
```

**Option 2: Azure Entra ID Authentication** (Recommended for production)
```bash
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

## 🏃‍♂️ Quick Start

### Basic Agent Demo

```bash
python examples/basic_agent_demo.py
```

This demonstrates individual agent capabilities:
- Research agent conducting information gathering
- Writing agent creating and editing content
- Coordinator agent analyzing tasks

### Multi-Agent Collaboration

```bash
python examples/multi_agent_collaboration.py
```

This showcases advanced collaboration:
- Coordinated task breakdown and assignment
- Multi-agent content creation workflow
- Group chat orchestration

### Azure AI Agent Integration

```bash
python examples/azure_ai_agent_demo.py
```

This demonstrates Azure AI Foundry integration:
- Azure AI Agent creation and management
- Declarative agent configuration
- Integration best practices

## 📚 Usage Examples

### Creating a Research Agent

```python
from src.agents import ResearchAgent

# Initialize the agent
research_agent = ResearchAgent()

# Conduct research
results = await research_agent.conduct_research(
    topic="AI in healthcare",
    depth="comprehensive"
)
print(results)
```

### Multi-Agent Coordination

```python
from src.agents import CoordinatorAgent, ResearchAgent, WritingAgent

# Initialize agents
coordinator = CoordinatorAgent()
research_agent = ResearchAgent()
writing_agent = WritingAgent()

# Coordinate a complex task
task = "Create a white paper on AI implementation in hospitals"
results = await coordinator.coordinate_task(
    task_description=task,
    agents=[research_agent, writing_agent],
    max_rounds=10
)
```

### Using Plugins

```python
from src.plugins import WebSearchPlugin, TaskManagementPlugin

# Web search
search_plugin = WebSearchPlugin()
results = search_plugin.search_web("machine learning trends", max_results=5)

# Task management
task_plugin = TaskManagementPlugin()
task_plugin.create_task(
    title="Research AI trends",
    description="Comprehensive analysis of current AI trends",
    priority="high",
    assigned_agent="ResearchAgent"
)
```

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

## 📁 Project Structure

```
python-agents-demo/
├── src/
│   ├── agents/          # Core agent implementations
│   ├── plugins/         # Plugin system
│   └── config/          # Configuration management
├── examples/            # Usage examples and demos
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
├── .env.example       # Environment configuration template
└── README.md          # This file
```

## 🔌 Extending the System

### Creating Custom Agents

```python
from src.agents import BaseAgent
from semantic_kernel import Kernel

class CustomAgent(BaseAgent):
    def __init__(self, name: str = "CustomAgent"):
        instructions = "Your custom agent instructions here"
        super().__init__(name=name, instructions=instructions)
    
    def _register_plugins(self, kernel: Kernel) -> None:
        # Register custom plugins
        pass
```

### Creating Custom Plugins

```python
from semantic_kernel.functions import kernel_function

class CustomPlugin:
    @kernel_function(
        name="custom_function",
        description="Description of your custom function"
    )
    def custom_function(self, input_param: str) -> str:
        # Your custom logic here
        return f"Processed: {input_param}"
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your Azure AI Foundry endpoint and API key
   - Check that your Azure credentials are properly configured
   - Ensure your Azure subscription has the necessary permissions

2. **Model Not Found**
   - Confirm your model deployment name matches what's configured in Azure
   - Verify the model is deployed and running in your Azure AI Foundry project

3. **Network Connectivity**
   - Check firewall settings and network connectivity to Azure services
   - Verify your endpoint URLs are correct and accessible

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're using Python 3.10 or later

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 🔒 Security Best Practices

- Use Azure Managed Identity in production environments
- Store sensitive credentials in Azure Key Vault
- Implement proper access controls and monitoring
- Regularly rotate API keys and secrets
- Use HTTPS for all communications

## 💰 Cost Management

- Monitor API usage through Azure portal
- Set up cost alerts and budgets
- Use appropriate model sizes for your use case
- Implement caching where appropriate
- Consider reserved capacity for predictable workloads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft Semantic Kernel team for the excellent framework
- Azure AI Foundry team for the powerful AI services
- The open-source community for inspiration and best practices

## 📞 Support

For questions and support:
- Check the [troubleshooting section](#-troubleshooting)
- Review the [examples](examples/) for usage patterns
- Consult the [Microsoft Semantic Kernel documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- Open an issue for bugs or feature requests