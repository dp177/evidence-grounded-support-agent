"""Embedding generation and persistent cache management for historical retrieval.

Uses SentenceTransformer ('all-MiniLM-L6-v2' by default) with L2 normalization.
Provides robust disk caching with SHA-256 corpus hash validation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd
import yaml

try:
    import torch
    from sentence_transformers import SentenceTransformer
except ImportError:
    torch = None
    SentenceTransformer = None

logger = logging.getLogger(__name__)


def compute_corpus_hash(texts: Iterable[str]) -> str:
    """Compute deterministic SHA-256 hash over an iterable of text strings."""
    hasher = hashlib.sha256()
    for text in texts:
        if text is not None:
            hasher.update(str(text).encode("utf-8"))
        else:
            hasher.update(b"")
    return hasher.hexdigest()


class EmbeddingEngine:
    """Manages embedding generation, normalization, and persistent caching."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
        normalize: bool = True,
        batch_size: int = 256,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.dimension = dimension
        self.normalize = normalize
        self.batch_size = batch_size
        self.device = device
        self._model: Optional[Any] = None

    @classmethod
    def from_config(
        cls,
        config_path: Union[str, Path] = "configs/retrieval.yaml",
    ) -> EmbeddingEngine:
        """Initialize EmbeddingEngine from YAML configuration."""
        config_file = Path(config_path)
        cfg: Dict[str, Any] = {}
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

        emb_cfg = cfg.get("embedding", {})
        return cls(
            model_name=emb_cfg.get("model", "all-MiniLM-L6-v2"),
            dimension=emb_cfg.get("dimension", 384),
            normalize=emb_cfg.get("normalize", True),
            batch_size=emb_cfg.get("batch_size", 256),
        )

    @property
    def model(self) -> Any:
        """Lazy load the SentenceTransformer model."""
        if self._model is None:
            if SentenceTransformer is None:
                raise ImportError(
                    "sentence-transformers is not installed. Install with `pip install sentence-transformers`."
                )
            logger.info("Loading embedding model: %s", self.model_name)
            try:
                self._model = SentenceTransformer(
                    self.model_name,
                    device=self.device,
                    model_kwargs={"local_files_only": True},
                )
            except Exception:
                self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """Encode texts into numpy float32 embeddings."""
        if isinstance(texts, str):
            texts = [texts]

        bs = batch_size or self.batch_size
        embeddings = self.model.encode(
            texts,
            batch_size=bs,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=self.normalize,
            convert_to_numpy=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def encode_query(self, query_text: str) -> np.ndarray:
        """Encode a single query string into a 1D normalized float32 vector."""
        embs = self.encode([query_text], show_progress_bar=False)
        return embs[0]

    def get_or_create_embeddings(
        self,
        df: pd.DataFrame,
        text_column: str = "embedding_text",
        cache_dir: Union[str, Path] = "artifacts/retrieval/embeddings",
        source_path: str = "data/processed/retrieval_documents.parquet",
        preprocessing_version: str = "v1",
        force_recompute: bool = False,
        show_progress_bar: bool = True,
    ) -> np.ndarray:
        """Load cached embeddings if manifest & hash match; otherwise compute and persist."""
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        embeddings_file = cache_path / "embeddings.npy"
        manifest_file = cache_path / "manifest.json"

        expected_count = len(df)
        computed_hash = compute_corpus_hash(df[text_column])

        # Validate existing cache
        if not force_recompute and embeddings_file.exists() and manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                if (
                    manifest.get("source_path") == source_path
                    and manifest.get("row_count") == expected_count
                    and manifest.get("corpus_hash") == computed_hash
                    and manifest.get("embedding_model") == self.model_name
                    and manifest.get("embedding_dimension") == self.dimension
                ):
                    logger.info("Loading cached embeddings from %s", embeddings_file)
                    embeddings = np.load(embeddings_file)
                    if embeddings.shape == (expected_count, self.dimension):
                        logger.info(
                            "Loaded %d cached embeddings with shape %s (verified SHA-256 match)",
                            len(embeddings),
                            embeddings.shape,
                        )
                        return embeddings
                    else:
                        logger.warning(
                            "Cached embeddings shape %s does not match expected (%d, %d). Recomputing.",
                            embeddings.shape,
                            expected_count,
                            self.dimension,
                        )
                else:
                    logger.info("Manifest mismatch or corpus hash changed. Recomputing embeddings.")
            except Exception as e:
                logger.warning("Failed to validate embedding cache (%s). Recomputing.", e)

        # Compute embeddings in chunks to enable checkpointing and progress resumption
        chunk_size = 5000
        num_chunks = (expected_count + chunk_size - 1) // chunk_size
        chunks_dir = cache_path / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Computing embeddings for %d documents in %d chunks of %d using model '%s' (batch_size=%d)...",
            expected_count,
            num_chunks,
            chunk_size,
            self.model_name,
            self.batch_size,
        )

        texts = df[text_column].tolist()
        all_chunk_embeddings = []

        for chunk_idx in range(num_chunks):
            start_i = chunk_idx * chunk_size
            end_i = min(start_i + chunk_size, expected_count)
            chunk_file = chunks_dir / f"chunk_{chunk_idx:04d}_{start_i}_{end_i}.npy"

            if chunk_file.exists():
                logger.info("Loaded checkpoint for chunk %d/%d (%d..%d)", chunk_idx + 1, num_chunks, start_i, end_i)
                chunk_embs = np.load(chunk_file)
            else:
                import time
                t0 = time.time()
                chunk_texts = texts[start_i:end_i]
                chunk_embs = self.encode(
                    chunk_texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                )
                np.save(chunk_file, chunk_embs)
                elapsed = time.time() - t0
                rate = len(chunk_texts) / max(elapsed, 0.001)
                logger.info(
                    "Computed chunk %d/%d (%d..%d, %.1f%%) in %.1fs (%.1f texts/s)",
                    chunk_idx + 1,
                    num_chunks,
                    start_i,
                    end_i,
                    100.0 * end_i / expected_count,
                    elapsed,
                    rate,
                )
            all_chunk_embeddings.append(chunk_embs)

        embeddings = np.vstack(all_chunk_embeddings)

        # Save consolidated embeddings and manifest
        np.save(embeddings_file, embeddings)

        # Clean up chunk files after successful consolidation
        for chunk_idx in range(num_chunks):
            start_i = chunk_idx * chunk_size
            end_i = min(start_i + chunk_size, expected_count)
            chunk_file = chunks_dir / f"chunk_{chunk_idx:04d}_{start_i}_{end_i}.npy"
            if chunk_file.exists():
                try:
                    chunk_file.unlink()
                except Exception:
                    pass
        try:
            chunks_dir.rmdir()
        except Exception:
            pass
        manifest_data = {
            "source_path": source_path,
            "row_count": expected_count,
            "corpus_hash": computed_hash,
            "embedding_model": self.model_name,
            "embedding_dimension": self.dimension,
            "preprocessing_version": preprocessing_version,
            "normalized": self.normalize,
        }
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        logger.info("Successfully saved embeddings to %s and manifest to %s", embeddings_file, manifest_file)
        return embeddings
