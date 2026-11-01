import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "knowdoc-ai-service"
    environment: str = "development"
    port: int = 8000
    host: str = "0.0.0.0"

    # Internal microservice security
    internal_service_key: str = "dev-internal-secret-change-in-production"

    # PostgreSQL / pgvector settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "knowdoc_vectors"
    postgres_user: str = "knowdoc_vector_user"
    postgres_password: str = "knowdoc_vector_password"
    vector_dimension: int = 1536

    # Ingestion & Chunking parameters
    default_chunk_size: int = 800
    default_chunk_overlap: int = 150
    min_chunk_length: int = 30
    max_pdf_pages: int = 500

    # Model & Provider configuration
    embedding_provider: str = "mock"  # "mock", "openai", "local"
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 64

    llm_provider: str = "mock"  # "mock", "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1500
    llm_timeout_seconds: float = 45.0
    openai_api_key: Optional[str] = None

    # Agent execution bounds
    agent_max_iterations: int = 4
    agent_tool_timeout_seconds: float = 15.0

    # RAG parameters
    default_top_k: int = 5
    default_similarity_threshold: float = 0.20

    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = Settings()
