from datetime import date

import pytest

from mitra import config
from mitra.kb import Document, KnowledgeBase, chunks_of, parse_front_matter
from mitra.precedence import Status, amendments_after, effective_value, in_force, status_on


# ---- loading ----------------------------------------------------------------------------------

def test_expected_documents_are_loaded(kb):
    for source_id in ("GL-FRM-01", "GL-FRM-02", "GL-PEN-01", "POL-FEE-01", "POL-GRV-01", "POL-PRV-01",
                      "CIR-2026-01", "CIR-2026-07", "CIR-2026-08", "CIR-2026-09", "HI-FRAUD-01", "GRV-2026-25"):
        assert kb.get(source_id) is not None, source_id


def test_repo_copies_and_bundled_kb_agree(kb):
    """The three guidelines exist both at the repo root and in kb/; they must be identical."""
    assert kb.conflicts == []
    for source_id in ("GL-FRM-01", "GL-FRM-02", "GL-PEN-01"):
        assert kb.get(source_id).path.parent in {config.REPO_ROOT, config.BUNDLED_KB}


def test_non_kb_markdown_is_ignored(kb):
    assert all(doc.path is None or doc.path.name != "README.md" for doc in kb)


def test_grievances_are_never_authoritative(kb):
    grievances = [d for d in kb if d.doc_type == "grievance"]
    assert grievances and not any(d.is_authoritative for d in grievances)


def test_front_matter_parsing_handles_bom_and_crlf():
    text = '﻿---\r\nsource_id: "X-1"\r\nsupersedes: ""\r\nscheme_id: "A, B"\r\n---\r\n# Body\r\n'
    meta, body = parse_front_matter(text)
    assert meta == {"source_id": "X-1", "supersedes": "", "scheme_id": "A, B"}
    assert body.startswith("# Body")


def _write_doc(directory, name, source_id, updated, body="text", extra=""):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(
        f'---\nsource_id: "{source_id}"\ndoc_type: "guideline"\nlast_updated: "{updated}"\n{extra}---\n{body}\n',
        encoding="utf-8")


def test_bad_date_fails_loudly_with_the_file_name(tmp_path):
    _write_doc(tmp_path, "bad.md", "X-1", "01/04/2026")
    with pytest.raises(ValueError, match="bad.md"):
        KnowledgeBase.load([tmp_path])


def test_dedupe_prefers_later_last_updated(tmp_path):
    _write_doc(tmp_path / "a", "x.md", "X-1", "2026-01-01", body="old text")
    _write_doc(tmp_path / "b", "x.md", "X-1", "2026-06-01", body="new text")
    kb = KnowledgeBase.load([tmp_path / "a", tmp_path / "b"])
    assert "new text" in kb.get("X-1").body and kb.conflicts == []


def test_same_date_different_text_is_reported_not_silently_resolved(tmp_path):
    _write_doc(tmp_path / "a", "x.md", "X-1", "2026-01-01", body="version one")
    _write_doc(tmp_path / "b", "x.md", "X-1", "2026-01-01", body="version two")
    kb = KnowledgeBase.load([tmp_path / "a", tmp_path / "b"])
    assert "version one" in kb.get("X-1").body  # first directory wins
    assert [c[0] for c in kb.conflicts] == ["X-1"]


def test_chunks_split_on_second_level_headings(kb):
    headings = [c.heading for c in chunks_of(kb.get("GL-PEN-01"))]
    assert any(h.endswith("Eligibility") for h in headings) and len(headings) >= 6


# ---- precedence -------------------------------------------------------------------------------

@pytest.mark.parametrize("source_id, as_of, expected", [
    ("CIR-2026-11", date(2026, 4, 30), Status.NOT_YET_EFFECTIVE),
    ("CIR-2026-11", date(2026, 5, 1), Status.IN_FORCE),
    ("CIR-2026-11", date(2026, 9, 9), Status.IN_FORCE),
    ("CIR-2026-11", date(2026, 9, 10), Status.EXPIRED),
    ("CIR-2026-01", date(2026, 9, 9), Status.NOT_YET_EFFECTIVE),
    ("CIR-2026-01", date(2026, 9, 10), Status.IN_FORCE),
    ("GL-INS-01", date(2026, 9, 30), Status.IN_FORCE),
    ("GL-INS-01", date(2026, 10, 1), Status.SUPERSEDED),  # CIR-2026-04 closes new enrolment
    ("CIR-2026-05", date(2026, 11, 21), Status.NOT_YET_EFFECTIVE),  # announced launch 2026-12-15
    ("CIR-2026-05", date(2026, 12, 15), Status.IN_FORCE),
])
def test_status_on(kb, source_id, as_of, expected):
    assert status_on(kb.get(source_id), as_of, kb) is expected


def test_informational_documents_cannot_supersede(tmp_path):
    _write_doc(tmp_path, "g.md", "GL-X", "2026-01-01", extra='effective_from: "2026-01-01"\n')
    (tmp_path / "f.md").write_text(
        '---\nsource_id: "FAQ-X"\ndoc_type: "faq"\nlast_updated: "2026-02-01"\neffective_from: "2026-02-01"\n'
        'supersedes: "GL-X"\n---\nfaq text\n', encoding="utf-8")
    kb = KnowledgeBase.load([tmp_path])
    assert in_force(kb.get("GL-X"), date(2026, 6, 1), kb)


def test_pension_guideline_is_amended_by_the_right_circular_at_the_right_time(kb):
    guideline = kb.get("GL-PEN-01")
    ids = lambda as_of: [d.source_id for d in amendments_after(guideline, kb, as_of)]  # noqa: E731
    assert ids(date(2026, 11, 21)) == ["CIR-2026-01"]
    assert ids(date(2026, 8, 1)) == ["CIR-2026-11"]  # the interim notice, before CIR-2026-01
    assert ids(date(2026, 4, 15)) == []


def test_translated_summary_refreshed_after_the_circular_is_not_flagged_as_stale(kb):
    assert amendments_after(kb.get("HI-PEN-01"), kb, date(2026, 11, 21)) == []


@pytest.mark.parametrize("as_of, expected_value, expected_source", [
    (date(2026, 4, 1), 120000, "GL-PEN-01"),
    (date(2026, 9, 9), 120000, "GL-PEN-01"),
    (date(2026, 9, 10), 150000, "CIR-2026-01"),
    (date(2026, 11, 21), 150000, "CIR-2026-01"),
])
def test_effective_value_follows_the_circular_date(kb, as_of, expected_value, expected_source):
    assert effective_value(120000, "GL-PEN-01", [("CIR-2026-01", 150000)], kb, as_of) == (expected_value, expected_source)
