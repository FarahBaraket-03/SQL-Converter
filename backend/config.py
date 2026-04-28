"""Configuration management for the SQL conversion platform."""
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env file from backend directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AI Provider Configuration
    ai_provider: str = "blazeapi"
    
    # BlazeAPI Configuration (Primary)
    blazeapi_api_key: str = ""
    blazeapi_base_url: str = "https://blazeai.boxu.dev/api/"
    blazeapi_model: str = "fast-general"
    
    # Ollama Configuration (Fallback)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    
    # MySQL Configuration
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        # Look for .env file in the backend directory
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        extra = 'ignore'  # Ignore extra fields from .env


settings = Settings()
