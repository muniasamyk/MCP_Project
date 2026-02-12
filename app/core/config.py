from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "MCP API"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # --- Security ---
    # Optional API key for simple auth
    API_KEY: Optional[str] = None 

    # --- Database ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "mcp_db"

    # --- LLM Provider ---
    # Options: 'mock', 'ollama', 'openai'
    MCP_LLM_PROVIDER: str = "mock"
    MCP_LLM_MODEL: str = "mistral"
    
    # Provider-specific settings
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_TIMEOUT_SECONDS: int = 180
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
