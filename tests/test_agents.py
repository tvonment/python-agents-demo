"""
Tests for agent classes.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from semantic_kernel.contents import ChatMessageContent, ChatHistory

from src.agents import BaseAgent, ResearchAgent, WritingAgent, CoordinatorAgent


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    def test_agent_initialization(self, mock_settings):
        """Test agent initialization."""
        agent = BaseAgent(
            name="TestAgent",
            instructions="Test instructions",
            description="Test description"
        )
        
        assert agent.name == "TestAgent"
        assert agent.instructions == "Test instructions"
        assert agent.description == "Test description"
        assert agent.model_deployment_name == mock_settings.default_model_deployment_name
    
    @patch('semantic_kernel.Kernel')
    @patch('semantic_kernel.connectors.ai.azure_ai_inference.AzureAIInferenceChatCompletion')
    def test_kernel_creation(self, mock_chat_service, mock_kernel_class, mock_settings):
        """Test kernel creation with AI services."""
        mock_kernel = Mock()
        mock_kernel_class.return_value = mock_kernel
        
        class TestAgent(BaseAgent):
            def _register_plugins(self, kernel):
                pass
        
        agent = TestAgent("TestAgent", "Test instructions")
        kernel = agent.kernel
        
        # Verify kernel was created and service was added
        mock_kernel_class.assert_called_once()
        mock_chat_service.assert_called_once()
        mock_kernel.add_service.assert_called_once()
    
    @patch('semantic_kernel.agents.ChatCompletionAgent')
    def test_agent_creation(self, mock_agent_class, mock_kernel):
        """Test chat completion agent creation."""
        class TestAgent(BaseAgent):
            def _register_plugins(self, kernel):
                pass
        
        agent = TestAgent("TestAgent", "Test instructions")
        agent._kernel = mock_kernel
        
        chat_agent = agent.agent
        
        mock_agent_class.assert_called_once_with(
            kernel=mock_kernel,
            name="TestAgent",
            instructions="Test instructions",
            description="Agent: TestAgent"
        )
    
    @pytest.mark.asyncio
    async def test_invoke_method(self, mock_settings):
        """Test agent invoke method."""
        class TestAgent(BaseAgent):
            def _register_plugins(self, kernel):
                pass
        
        agent = TestAgent("TestAgent", "Test instructions")
        
        # Mock the agent's invoke method
        mock_response = Mock()
        mock_response.content = "Test response"
        agent._agent = Mock()
        agent._agent.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent.invoke("Test message")
        
        assert result == mock_response
        agent._agent.invoke.assert_called_once()


class TestResearchAgent:
    """Test cases for ResearchAgent."""
    
    def test_research_agent_initialization(self, mock_settings):
        """Test research agent initialization."""
        agent = ResearchAgent()
        
        assert agent.name == "ResearchAgent"
        assert "research" in agent.instructions.lower()
        assert "Research Agent" in agent.description
    
    @pytest.mark.asyncio
    async def test_conduct_research(self, mock_settings):
        """Test research conducting functionality."""
        agent = ResearchAgent()
        
        # Mock the agent's invoke method
        mock_response = Mock()
        mock_response.content = "Research findings on AI in healthcare..."
        agent._agent = Mock()
        agent._agent.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent.conduct_research("AI in healthcare")
        
        assert result == "Research findings on AI in healthcare..."
        agent._agent.invoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_data(self, mock_settings):
        """Test data analysis functionality."""
        agent = ResearchAgent()
        
        # Mock the agent's invoke method
        mock_response = Mock()
        mock_response.content = "Data analysis results..."
        agent._agent = Mock()
        agent._agent.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent.analyze_data("Patient data", "statistical")
        
        assert result == "Data analysis results..."
        agent._agent.invoke.assert_called_once()


class TestWritingAgent:
    """Test cases for WritingAgent."""
    
    def test_writing_agent_initialization(self, mock_settings):
        """Test writing agent initialization."""
        agent = WritingAgent()
        
        assert agent.name == "WritingAgent"
        assert "writing" in agent.instructions.lower()
        assert "Writing Agent" in agent.description
    
    @pytest.mark.asyncio
    async def test_write_article(self, mock_settings):
        """Test article writing functionality."""
        agent = WritingAgent()
        
        # Mock the agent's invoke method
        mock_response = Mock()
        mock_response.content = "AI in Healthcare: A Comprehensive Analysis..."
        agent._agent = Mock()
        agent._agent.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent.write_article(
            topic="AI in Healthcare",
            audience="professionals",
            style="informative"
        )
        
        assert "AI in Healthcare" in result
        agent._agent.invoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_edit_content(self, mock_settings):
        """Test content editing functionality."""
        agent = WritingAgent()
        
        # Mock the agent's invoke method
        mock_response = Mock()
        mock_response.content = "Edited content with improvements..."
        agent._agent = Mock()
        agent._agent.invoke = AsyncMock(return_value=mock_response)
        
        result = await agent.edit_content("Original content", "grammar")
        
        assert "Edited content" in result
        agent._agent.invoke.assert_called_once()


class TestCoordinatorAgent:
    """Test cases for CoordinatorAgent."""
    
    def test_coordinator_agent_initialization(self, mock_settings):
        """Test coordinator agent initialization."""
        agent = CoordinatorAgent()
        
        assert agent.name == "CoordinatorAgent"
        assert "coordinator" in agent.instructions.lower()
        assert "Coordinator Agent" in agent.description
        assert len(agent.available_agents) == 0
        assert agent.group_chat is None
    
    def test_register_agent(self, mock_settings):
        """Test agent registration."""
        coordinator = CoordinatorAgent()
        research_agent = ResearchAgent()
        
        coordinator.register_agent(research_agent)
        
        assert "ResearchAgent" in coordinator.available_agents
        assert coordinator.available_agents["ResearchAgent"] == research_agent
    
    @pytest.mark.asyncio
    async def test_analyze_task_requirements(self, mock_settings):
        """Test task analysis functionality."""
        coordinator = CoordinatorAgent()
        
        # Mock the agent's invoke method
        mock_response = Mock()
        mock_response.content = "Task analysis: Complex task requiring research and writing..."
        coordinator._agent = Mock()
        coordinator._agent.invoke = AsyncMock(return_value=mock_response)
        
        result = await coordinator.analyze_task_requirements("Create a report")
        
        assert "analysis" in result
        assert "Task analysis" in result["analysis"]
        coordinator._agent.invoke.assert_called_once()
