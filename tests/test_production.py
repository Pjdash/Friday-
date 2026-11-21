import json
import logging

from mitra import config
from mitra.kb import KnowledgeBase
from mitra.logging_setup import JsonFormatter
from mitra.schemes import SCHEMES, required_source_ids
from mitra.seed import CitizenStore


def test_the_shipped_kb_satisfies_every_citation_in_the_rules(kb):
    assert kb.problems(required_source_ids()) == []


def test_required_ids_are_derived_from_the_rules():
    ids = required_source_ids()
    for expected in ("GL-FRM-01", "GL-FRM-02", "GL-PEN-01", "CIR-2026-01", "CIR-2026-07", "CIR-2026-08",
                     "POL-FEE-01", "POL-GRV-01", "POL-PRV-01", "CIR-2026-09"):
        assert expected in ids
    assert all(s.guideline_id in ids for s in SCHEMES.values())


def test_problems_report_missing_documents_and_conflicts_by_id_only(tmp_path):
    for name, body in (("a", "one"), ("b", "two")):
        folder = tmp_path / name
        folder.mkdir()
        (folder / "x.md").write_text(
            f'---\nsource_id: "X-1"\nlast_updated: "2026-01-01"\n---\n{body}\n', encoding="utf-8")
    kb = KnowledgeBase.load([tmp_path / "a", tmp_path / "b"])
    problems = kb.problems(["X-1", "GL-MISSING"])
    assert problems == ["conflicting copies of X-1", "missing required document GL-MISSING"]
    assert str(tmp_path) not in " ".join(problems)  # no filesystem paths in anything shown to callers


def test_bundled_kb_is_preferred_and_env_override_wins(monkeypatch):
    monkeypatch.delenv("MITRA_KB_DIRS", raising=False)
    assert config.kb_dirs()[0] == config.BUNDLED_KB
    monkeypatch.setenv("MITRA_KB_DIRS", "/a" + __import__("os").pathsep + "/b")
    assert [p.as_posix() for p in config.kb_dirs()] == ["/a", "/b"]


def test_demo_citizens_never_load_in_production_by_default(monkeypatch):
    monkeypatch.setenv("MITRA_ENV", "production")
    monkeypatch.delenv("MITRA_SEED_DIR", raising=False)
    assert config.is_production() and config.seed_dir() is None
    assert len(CitizenStore.load()) == 0


def test_seed_dir_can_still_be_set_explicitly_in_production(monkeypatch, tmp_path):
    monkeypatch.setenv("MITRA_ENV", "production")
    monkeypatch.setenv("MITRA_SEED_DIR", str(tmp_path))
    assert config.seed_dir() == tmp_path


def test_api_keys_and_cors_are_parsed_from_the_environment(monkeypatch):
    monkeypatch.setenv("MITRA_API_KEYS", " alpha , beta,, ")
    monkeypatch.setenv("MITRA_CORS_ORIGINS", "https://a.example, https://b.example")
    assert config.api_keys() == frozenset({"alpha", "beta"})
    assert config.cors_origins() == ["https://a.example", "https://b.example"]


def test_third_party_tracing_is_forced_off_so_citizen_messages_cannot_leave(monkeypatch):
    import importlib
    import os

    import mitra

    for name in ("LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2"):
        monkeypatch.setenv(name, "true")
    monkeypatch.delenv("MITRA_ALLOW_TRACING", raising=False)
    importlib.reload(mitra)
    assert os.environ["LANGSMITH_TRACING"] == "false" and os.environ["LANGCHAIN_TRACING_V2"] == "false"

    monkeypatch.setenv("MITRA_ALLOW_TRACING", "1")
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    importlib.reload(mitra)
    assert os.environ["LANGSMITH_TRACING"] == "true"  # explicit opt-in is respected


def test_json_log_lines_are_valid_json_with_extras():
    record = logging.LogRecord("mitra.x", logging.INFO, __file__, 1, "hello %s", ("world",), None)
    record.intent = "fee"
    payload = json.loads(JsonFormatter().format(record))
    assert payload["msg"] == "hello world" and payload["intent"] == "fee" and payload["level"] == "INFO"
