"""
Configuration settings for Bridged Demo application.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # API Keys
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Pinecone Configuration
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "bridged-demo-articles")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    
    # LLM Configuration
    DEFAULT_LLM_MODEL: str = "deepseek/deepseek-r1-0528:free"
    FALLBACK_MODELS: List[str] = [
        "deepseek/deepseek-r1-0528:free",
        "sarvamai/sarvam-m:free", 
        "google/gemma-3n-e4b-it:free",
        "qwen/qwen3-4b:free",
        "qwen/qwen3-8b:free",
        "deepseek/deepseek-v3-base:free",
        "mistralai/mistral-small-3.1-24b-instruct:free"
    ]
    
    # Application Configuration
    APP_NAME: str = "Bridged Demo - NL to Pinecone Query Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 1536
    
    # Search Configuration
    DEFAULT_TOP_K: int = 10
    MAX_TOP_K: int = 50
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present."""
        required_keys = [
            cls.PINECONE_API_KEY,
            cls.PINECONE_INDEX_NAME
        ]
        
        missing_keys = [key for key in required_keys if not key]
        
        if missing_keys:
            print(f"Missing required configuration: {missing_keys}")
            return False
        
        return True

# Global settings instance
settings = Settings()
