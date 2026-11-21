"""Dense embeddings for retrieval: a provider wrapper and a small on-disk-cached vector index.

The knowledge base is a few hundred chunks, so the index is plain Python (no vector database): each
chunk is embedded once, cached by content hash, and a query is scored against every chunk by cosine
similarity. Embedding is what lets a Kannada or Tamil question find an English clause with no shared
words, which keyword (BM25) search cannot do.

Privacy: only knowledge-base text is embedded in bulk. A query is sent to the provider for embedding
(after the same sanitising as every other message) but is never written to the cache or the logs.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Protocol, Sequence

from . import env

log = logging.getLogger("mitra.embeddings")

DEFAULT_MODEL = "gemini-embedding-001"
DEFAULT_DIMENSIONS = 768
_BATCH = 32


class Embedder(Protocol):
    #: Identifies the model and settings; part of the cache key so a change never reuses stale vectors.
    model: str

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class GeminiEmbedder:
    """Gemini embeddings via langchain-google-genai (document vs query task types are set by the library)."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, dimensions: int = DEFAULT_DIMENSIONS,
                 timeout: float = 20.0):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        self.model = f"gemini:{model}:{dimensions}"
        self._client = GoogleGenerativeAIEmbeddings(
            model=model, google_api_key=api_key, output_dimensionality=dimensions,
            request_options={"timeout": timeout})

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._client.embed_documents(list(texts))

    def embed_query(self, text: str) -> list[float]:
        return self._client.embed_query(text)


def default_embedder() -> Embedder | None:
    """The configured embedder, or None when embeddings are off, unkeyed or the package is missing."""
    if not env.enabled("MITRA_EMBEDDINGS"):
        return None
    key = env.google_key()
    if not key:
        log.info("embeddings disabled: no GOOGLE_API_KEY, using keyword retrieval only")
        return None
    try:
        return GeminiEmbedder(
            key, env.get("MITRA_EMBED_MODEL", DEFAULT_MODEL),
            int(env.get("MITRA_EMBED_DIMENSIONS", str(DEFAULT_DIMENSIONS))),
            float(env.get("MITRA_EMBED_TIMEOUT", "20")))
    except ImportError:
        log.warning("embeddings disabled: langchain-google-genai is not installed (see requirements-rag.txt)")
    except Exception as exc:  # noqa: BLE001 - bad settings must not stop the assistant starting
        log.warning("embeddings disabled: could not create the embedder", extra={"error_type": type(exc).__name__})
    return None


def cache_dir() -> Path:
    override = env.get("MITRA_CACHE_DIR")
    return Path(override) if override else Path(__file__).resolve().parent.parent / ".cache" / "mitra"


def _normalised(vector: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    if not norm:
        raise ValueError("the embedding provider returned a zero vector")
    return [x / norm for x in vector]


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class VectorIndex:
    """Unit vectors for a fixed list of texts, embedded once and cached on disk.

    Construction embeds only the texts that are not already cached and raises if the provider fails,
    so callers decide how to degrade. Similarity of a query to every text is one cosine each.
    """

    def __init__(self, texts: Sequence[str], embedder: Embedder, cache_path: Path | None = None):
        self._embedder = embedder
        digests = [_digest(t) for t in texts]
        cache = self._read(cache_path, embedder.model)
        missing = sorted({d: t for d, t in zip(digests, texts) if d not in cache}.items())
        for start in range(0, len(missing), _BATCH):
            batch = missing[start:start + _BATCH]
            vectors = embedder.embed_documents([t for _, t in batch])
            if len(vectors) != len(batch):
                raise ValueError("the embedding provider returned the wrong number of vectors")
            for (digest, _), vector in zip(batch, vectors):
                cache[digest] = [round(x, 6) for x in _normalised(vector)]
        self._vectors = [cache[d] for d in digests]
        if missing:
            self._write(cache_path, embedder.model, {d: cache[d] for d in digests})
        self.newly_embedded = len(missing)

    def __len__(self) -> int:
        return len(self._vectors)

    def similarities(self, query: str) -> list[float]:
        """Cosine similarity of the query to each indexed text, in index order."""
        q = _normalised(self._embedder.embed_query(query))
        if self._vectors and len(q) != len(self._vectors[0]):
            raise ValueError("query and index embeddings have different sizes")
        return [sum(a * b for a, b in zip(q, v)) for v in self._vectors]

    # ---- cache ---------------------------------------------------------------------------------

    @staticmethod
    def _file(cache_path: Path | None, model: str) -> Path | None:
        if cache_path is None:
            return None
        return cache_path / f"embeddings-{re.sub(r'[^A-Za-z0-9._-]+', '_', model)}.json"

    @classmethod
    def _read(cls, cache_path: Path | None, model: str) -> dict[str, list[float]]:
        path = cls._file(cache_path, model)
        if path is None or not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            vectors = data["vectors"] if data.get("model") == model else {}
            return {k: v for k, v in vectors.items() if isinstance(v, list)}
        except (OSError, ValueError, KeyError, AttributeError):
            log.warning("embedding cache is unreadable and will be rebuilt")
            return {}

    @classmethod
    def _write(cls, cache_path: Path | None, model: str, vectors: dict[str, list[float]]) -> None:
        path = cls._file(cache_path, model)
        if path is None:
            return
        tmp = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"model": model, "vectors": vectors}, handle)
            os.replace(tmp, path)  # atomic: a crash never leaves a half-written cache
        except OSError:
            log.warning("could not write the embedding cache; vectors will be recomputed next start")
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
