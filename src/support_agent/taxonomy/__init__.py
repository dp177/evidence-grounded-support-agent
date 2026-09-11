"""Taxonomy and intent discovery package."""

from support_agent.taxonomy.embeddings import (
    DEFAULT_CACHE_DIR,
    DEFAULT_MODEL_NAME,
    encode_texts,
    get_embedding_model,
    get_or_compute_embeddings,
)

__all__ = [
    "DEFAULT_MODEL_NAME",
    "DEFAULT_CACHE_DIR",
    "get_embedding_model",
    "encode_texts",
    "get_or_compute_embeddings",
]
