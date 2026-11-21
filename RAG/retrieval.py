"""Offline BM25 retrieval over knowledge-base sections, filtered by date, scheme and language.

Resolved grievances are never retrievable: they are examples of past answers (several quote the
old pension cap) and carry no authority. FAQs are retrievable but ranked below official text.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import date

from . import precedence
from .kb import Chunk, Document, KnowledgeBase, chunks_of

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


class Retriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.chunks: list[Chunk] = [
            c for doc in kb if doc.doc_type in RETRIEVABLE_TYPES for c in chunks_of(doc)
        ]
        # The document title is deliberately not indexed: it repeats in every chunk of a document and
        # would pull in near-empty preamble chunks whose only content is the title.
        self._index = _BM25([tokenize(c.text) for c in self.chunks])

    def search(self, query: str, as_of: date, *, scheme_id: str | None = None,
               language: str | None = None, k: int = 3) -> list[Hit]:
        q = tokenize(query)
        if not q:
            return []
        scored = []
        for i, chunk in enumerate(self.chunks):
            doc = chunk.doc
            if not precedence.in_force(doc, as_of, self.kb):
                continue
            if scheme_id and doc.scheme_ids and scheme_id not in doc.scheme_ids:
                continue
            if scheme_id and not doc.scheme_ids and doc.doc_type != "policy":
                continue
            score = self._index.score(q, i)
            if score <= 0:
                continue
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
