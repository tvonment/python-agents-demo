# 🤖 Multi-Agent System Demo

A sophisticated multi-agent system built with **Microsoft Semantic Kernel** and **Azure AI**, featuring intelligent agent orchestration and a modern React frontend. This demo showcases how multiple specialized AI agents can work together to handle complex tasks through intelligent routing and coordination.

![Multi-Agent System](https://img.shields.io/badge/Agents-5-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![React](https://img.shields.io/badge/React-18.2+-blue)
![Semantic Kernel](https://img.shields.io/badge/Semantic%20Kernel-1.32+-purple)
![Azure AI](https://img.shields.io/badge/Azure%20AI-Enabled-orange)

## 🌟 Features

### 🎯 **Intelligent Agent Orchestration**
- **Magentic Multi-Agent Coordination**: Advanced orchestration for complex multi-step tasks
- **Smart Routing**: Automatically determines the best agent(s) for each request
- **Multi-Topic Support**: Handles requests requiring multiple specialized agents
- **Loop Prevention**: Prevents infinite loops in email formatting workflows

### 🤖 **Specialized AI Agents**

| Agent | Purpose | Capabilities |
|-------|---------|-------------|
| 🎯 **Orchestrator** | Central coordination | Magentic orchestration, intelligent routing, multi-agent workflows |
| 📧 **Support Email** | Email formatting | Professional email responses (final step only - prevents loops) |
| 🌤️ **Weather** | Weather information | Real-time weather data for any location worldwide |
| 🧠 **AI Ethics** | Ethics & philosophy | AI ethics discussions, bias analysis, human-AI relationships |
| 💬 **QnA** | General inquiries | Customer support, FAQ responses, general information |

### 🎨 **Modern User Interface**
- **Responsive React Frontend**: Beautiful, mobile-friendly chat interface
- **Real-time Communication**: Instant messaging with typing indicators
- **Markdown Support**: Rich text formatting in agent responses
- **Pre-built Prompts**: Example prompts to explore different agent capabilities
- **Conversation Management**: Clear chat history, thread continuity

### 🔧 **Technical Features**
- **Magentic Orchestration**: Advanced multi-agent coordination for complex tasks
- **Async Processing**: Non-blocking agent operations with parallel execution
- **Loop Prevention**: Intelligent email formatting to prevent orchestration loops
- **Multi-Agent Synthesis**: Seamless integration of responses from multiple agents
- **Document Intelligence**: PDF processing with Azure Document Intelligence
- **Vector Search**: Semantic search capabilities for knowledge retrieval
- **Database Integration**: SQLite databases for document storage and retrieval
- **Error Handling**: Comprehensive error management and logging

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Azure AI Foundry account** with OpenAI deployment
- **Azure Document Intelligence** (optional, for AI Ethics agent)

### 1. Clone the Repository

```bash
git clone https://github.com/tvonment/python-agents-demo.git
cd python-agents-demo
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Required: Azure AI Foundry Configuration
AZURE_AI_FOUNDRY_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-4-deployment-name
AZURE_OPENAI_API_KEY=your-api-key

# Optional: Weather API (for Weather Agent)
WEATHER_API_KEY=your-openweather-api-key

# Optional: Azure Document Intelligence (for AI Ethics Agent)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-intel.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-doc-intel-key
```

### 3. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI backend
cd src
python main.py
```

The backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
# Install Node.js dependencies
cd frontend
npm install

# Start the React development server
npm start
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
python-agents-demo/
├── 📄 README.md              # This file
├── 📄 requirements.txt       # Python dependencies
├── 📁 src/                   # Backend source code
│   ├── 📄 main.py            # FastAPI application entry point
│   ├── 📁 agents/            # AI agent implementations
│   │   ├── 📄 orchestrator_agent.py     # Central orchestrator
│   │   ├── 📄 ai_ethics_agent.py        # AI ethics specialist
│   │   ├── 📄 qna_agent.py              # Q&A assistant
│   │   ├── 📄 support_email_agent.py    # Email support specialist
│   │   └── 📄 weather_agent.py          # Weather information
│   └── 📁 support/           # Support modules
│       ├── 📄 ai_ethics_db.py           # AI ethics document database
│       └── 📄 customer_support_db.py    # Customer support database
├── 📁 frontend/              # React frontend
│   ├── 📄 package.json       # Node.js dependencies
│   └── 📁 src/               # React source code
│       ├── 📄 App.js         # Main React component
│       └── 📄 App.css        # Styling
└── 📁 data/                  # Data storage
    ├── 📄 ai_ethics.db       # AI ethics documents database
    ├── 📄 customer_support.db # Customer support database
    └── 📁 files/             # Document files
```

## 🔧 Development

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send message to the multi-agent system |

### Example API Usage

```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "message": "What's the weather like in Stockholm?",
    "thread_id": None  # Optional: for conversation continuity
})

print(response.json())
# Output: {"response": "Weather information...", "thread_id": "abc123"}
```

## 🎮 Usage Examples

### 1. **Casual Conversation**
```
👤 User: "Hello! How are you doing today?"
🤖 Assistant: "Hello! I'm doing great, thank you for asking! I'm here and ready to help..."
```

### 2. **Weather Information**
```
👤 User: "What's the weather like in Stockholm?"
🤖 Assistant: "I'll check the current weather in Stockholm for you..."
```

### 3. **AI Ethics Discussion**
```
👤 User: "What are the ethical implications of AI dependency in healthcare?"
🤖 Assistant: "This is an excellent question about AI ethics in healthcare. Let me analyze this from multiple perspectives..."
```

### 4. **Multi-Topic Request**
```
👤 User: "What are the ethical implications of AI dependency and what's the weather in Stockholm?"
🤖 Assistant: "I'll analyze both the AI ethics aspects and get the current weather for you..."
```

### 5. **Complex Multi-Agent Analysis**
```
👤 User: "Please analyze AI governance across healthcare and automotive sectors, and examine how weather patterns might impact AI deployment strategies."
🤖 Assistant: "This is a comprehensive request requiring analysis from multiple perspectives..."
```

## 🛠️ Customization

### Adding New Agents

1. **Create Agent Class**: Create a new file in `src/agents/`
2. **Implement Agent Interface**: Follow the pattern of existing agents
3. **Register with Orchestrator**: Add to `orchestrator_agent.py`
4. **Update Frontend**: Add agent card in `frontend/src/App.js`

### Configuring Existing Agents

- **Prompts**: Modify agent system prompts in their respective files
- **Capabilities**: Extend agent functions and tool integrations
- **Data Sources**: Update database configurations in `src/support/`


## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft Semantic Kernel** team for the excellent multi-agent framework
- **Azure AI** services for powerful language models
- **React** team for the amazing frontend framework
- **FastAPI** for the high-performance backend framework

## 📞 Support

- **Issues**: Report bugs and feature requests in [GitHub Issues](https://github.com/tvonment/python-agents-demo/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/tvonment/python-agents-demo/discussions)
- **Documentation**: Check out the [Microsoft Semantic Kernel docs](https://learn.microsoft.com/en-us/semantic-kernel/)

---

**Built with ❤️ using Microsoft Semantic Kernel and Azure AI**
