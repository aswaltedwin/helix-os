from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
from app.utils.logger import setup_logging

# Initialize logging immediately to capture startup status
logger = setup_logging()

# Load .env file explicitly to ensure it's in the environment
load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://helixos:helixos_dev_password@localhost:5432/helixos"

    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM APIs
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Vector DB
    CHROMA_DB_URL: str = "http://localhost:8001"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

# Log API key status for visibility
if not settings.ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY is not set")
else:
    logger.info("ANTHROPIC_API_KEY is successfully loaded")

if not settings.OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is not set")
else:
    logger.info("OPENAI_API_KEY is successfully loaded")