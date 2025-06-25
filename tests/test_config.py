"""
Tests for the configuration module.
"""
import pytest
import os
from unittest.mock import patch
from src.config.settings import AzureAISettings


class TestAzureAISettings:
    """Test cases for Azure AI settings."""
    
    def test_settings_initialization(self):
        """Test basic settings initialization."""
        with patch.dict(os.environ, {
            'AZURE_AI_INFERENCE_ENDPOINT': 'https://test.endpoint.com',
            'AZURE_AI_INFERENCE_API_KEY': 'test-key',
            'DEFAULT_MODEL_DEPLOYMENT_NAME': 'test-model'
        }):
            settings = AzureAISettings()
            
            assert settings.azure_ai_inference_endpoint == 'https://test.endpoint.com'
            assert settings.azure_ai_inference_api_key == 'test-key'
            assert settings.default_model_deployment_name == 'test-model'
    
    def test_default_values(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {
            'AZURE_AI_INFERENCE_ENDPOINT': 'https://test.endpoint.com'
        }, clear=True):
            settings = AzureAISettings()
            
            assert settings.default_model_deployment_name == 'gpt-4o-mini'
            assert settings.embedding_model_deployment_name == 'text-embedding-ada-002'
            assert settings.log_level == 'INFO'
            assert settings.max_tokens == 1000
            assert settings.temperature == 0.7
    
    def test_entra_id_detection(self):
        """Test Entra ID authentication detection."""
        # Test with all Entra ID credentials
        with patch.dict(os.environ, {
            'AZURE_AI_INFERENCE_ENDPOINT': 'https://test.endpoint.com',
            'AZURE_CLIENT_ID': 'test-client-id',
            'AZURE_CLIENT_SECRET': 'test-client-secret',
            'AZURE_TENANT_ID': 'test-tenant-id'
        }):
            settings = AzureAISettings()
            assert settings.use_entra_id is True
        
        # Test without Entra ID credentials
        with patch.dict(os.environ, {
            'AZURE_AI_INFERENCE_ENDPOINT': 'https://test.endpoint.com',
            'AZURE_AI_INFERENCE_API_KEY': 'test-key'
        }, clear=True):
            settings = AzureAISettings()
            assert settings.use_entra_id is False
    
    def test_required_fields_validation(self):
        """Test validation of required fields."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):  # Should raise validation error
                AzureAISettings()
    
    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case insensitive."""
        with patch.dict(os.environ, {
            'azure_ai_inference_endpoint': 'https://test.endpoint.com',
            'AZURE_AI_INFERENCE_API_KEY': 'test-key'
        }):
            settings = AzureAISettings()
            assert settings.azure_ai_inference_endpoint == 'https://test.endpoint.com'
            assert settings.azure_ai_inference_api_key == 'test-key'
