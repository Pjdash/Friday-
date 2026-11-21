"""Which documents are in force on a given date, and which later circulars override a guideline.

Rules come from POL-PRV-01 section 4: a later official circular takes precedence over the
conflicting clause of the base guideline; unmodified clauses stay in force. A document that
another authoritative document `supersedes` stops applying once that document takes effect.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Iterable

from .kb import Document, KnowledgeBase


class Status(str, Enum):
    IN_FORCE = "in_force"
    NOT_YET_EFFECTIVE = "not_yet_effective"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


def status_on(doc: Document, as_of: date, kb: KnowledgeBase) -> Status:
    if doc.effective_from and as_of < doc.effective_from:
        return Status.NOT_YET_EFFECTIVE
    if doc.valid_until and as_of > doc.valid_until:
        return Status.EXPIRED
    for other in kb.authoritative():
        if other.source_id != doc.source_id and doc.source_id in other.supersedes:
            if other.effective_from is None or other.effective_from <= as_of:
                return Status.SUPERSEDED
    return Status.IN_FORCE


def in_force(doc: Document, as_of: date, kb: KnowledgeBase) -> bool:
    return status_on(doc, as_of, kb) is Status.IN_FORCE


def amendments_after(doc: Document, kb: KnowledgeBase, as_of: date) -> list[Document]:
    """In-force circulars/amendments for the same scheme(s) that postdate this guideline's text.

    Documents refreshed after the circular (e.g. translated summaries that already quote it)
    are not flagged. Returned oldest first.
    """
    if doc.doc_type != "guideline" or not doc.scheme_ids:
        return []
    cutoff = doc.last_updated or date.min
    found = [
        other
        for other in kb.authoritative()
        if other.doc_type in {"amendment", "circular"}
        and set(other.scheme_ids) & set(doc.scheme_ids)
        and other.effective_from is not None
        and other.effective_from > cutoff
        and in_force(other, as_of, kb)
    ]
    return sorted(found, key=lambda d: d.effective_from or date.min)


def effective_value(
    base_value: Any,
    base_source: str,
    overrides: Iterable[tuple[str, Any]],
    kb: KnowledgeBase,
    as_of: date,
) -> tuple[Any, str]:
    """Value of a rule on `as_of`: the base guideline value unless an in-force circular overrides it.

    `overrides` is (source_id, value) pairs. The in-force override with the latest effective_from wins.
    """
    value, source = base_value, base_source
    latest = date.min
    base = kb.get(base_source)
    if base is not None and base.effective_from:
        latest = base.effective_from
    for source_id, new_value in overrides:
        doc = kb.get(source_id)
        if doc is None or not in_force(doc, as_of, kb):
            continue
        if (doc.effective_from or date.min) >= latest:
            value, source, latest = new_value, source_id, doc.effective_from or date.min
    return value, source
