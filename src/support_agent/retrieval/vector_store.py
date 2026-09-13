"""Vector store backend abstraction and Qdrant implementation.

Supports both local-first (persistent on-disk) and cloud-ready modes
without rewriting retrieval logic.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
import numpy as np

try:
    from qdrant_client import QdrantClient, models
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None
    models = None
    Distance = None
    VectorParams = None
    PointStruct = None


class VectorStore(ABC):
    """Abstract base class for vector store backends."""

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        distance: str = "cosine",
    ) -> None:
        """Create a collection with specified dimension and distance metric."""
        pass

    @abstractmethod
    def upsert(
        self,
        collection_name: str,
        points: List[Any],
    ) -> int:
        """Insert or update points in collection. Returns number of points upserted."""
        pass

    @abstractmethod
    def search(
        self,
        collection_name: str,
        query_vector: Union[List[float], np.ndarray],
        top_k: int = 30,
        filters: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Search for top_k nearest neighbors."""
        pass

    @abstractmethod
    def count(self, collection_name: str) -> int:
        """Return total point count in collection."""
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Return collection metadata and status."""
        pass


class QdrantVectorStore(VectorStore):
    """Qdrant vector store supporting both local persistent storage and cloud."""

    def __init__(
        self,
        mode: str = "local",
        local_path: Optional[str] = None,
        cloud_url: Optional[str] = None,
        api_key_env: str = "QDRANT_API_KEY",
        api_key: Optional[str] = None,
        client: Optional[Any] = None,
    ):
        if QdrantClient is None:
            raise ImportError(
                "qdrant-client is not installed. Install it with `pip install qdrant-client`."
            )

        # Environment variable overrides
        env_mode = os.environ.get("QDRANT_MODE")
        if env_mode:
            mode = env_mode.strip().lower()

        self.mode = mode.lower()

        if client is not None:
            self.client = client
            return

        if self.mode == "local":
            path_val = os.environ.get("QDRANT_PATH") or local_path or "artifacts/retrieval/qdrant"
            self.local_path = Path(path_val)
            self.local_path.mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=str(self.local_path))
        elif self.mode == "cloud":
            url_val = os.environ.get("QDRANT_URL") or cloud_url
            if not url_val:
                raise ValueError(
                    "Qdrant cloud mode requires a valid URL. "
                    "Set QDRANT_URL environment variable or configure vector_store.cloud.url."
                )
            key_val = api_key or os.environ.get(api_key_env)
            if not key_val:
                raise ValueError(
                    f"Qdrant cloud mode requires an API key in environment variable '{api_key_env}'. "
                    "API keys must never be hardcoded or checked into configuration files."
                )
            self.client = QdrantClient(url=url_val, api_key=key_val)
        else:
            raise ValueError(
                f"Unsupported Qdrant mode: '{self.mode}'. Supported modes are 'local' and 'cloud'."
            )

    @classmethod
    def from_config(
        cls,
        config_path: Union[str, Path] = "configs/retrieval.yaml",
        mode_override: Optional[str] = None,
    ) -> QdrantVectorStore:
        """Initialize QdrantVectorStore from YAML configuration with environment overrides."""
        config_file = Path(config_path)
        cfg: Dict[str, Any] = {}
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

        vs_cfg = cfg.get("vector_store", {})
        mode = mode_override or vs_cfg.get("mode", "local")
        local_cfg = vs_cfg.get("local", {})
        cloud_cfg = vs_cfg.get("cloud", {})

        return cls(
            mode=mode,
            local_path=local_cfg.get("path", "artifacts/retrieval/qdrant"),
            cloud_url=cloud_cfg.get("url"),
            api_key_env=cloud_cfg.get("api_key_env", "QDRANT_API_KEY"),
        )

    def _map_distance(self, distance: str) -> Distance:
        dist_lower = distance.lower()
        if dist_lower in ("cosine", "cos"):
            return Distance.COSINE
        elif dist_lower in ("dot", "ip", "inner_product"):
            return Distance.DOT
        elif dist_lower in ("euclid", "euclidean", "l2"):
            return Distance.EUCLID
        raise ValueError(f"Unsupported distance metric: '{distance}'. Use 'cosine', 'dot', or 'euclid'.")

    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        distance: str = "cosine",
    ) -> None:
        """Create or recreate collection."""
        dist_enum = self._map_distance(distance)
        # Check if collection already exists
        collections_response = self.client.get_collections()
        existing_names = [c.name for c in collections_response.collections]
        if collection_name in existing_names:
            # Drop existing collection to re-create clean collection
            self.client.delete_collection(collection_name)

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dimension, distance=dist_enum),
        )

    def upsert(
        self,
        collection_name: str,
        points: List[Any],
    ) -> int:
        """Upsert a list of points (PointStruct or dict) into the collection."""
        if not points:
            return 0

        # Convert dictionaries to PointStruct if necessary
        formatted_points = []
        for p in points:
            if isinstance(p, PointStruct):
                formatted_points.append(p)
            elif isinstance(p, dict):
                formatted_points.append(
                    PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p.get("payload", {}),
                    )
                )
            else:
                formatted_points.append(p)

        self.client.upsert(
            collection_name=collection_name,
            points=formatted_points,
            wait=True,
        )
        return len(formatted_points)

    def search(
        self,
        collection_name: str,
        query_vector: Union[List[float], np.ndarray],
        top_k: int = 30,
        filters: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Search top_k nearest neighbors by query vector."""
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()

        res = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=filters,
            with_payload=True,
            with_vectors=False,
        )

        results = []
        for pt in res.points:
            results.append({
                "id": pt.id,
                "score": float(pt.score),
                "payload": pt.payload or {},
            })
        return results

    def count(self, collection_name: str) -> int:
        """Return total point count in collection."""
        info = self.client.count(collection_name=collection_name, exact=True)
        return info.count

    def delete_collection(self, collection_name: str) -> None:
        """Delete collection by name."""
        self.client.delete_collection(collection_name=collection_name)

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Return collection information."""
        info = self.client.get_collection(collection_name=collection_name)
        params = info.config.params.vectors
        size = params.size if hasattr(params, "size") else None
        distance = str(params.distance) if hasattr(params, "distance") else None

        return {
            "name": collection_name,
            "status": str(info.status),
            "points_count": info.points_count,
            "indexed_vectors_count": getattr(info, "indexed_vectors_count", None),
            "vector_dimension": size,
            "distance": distance,
        }


def get_vector_store(
    config_path: Union[str, Path] = "configs/retrieval.yaml",
    mode_override: Optional[str] = None,
) -> VectorStore:
    """Factory helper to obtain the configured VectorStore instance."""
    return QdrantVectorStore.from_config(config_path=config_path, mode_override=mode_override)
