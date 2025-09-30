# config.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os

class BaseConfig(BaseModel):
    """Base configuration class for all services"""
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

class AzureConfig(BaseConfig):
    """Azure-specific configuration"""
    azure_deployment: str = Field(default=os.getenv("AZURE_DEPLOYMENT", "o4-mini"))
    model: str = Field(default=os.getenv("AZURE_MODEL", "o4-mini"))
    api_version: str = Field(default=os.getenv("AZURE_API_VERSION", "2024-12-01-preview"))
    azure_endpoint: str = Field(default=os.getenv("AZURE_ENDPOINT"))
    api_key: str = Field(default=os.getenv("AZURE_API_KEY"))

class GroqConfig(BaseConfig):
    """Groq-specific configuration"""
    model_name: str = Field(default=os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-20b"))
    api_base: str = Field(default=os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1"))
    api_key: str = Field(default=os.getenv("GROQ_API_KEY"))

class DatabaseConfig(BaseConfig):
    """Database configuration"""
    connection_string: str = Field(default=os.getenv("DATABASE_URL"))
    database_name: str = Field(default=os.getenv("DATABASE_NAME", "financial_assistant"))

class FileStorageConfig(BaseConfig):
    """File storage configuration"""
    form_data_path: str = Field(default=os.getenv("FORM_DATA_PATH", "form_sample.json"))
    state_data_path: str = Field(default=os.getenv("STATE_DATA_PATH", "team_state.json"))