"""
Configuration settings for the AI-powered book RAG system
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "Textbook Generation API"
    api_description: str = "API for generating textbooks using AI"
    api_version: str = "1.0.0"

    # Security Configuration
    secret_key: str

    # Database Configuration
    database_url: str
    neon_database_url: str = ""

    # Qdrant Vector Database Configuration
    qdrant_url: str
    qdrant_api_key: Optional[str] = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_https: str = "false"

    # Qdrant Collection Configuration
    qdrant_collection_name: str = "deploy_book_embeddings"
    qdrant_vector_size: int = 1536
    qdrant_distance: str = "Cosine"

    # AI Provider Keys
    openrouter_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"  # Default Groq model
    gemini_api_key: Optional[str] = None

    # Application Configuration
    debug: bool = True
    log_level: str = "INFO"
    book_url: str = "https://book-2-bay.vercel.app/"  # Default book URL

    # Source URLs
    source_urls: str = "https://book-2-bay.vercel.app/"
    # Context7 MCP Configuration
    context7_api_key: Optional[str] = None
    context7_base_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # Allow extra fields to prevent validation errors
        extra = "allow"


# Create a global settings instance
def get_settings():
    settings = Settings()

    # Validate required settings
    if not settings.secret_key:
        raise ValueError("SECRET_KEY environment variable must be set")
    if not settings.database_url:
        raise ValueError("DATABASE_URL environment variable must be set")
    if not settings.qdrant_url:
        raise ValueError("QDRANT_URL environment variable must be set")

    return settings


settings = get_settings()