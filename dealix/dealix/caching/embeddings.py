"""
Local Arabic-friendly embeddings — zero API cost.

Uses sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (118 MB).
CPU-only, ~50ms per query on a modern server. Multilingual incl. Arabic.
"""

from __future__ import annotations

import hashlib
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_EMBED_DIM = 384


class LocalEmbedder:
    """Thread-safe lazy-loaded local embedder.

    The underlying sentence-transformers model is heavy (~118 MB) so we load it
    on first use and keep it as a class-level singleton.
    """

    _lock = threading.Lock()
    _model = None  # type: ignore[assignment]

    @classmethod
    def _get_model(cls):  # pragma: no cover — external dep
        if cls._model is None:
            with cls._lock:
                if cls._model is None:
                    from sentence_transformers import SentenceTransformer  # type: ignore

                    cls._model = SentenceTransformer(_MODEL_NAME)
        return cls._model

    @staticmethod
    def fingerprint(text: str) -> str:
        """Deterministic short hash — used as Redis sub-key."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def embed(cls, text: str) -> np.ndarray:
        """Return a 384-dim float32 vector for ``text`` (L2-normalized)."""
        import numpy as np

        model = cls._get_model()
        vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return vec.astype(np.float32)

    @classmethod
    def similarity(cls, a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two already-normalized vectors."""
        import numpy as np

        return float(np.dot(a, b))


DIM = _EMBED_DIM
