import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    service_name: str = "knowdoc-ai-service"
    environment: str = "development"
    port: int = 8000
    host: str = "0.0.0.0"

    internal_service_key: str = "dev-internal-secret-change-in-production"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "knowdoc_vectors"
    postgres_user: str = "knowdoc_vector_user"
    postgres_password: str = "knowdoc_vector_password"
    vector_dimension: int = 1536

    embedding_provider: str = "mock"  # "mock", "openai", "local"
    embedding_model: str = "text-embedding-3-small"

    llm_provider: str = "mock"  # "mock", "openai"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: Optional[str] = None

    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = Settings()

