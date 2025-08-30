from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "InfoU Backend API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./data/infou.db"
    
    # LLM Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # LLM Configuration
    default_llm_provider: str = "openai"
    max_tokens_per_request: int = 4000
    llm_temperature: float = 0.7
    
    # API Configuration  
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    api_rate_limit: int = 100  # requests per minute
    
    # Session Configuration
    session_expires_days: int = 30
    max_articles_per_session: int = 20
    
    # WebSocket
    websocket_connection_timeout: int = 300  # seconds
    
    # Development
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()