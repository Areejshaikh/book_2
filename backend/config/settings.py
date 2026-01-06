"""
Configuration management for the URL ingestion pipeline
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineConfig:
    """Configuration for the URL ingestion pipeline"""

    # Required fields (no defaults)
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str

    # Fields with defaults
    embed_model: str = "embed-english-v2.0"
    collection_name: str = "textbook_vectors"

    # Processing settings
    chunk_size: int = 512
    overlap: float = 0.2
    batch_size: int = 10
    max_pages: int = 1000

    # Network settings
    request_timeout: int = 60
    rate_limit_delay: float = 0.5
def load_config_from_env() -> PipelineConfig:
    """Load configuration from environment variables"""

    # Required environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not cohere_api_key:
        raise ValueError("COHERE_API_KEY environment variable not set")

    if not qdrant_url:
        raise ValueError("QDRANT_URL environment variable not set")

    if not qdrant_api_key:
        raise ValueError("QDRANT_API_KEY environment variable not set")

    # Optional environment variables with defaults
    embed_model = os.getenv("EMBED_MODEL", "embed-english-v2.0")
    collection_name = os.getenv("COLLECTION_NAME", "book_embeddings")

    chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
    overlap = float(os.getenv("OVERLAP", "0.2"))
    batch_size = int(os.getenv("BATCH_SIZE", "10"))
    max_pages = int(os.getenv("MAX_PAGES", "1000"))

    request_timeout = int(os.getenv("REQUEST_TIMEOUT", "60"))
    rate_limit_delay = float(os.getenv("RATE_LIMIT_DELAY", "0.5"))

    return PipelineConfig(
        cohere_api_key=cohere_api_key,
        embed_model=embed_model,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        collection_name=collection_name,
        chunk_size=chunk_size,
        overlap=overlap,
        batch_size=batch_size,
        max_pages=max_pages,
        request_timeout=request_timeout,
        rate_limit_delay=rate_limit_delay
    )