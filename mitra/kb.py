"""Knowledge-base loading: front-matter parsing, deduplication, section chunking."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Iterator

from . import config

# Only these document types can set or amend rules (POL-PRV-01 section 4).
# FAQs and resolved grievances are informational and never override a guideline or circular.
AUTHORITATIVE_TYPES = frozenset({"guideline", "policy", "amendment", "circular"})

_FRONT_MATTER = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)(.*)\Z", re.S)
_KEY_VALUE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*?)[ \t]*$")


@dataclass(frozen=True)
class Document:
    source_id: str
    doc_type: str
    title: str
    language: str
    authority_level: int
    scheme_ids: tuple[str, ...]
    last_updated: date | None
    effective_from: date | None
    valid_until: date | None
    supersedes: tuple[str, ...]
    body: str
    path: Path | None = None

    @property
    def is_authoritative(self) -> bool:
        return self.doc_type in AUTHORITATIVE_TYPES


@dataclass(frozen=True)
class Chunk:
    doc: Document
    heading: str
    text: str


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        kv = _KEY_VALUE.match(line)
        if kv:
            meta[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return meta, match.group(2)


def _split_ids(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _parse_date(value: str | None, field: str, where: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{where}: bad {field} {value!r} (expected YYYY-MM-DD)") from exc


def _document_from_markdown(path: Path) -> Document | None:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8-sig"))
    source_id = meta.get("source_id")
    if not source_id:  # README and other non-KB markdown
        return None
    where = str(path)
    return Document(
        source_id=source_id,
        doc_type=meta.get("doc_type", ""),
        title=meta.get("title", source_id),
        language=meta.get("language", "en"),
        authority_level=int(meta.get("authority_level") or 0),
        scheme_ids=_split_ids(meta.get("scheme_id", "")),
        last_updated=_parse_date(meta.get("last_updated"), "last_updated", where),
        effective_from=_parse_date(meta.get("effective_from"), "effective_from", where),
        valid_until=_parse_date(meta.get("valid_until"), "valid_until", where),
        supersedes=_split_ids(meta.get("supersedes", "")),
        body=body,
        path=path,
    )


def _documents_from_grievances(path: Path) -> Iterator[Document]:
    for item in json.loads(path.read_text(encoding="utf-8-sig")):
        body = f"Question: {item['citizen_question']}\nResolution: {item['resolution']}"
        yield Document(
            source_id=item["source_id"],
            doc_type=item.get("doc_type", "grievance"),
            title=f"Resolved grievance {item['source_id']}",
            language=item.get("language", "en"),
            authority_level=int(item.get("authority_level", 4)),
            scheme_ids=_split_ids(item.get("scheme_id", "")),
            last_updated=_parse_date(item.get("resolved_at"), "resolved_at", str(path)),
            effective_from=None,
            valid_until=None,
            supersedes=(),
            body=body,
            path=path,
        )


def _read_dir(directory: Path) -> Iterator[Document]:
    for path in sorted(directory.glob("*.md")):
        doc = _document_from_markdown(path)
        if doc is not None:
            yield doc
    for folder in (directory / "kb" / "grievances", directory / "grievances"):
        for path in sorted(folder.glob("*.json")):
            yield from _documents_from_grievances(path)


def _normalise(text: str) -> str:
    return " ".join(text.split())


def chunks_of(doc: Document) -> list[Chunk]:
    """Split a document at '## ' headings. Text before the first heading is its own chunk."""
    chunks = []
    for part in re.split(r"(?m)^(?=## )", doc.body):
        part = part.strip()
        if not part:
            continue
        heading = part.splitlines()[0].lstrip("# ").strip()
        chunks.append(Chunk(doc, heading, part))
    return chunks


class KnowledgeBase:
    def __init__(self, docs: Iterable[Document], conflicts: Iterable[tuple[str, tuple[str, str]]] = ()):
        self._docs: dict[str, Document] = {d.source_id: d for d in docs}
        self.conflicts: list[tuple[str, tuple[str, str]]] = list(conflicts)

    @classmethod
    def load(cls, dirs: Iterable[Path] | None = None) -> "KnowledgeBase":
        """Load every directory in order, deduplicating by source_id.

        For a repeated source_id the later last_updated wins. If two copies have the same
        last_updated but different text, the first one is kept and the clash is recorded in
        `conflicts` so callers can surface it instead of silently picking a side.
        """
        found: dict[str, Document] = {}
        conflicts: list[tuple[str, tuple[str, str]]] = []
        for directory in dirs if dirs is not None else config.kb_dirs():
            for doc in _read_dir(Path(directory)):
                previous = found.get(doc.source_id)
                if previous is None:
                    found[doc.source_id] = doc
                    continue
                if previous.last_updated == doc.last_updated and _normalise(previous.body) != _normalise(doc.body):
                    conflicts.append((doc.source_id, (str(previous.path), str(doc.path))))
                if (doc.last_updated or date.min) > (previous.last_updated or date.min):
                    found[doc.source_id] = doc
        return cls(found.values(), conflicts)

    def __len__(self) -> int:
        return len(self._docs)

    def __iter__(self) -> Iterator[Document]:
        return iter(self._docs.values())

    def get(self, source_id: str) -> Document | None:
        return self._docs.get(source_id)

    def problems(self, required_ids: Iterable[str] = ()) -> list[str]:
        """Reasons this knowledge base is not safe to serve from (empty list = healthy).

        Reports only source ids, never file paths, so the result can be shown to callers.
        """
        found = [f"conflicting copies of {source_id}" for source_id, _ in self.conflicts]
        found += [f"missing required document {source_id}" for source_id in sorted(set(required_ids))
                  if source_id not in self._docs]
        return found

    def authoritative(self) -> list[Document]:
        return [d for d in self._docs.values() if d.is_authoritative]

    def for_scheme(self, scheme_id: str) -> list[Document]:
        return [d for d in self._docs.values() if scheme_id in d.scheme_ids]
