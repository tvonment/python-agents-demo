"""
Test configuration for the multi-agent solution.
"""
import pytest
import asyncio
import os
from unittest.mock import Mock, patch

# Test configuration
TEST_CONFIG = {
    "azure_ai_inference_endpoint": "https://test-endpoint.inference.ml.azure.com",
    "azure_ai_inference_api_key": "test-api-key",
    "default_model_deployment_name": "test-model",
    "temperature": 0.5,
    "max_tokens": 500
}


@pytest.fixture
def mock_azure_credentials():
    """Mock Azure credentials for testing."""
    with patch('azure.identity.DefaultAzureCredential') as mock_cred:
        mock_cred.return_value = Mock()
        yield mock_cred


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('src.config.settings') as mock_settings:
        for key, value in TEST_CONFIG.items():
            setattr(mock_settings, key, value)
        mock_settings.use_entra_id = False
        yield mock_settings


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_chat_completion_service():
    """Mock chat completion service for testing."""
    with patch('semantic_kernel.connectors.ai.azure_ai_inference.AzureAIInferenceChatCompletion') as mock_service:
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_kernel():
    """Mock kernel for testing."""
    with patch('semantic_kernel.Kernel') as mock_kernel_class:
        mock_kernel = Mock()
        mock_kernel_class.return_value = mock_kernel
        yield mock_kernel
