"""
Configuration settings for the multi-agent solution.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureAISettings(BaseSettings):
    """Azure AI Foundry configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Azure AI Foundry Project Configuration
    azure_ai_foundry_project_endpoint: Optional[str] = Field(
        None,
        description="Azure AI Foundry project endpoint URL"
    )
    azure_ai_foundry_api_key: Optional[str] = Field(
        None,
        description="Azure AI Foundry project API key"
    )
    
    # Azure AI Inference Configuration (for specific model endpoints)
    azure_ai_inference_endpoint: Optional[str] = Field(
        None,
        description="Azure AI Foundry model endpoint URL"
    )
    azure_ai_inference_api_key: Optional[str] = Field(
        None,
        description="Azure AI Foundry model API key"
    )
    
    # Azure AI Agent Configuration
    azure_ai_agent_endpoint: Optional[str] = Field(
        None,
        description="Azure AI Foundry project endpoint for agents"
    )
    azure_ai_agent_model_deployment_name: Optional[str] = Field(
        None,
        description="Model deployment name for Azure AI agents"
    )
    
    # Azure Entra ID Configuration (optional)
    azure_client_id: Optional[str] = Field(None, description="Azure Client ID")
    azure_client_secret: Optional[str] = Field(None, description="Azure Client Secret")
    azure_tenant_id: Optional[str] = Field(None, description="Azure Tenant ID")
    
    # Model Configuration
    default_model_deployment_name: str = Field(
        default="gpt-4o-mini",
        description="Default model deployment name"
    )
    embedding_model_deployment_name: str = Field(
        default="text-embedding-ada-002",
        description="Embedding model deployment name"
    )
    
    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    max_tokens: int = Field(default=1000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.7, description="Temperature for model responses")
    
    @property
    def use_entra_id(self) -> bool:
        """Check if Entra ID authentication should be used."""
        return all([
            self.azure_client_id,
            self.azure_client_secret,
            self.azure_tenant_id
        ])
    
    @property
    def primary_endpoint(self) -> str:
        """Get the primary endpoint to use for AI services."""
        # Prefer specific model endpoint, fall back to project endpoint
        return (
            self.azure_ai_inference_endpoint or 
            self.azure_ai_foundry_project_endpoint or
            ""
        )
    
    @property
    def primary_api_key(self) -> str:
        """Get the primary API key to use for AI services."""
        # Prefer specific model key, fall back to project key
        return (
            self.azure_ai_inference_api_key or 
            self.azure_ai_foundry_api_key or
            ""
        )
    
    @property
    def agent_endpoint(self) -> str:
        """Get the endpoint for Azure AI Agents."""
        return (
            self.azure_ai_agent_endpoint or
            self.azure_ai_foundry_project_endpoint or
            ""
        )


# Global settings instance
settings = AzureAISettings()
