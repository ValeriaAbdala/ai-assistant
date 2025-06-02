import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-pro"
    
    # Database
    database_url: str = "sqlite:///./pm_assistant.db"
    
    # RAG Configuration
    embeddings_model: str = "all-MiniLM-L6-v2"
    vector_db_path: str = "./data/embeddings/chroma_db"
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_chunks_retrieval: int = 5
    
    # Analytics
    max_context_length: int = 4000
    cache_duration_hours: int = 1
    
    class Config:
        env_file = ".env"

settings = Settings()