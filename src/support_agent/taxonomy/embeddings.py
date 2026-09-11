"""
Semantic Embedding Module for Intent Discovery.

Provides batched, normalized sentence embeddings using SentenceTransformers,
with persistent disk caching to avoid redundant computation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Sequence, Union

import numpy as np

# Cache directory resolved relative to this module
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CACHE_DIR = PROJECT_ROOT / "generated" / "embeddings"
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    """
    Load a SentenceTransformer model instance.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise ImportError(
            "sentence-transformers is required for taxonomy embeddings. "
            "Please install it via: pip install sentence-transformers"
        ) from e

    model = SentenceTransformer(model_name)
    return model


def encode_texts(
    texts: Sequence[str],
    model_name: str = DEFAULT_MODEL_NAME,
    batch_size: int = 128,
    normalize_embeddings: bool = True,
    show_progress_bar: bool = True,
) -> np.ndarray:
    """
    Compute dense vector embeddings for a sequence of texts.

    Args:
        texts: List of strings to encode.
        model_name: HuggingFace model identifier.
        batch_size: Number of texts per forward pass.
        normalize_embeddings: If True, applies L2 normalization (cosine similarity = dot product).
        show_progress_bar: If True, prints progress.

    Returns:
        np.ndarray of shape (len(texts), embedding_dim) as float32.
    """
    model = get_embedding_model(model_name)
    clean_texts = [str(t) if str(t).strip() else " " for t in texts]

    embeddings = model.encode(
        clean_texts,
        batch_size=batch_size,
        show_progress_bar=show_progress_bar,
        normalize_embeddings=normalize_embeddings,
        convert_to_numpy=True,
    )
    return embeddings.astype(np.float32)


def get_or_compute_embeddings(
    texts: Sequence[str],
    ids: Optional[Sequence[str]] = None,
    cache_path: Optional[Union[str, Path]] = None,
    model_name: str = DEFAULT_MODEL_NAME,
    batch_size: int = 128,
    force_recompute: bool = False,
) -> np.ndarray:
    """
    Retrieve cached embeddings or compute and persist them if absent.

    Args:
        texts: Sequence of strings to encode.
        ids: Optional sequence of case/discovery IDs aligned with texts.
        cache_path: Path to .npy file. Defaults to generated/embeddings/intent_discovery_minilm.npy.
        model_name: Model identifier.
        batch_size: Batch size.
        force_recompute: If True, ignores existing cache.

    Returns:
        np.ndarray: Embedding matrix.
    """
    target_cache = Path(cache_path) if cache_path else (DEFAULT_CACHE_DIR / "intent_discovery_minilm.npy")

    if not force_recompute and target_cache.exists():
        embeddings = np.load(target_cache)
        if len(embeddings) == len(texts):
            return embeddings

    # Compute fresh embeddings
    embeddings = encode_texts(
        texts=texts,
        model_name=model_name,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    # Persist cache
    target_cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(target_cache, embeddings)

    # Optionally persist IDs alignment
    if ids is not None:
        ids_path = target_cache.with_suffix(".ids.json")
        with open(ids_path, "w", encoding="utf-8") as f:
            json.dump(list(ids), f)

    return embeddings
