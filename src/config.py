"""
Configuration management using Pydantic Settings.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    voyage_api_key: Optional[str] = Field(None, env="VOYAGE_API_KEY")
    
    # Neo4j
    neo4j_uri: str = Field("bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field("neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")
    
    # Qdrant
    qdrant_host: str = Field("localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(6333, env="QDRANT_PORT")
    qdrant_api_key: Optional[str] = Field(None, env="QDRANT_API_KEY")
    
    # Models
    dense_embedding_model: str = Field("text-embedding-3-large", env="DENSE_EMBEDDING_MODEL")
    sparse_embedding_model: str = Field(
        "naver/splade-cocondenser-ensembledistil",
        env="SPARSE_EMBEDDING_MODEL"
    )
    colbert_model: str = Field("colbert-ir/colbertv2.0", env="COLBERT_MODEL")
    llm_model: str = Field("gpt-4o", env="LLM_MODEL")
    
    # Application
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_workers: int = Field(4, env="MAX_WORKERS")
    batch_size: int = Field(32, env="BATCH_SIZE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_yaml_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "r") as f:
        return yaml.safe_load(f)


# Global settings instance
settings = Settings()
