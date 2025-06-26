# Multi-Agent System with Semantic Kernel

A modern multi-agent system built with Microsoft Semantic Kernel, featuring an orchestrator agent and specialized QnA agent, with a React frontend.

## 🏗️ Architecture

This solution demonstrates a clean multi-agent architecture using:

- **Orchestrator Agent**: Coordinates requests and manages agent collaboration
- **QnA Agent**: Handles question-answering with specialized system prompts
- **Semantic Kernel**: Microsoft's AI orchestration framework
- **Azure AI Foundry**: Model hosting and management (without hubs)
- **Managed Identity**: Secure authentication using DefaultAzureCredential
- **React Frontend**: Modern web interface for interaction

## 🚀 Features

- ✅ Multi-agent orchestration with Semantic Kernel
- ✅ Azure AI Foundry integration (new resource model)
- ✅ Managed Identity authentication (no API keys)
- ✅ Modern React frontend with real-time chat
- ✅ Conversation threading and history
- ✅ Professional UI with loading states
- ✅ FastAPI backend with async support

## 📋 Prerequisites

1. **Azure AI Foundry Resource** (the new model without hubs)
2. **Azure OpenAI model deployment** (e.g., gpt-4o)
3. **Managed Identity** configured for your environment
4. **Python 3.8+** and **Node.js 16+**

## ⚙️ Setup

### 1. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Update `.env` with your Azure AI Foundry details:

```env
# Azure AI Foundry Resource Configuration
AZURE_AI_FOUNDRY_ENDPOINT=https://your-foundry-resource.services.ai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 2. Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

Install Node.js dependencies:

```bash
cd frontend
npm install
```

## 🚦 Running the Application

### Start the Backend (Terminal 1)

```bash
cd src
python main.py
```

The FastAPI server will start on `http://localhost:8000`

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm start
```

The React app will start on `http://localhost:3000`

## 🔧 Authentication

This project uses **Azure Managed Identity** for secure authentication:

- **Development**: Uses `DefaultAzureCredential` which tries various auth methods
- **Production**: Will use the managed identity assigned to your Azure resource
- **No API keys required** - fully managed authentication

### Authentication Flow

1. `DefaultAzureCredential` attempts authentication in this order:
   - Environment variables
   - Managed Identity
   - Azure CLI credentials
   - Visual Studio credentials
   - Other available credential providers

## 📁 Project Structure

```
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── qna_agent.py          # QnA specialist agent
│   │   └── orchestrator_agent.py # Main orchestrator
│   ├── main.py                   # FastAPI application
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── App.js               # Main React component
│   │   ├── App.css              # Styling
│   │   ├── index.js             # React entry point
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   └── package.json
├── requirements.txt              # Python dependencies
├── .env.example                 # Environment template
└── README.md
```

## 🤖 Agent Details

### Orchestrator Agent
- **Role**: Request coordination and agent management
- **Capabilities**: Analyzes requests, delegates to specialists, provides comprehensive responses
- **Service ID**: `orchestrator-service`

### QnA Agent
- **Role**: Question answering and information retrieval
- **Capabilities**: Handles general questions with specialized prompts
- **Service ID**: `qna-service`

## 🔗 API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /chat` - Chat with agents

### Chat API

```json
POST /chat
{
  "message": "Your question here",
  "thread_id": "optional-thread-id"
}

Response:
{
  "response": "Agent response",
  "thread_id": "thread-identifier"
}
```

## 🎯 Usage Examples

1. **Simple Questions**: Automatically routed to QnA Agent
   - "What is machine learning?"
   - "How does Azure work?"

2. **Complex Requests**: Handled by Orchestrator with agent coordination
   - Multi-step workflows
   - Complex analysis requests

## 🔍 Monitoring and Debugging

- Check FastAPI logs in Terminal 1
- Use browser dev tools for frontend debugging
- Health endpoint: `http://localhost:8000/health`

## 🚀 Future Enhancements

- Additional specialized agents (Research, Writing, etc.)
- Advanced orchestration patterns (Sequential, Concurrent)
- Persistent storage for conversation history
- Enhanced UI with agent visualization
- Plugin system for extensible capabilities

## 📚 Learn More

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure Managed Identity](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/)

## 🤝 Contributing

This is a demonstration project showcasing modern multi-agent architecture patterns with Microsoft Semantic Kernel and Azure AI services.
