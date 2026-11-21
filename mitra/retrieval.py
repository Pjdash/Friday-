"""Offline BM25 retrieval over knowledge-base sections, filtered by date, scheme and language.

Resolved grievances are never retrievable: they are examples of past answers (several quote the
old pension cap) and carry no authority. FAQs are retrievable but ranked below official text.
"""
from __future__ import annotations

import logging
import math
import re
import threading
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import env, precedence
from .embeddings import Embedder, VectorIndex
from .kb import Chunk, Document, KnowledgeBase, chunks_of

log = logging.getLogger("mitra.retrieval")

RETRIEVABLE_TYPES = frozenset({"guideline", "policy", "amendment", "circular", "faq"})

# \w misses Indic vowel signs, which would split every word apart, so the Devanagari, Tamil and
# Kannada blocks are listed explicitly.
_TOKEN = re.compile(r"[\wऀ-ॿ஀-௿ಀ-೿‌‍]+")
_STOPWORDS = frozenset(
    # English
    "a an and are as at be by can do for from has have how i in is it me my of on or the to what when where which who will with you your "
    # Hindi
    "की का के है हैं क्या में से को और यह कि पर भी तो था हो कौन कब कैसे "
    # Kannada
    "ಏನು ಎಂದರೆ ಮತ್ತು ಆ ಈ ಇದು ಅದು ಯಾವ ಏನಾಗಿದೆ ಇದೆ "
    # Tamil
    "என்ன மற்றும் இது அது ஒரு என்று எது எப்படி உள்ளது".split()
)


def tokenize(text: str) -> list[str]:
    tokens = _TOKEN.findall(unicodedata.normalize("NFKC", text).casefold())
    return [t for t in tokens if t not in _STOPWORDS]


@dataclass
class Hit:
    chunk: Chunk
    score: float
    amended_by: list[Document]

    @property
    def doc(self) -> Document:
        return self.chunk.doc


class _BM25:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(doc) for doc in corpus]
        self.lengths = [len(doc) for doc in corpus]
        self.avg_len = (sum(self.lengths) / len(corpus)) if corpus else 0.0
        df: Counter[str] = Counter()
        for tf in self.tf:
            df.update(tf.keys())
        n = len(corpus)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def score(self, query: list[str], index: int) -> float:
        tf, length = self.tf[index], self.lengths[index]
        total = 0.0
        for term in set(query):
            freq = tf.get(term, 0)
            if not freq:
                continue
            norm = freq + self.k1 * (1 - self.b + self.b * length / (self.avg_len or 1))
            total += self.idf[term] * freq * (self.k1 + 1) / norm
        return total


def embedding_text(chunk: Chunk) -> str:
    """What the dense index sees for a chunk: the document title plus the section.

    Unlike BM25, dense retrieval needs the title. A section such as "2 Benefit" never names its own
    scheme, so without the title every scheme's benefit section would look alike.
    """
    return f"{chunk.doc.title}\n{chunk.text}"


class Retriever:
    """Hybrid search: BM25 keywords fused with dense embeddings when an embedder is available.

    Every guard is applied before and independently of ranking, so the dense side can never surface
    something BM25 could not: documents not in force on the date, other schemes' documents, and
    resolved grievances (never indexed) are all excluded first. Without an embedder, or whenever the
    provider fails, results are exactly the keyword results.
    """

    #: Reciprocal-rank-fusion constant: larger values flatten the difference between ranks.
    RRF_K = 20
    #: How many dense candidates enter the fusion.
    DENSE_POOL = 10
    #: Cosine similarity a chunk needs to be offered on meaning alone. Calibrated with
    #: scripts/eval_retrieval.py against gemini-embedding-001 (768 dimensions): the best match for every in-scope
    #: question scored 0.68-0.78 and for out-of-scope questions 0.48-0.64. The gap is thin and rests on 23
    #: questions, so re-run the script after changing the embedding model or the knowledge base.
    #: Set MITRA_DENSE_MIN_SIM to override.
    DENSE_MIN_SIM = 0.66

    def __init__(self, kb: KnowledgeBase, embedder: Embedder | None = None, *,
                 cache_path: Path | None = None, dense_min_sim: float | None = None,
                 retry_after: float = 60.0, clock=time.monotonic):
        self.kb = kb
        self.chunks: list[Chunk] = [
            c for doc in kb if doc.doc_type in RETRIEVABLE_TYPES for c in chunks_of(doc)
        ]
        # The document title is deliberately not indexed for BM25: it repeats in every chunk of a document
        # and would pull in near-empty preamble chunks whose only content is the title.
        self._index = _BM25([tokenize(c.text) for c in self.chunks])
        self._embedder = embedder
        self._cache_path = cache_path
        self._min_sim = dense_min_sim if dense_min_sim is not None else float(
            env.get("MITRA_DENSE_MIN_SIM", str(self.DENSE_MIN_SIM)))
        self._retry_after, self._clock = retry_after, clock
        self._dense: VectorIndex | None = None
        self._dense_down_until = 0.0
        self._lock = threading.Lock()

    @property
    def dense_enabled(self) -> bool:
        return self._embedder is not None

    def warm(self) -> bool:
        """Build (or load from cache) the dense index now. Returns False when it is unavailable."""
        return self._dense_index() is not None

    def _dense_index(self) -> VectorIndex | None:
        if self._embedder is None:
            return None
        with self._lock:
            if self._dense is not None:
                return self._dense
            if self._clock() < self._dense_down_until:
                return None
            try:
                self._dense = VectorIndex([embedding_text(c) for c in self.chunks], self._embedder, self._cache_path)
                log.info("dense index ready", extra={"chunks": len(self._dense), "embedded_now": self._dense.newly_embedded})
            except Exception as exc:  # noqa: BLE001 - any provider failure must degrade to keyword search
                self._dense_down_until = self._clock() + self._retry_after
                log.warning("dense index unavailable, using keyword search only",
                            extra={"error_type": type(exc).__name__})
            return self._dense

    def _similarities(self, query: str) -> list[float] | None:
        index = self._dense_index()
        if index is None:
            return None
        try:
            return index.similarities(query)
        except Exception as exc:  # noqa: BLE001
            self._dense_down_until = self._clock() + self._retry_after
            log.warning("query embedding failed, using keyword search only",
                        extra={"error_type": type(exc).__name__})
            return None

    def _eligible(self, i: int, as_of: date, scheme_id: str | None) -> bool:
        doc = self.chunks[i].doc
        if not precedence.in_force(doc, as_of, self.kb):
            return False
        if scheme_id and doc.scheme_ids and scheme_id not in doc.scheme_ids:
            return False
        if scheme_id and not doc.scheme_ids and doc.doc_type != "policy":
            return False
        return True

    def search(self, query: str, as_of: date, *, scheme_id: str | None = None,
               language: str | None = None, k: int = 3) -> list[Hit]:
        if not query.strip():
            return []
        q = tokenize(query)
        eligible = [i for i in range(len(self.chunks)) if self._eligible(i, as_of, scheme_id)]
        lexical = {i: s for i in eligible if q and (s := self._index.score(q, i)) > 0}
        sims = self._similarities(query)

        if sims is None:
            scores = dict(lexical)
        else:
            scores = self._fuse(lexical, {i: sims[i] for i in eligible})
        scored = []
        for i, score in scores.items():
            doc = self.chunks[i].doc
            if language and doc.language == language:
                score *= 1.3
            if not doc.is_authoritative:
                score *= 0.8
            scored.append((score, i))
        scored.sort(reverse=True)
        hits = []
        for score, i in scored[:k]:
            chunk = self.chunks[i]
            hits.append(Hit(chunk, score, precedence.amendments_after(chunk.doc, self.kb, as_of)))
        return hits

    def _fuse(self, lexical: dict[int, float], similarity: dict[int, float]) -> dict[int, float]:
        """Reciprocal rank fusion of the keyword ranking and the (floored) dense ranking."""
        by_keyword = sorted(lexical, key=lexical.__getitem__, reverse=True)
        by_meaning = [i for i in sorted(similarity, key=similarity.__getitem__, reverse=True)
                      if similarity[i] >= self._min_sim][:self.DENSE_POOL]
        fused: dict[int, float] = {}
        for ranking in (by_keyword, by_meaning):
            for rank, i in enumerate(ranking):
                fused[i] = fused.get(i, 0.0) + 1.0 / (self.RRF_K + rank + 1)
        return fused
