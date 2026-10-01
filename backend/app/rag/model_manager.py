"""
Sentence Transformer Model Manager.
Handles lazy loading, in-process caching, device configuration,
dimension verification, and metadata reporting for embedding models.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from fastembed import TextEmbedding

from backend.app.config import get_settings
from backend.app.rag.exceptions import EmbeddingModelLoadError

logger = logging.getLogger("sahayakai.rag.model_manager")


class EmbeddingModelManager:
    """Thread-safe singleton managing the FastEmbed model lifecycle."""

    _instance: Optional[EmbeddingModelManager] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._model: Optional[TextEmbedding] = None
        self._load_lock: threading.Lock = threading.Lock()
        self._model_name: Optional[str] = None
        self._dimension: Optional[int] = None
        self._device: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "EmbeddingModelManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load_model(self, force_reload: bool = False) -> TextEmbedding:
        """
        Lazily initialize and cache the ONNX embedding model.
        Verifies actual embedding dimension against configured expectations.
        """
        if self._model is not None and not force_reload:
            return self._model

        with self._load_lock:
            if self._model is not None and not force_reload:
                return self._model

            settings = get_settings()
            model_name = settings.EMBEDDING_MODEL
            if model_name == "all-MiniLM-L6-v2":
                model_name = "sentence-transformers/all-MiniLM-L6-v2"
            cache_dir = settings.EMBEDDING_CACHE_DIR

            logger.info("Initializing FastEmbed model '%s'...", model_name)

            try:
                from fastembed import TextEmbedding

                model = TextEmbedding(
                    model_name=model_name,
                    cache_dir=cache_dir,
                    threads=1,
                    providers=["CPUExecutionProvider"],
                    lazy_load=True,
                )

                model_info = next(
                    item
                    for item in TextEmbedding.list_supported_models()
                    if item["model"] == model_name
                )
                actual_dim = model_info["dim"]
                if actual_dim != settings.EMBEDDING_DIMENSION:
                    raise EmbeddingModelLoadError(
                        message=f"Model '{model_name}' dimension mismatch: expected {settings.EMBEDDING_DIMENSION}, got {actual_dim}.",
                        details={"expected": settings.EMBEDDING_DIMENSION, "actual": actual_dim},
                    )

                self._model = model
                self._model_name = settings.EMBEDDING_MODEL
                self._dimension = actual_dim
                self._device = "cpu"

                logger.info("FastEmbed model '%s' initialized (dimension: %d).", model_name, actual_dim)
                return self._model

            except Exception as exc:
                logger.error("Failed to load embedding model '%s': %s", model_name, exc, exc_info=True)
                if isinstance(exc, EmbeddingModelLoadError):
                    raise exc
                raise EmbeddingModelLoadError(
                    message=f"Failed to initialize embedding model '{model_name}': {str(exc)}",
                    details={"model_name": model_name, "error": str(exc)},
                )

    def is_loaded(self) -> bool:
        """Check if model is currently loaded in memory."""
        return self._model is not None

    def get_metadata(self) -> Dict[str, Any]:
        """Return model metadata."""
        settings = get_settings()
        return {
            "model_name": self._model_name or settings.EMBEDDING_MODEL,
            "dimension": self._dimension or settings.EMBEDDING_DIMENSION,
            "device": self._device or settings.EMBEDDING_DEVICE,
            "is_loaded": self.is_loaded(),
            "batch_size": settings.EMBEDDING_BATCH_SIZE,
            "normalize": settings.EMBEDDING_NORMALIZE,
        }

    def unload_model(self) -> None:
        """Unload model from memory (useful for testing and memory cleanup)."""
        with self._load_lock:
            self._model = None
            self._model_name = None
            self._dimension = None
            self._device = None


def get_model_manager() -> EmbeddingModelManager:
    """Return the global EmbeddingModelManager instance."""
    return EmbeddingModelManager.get_instance()
