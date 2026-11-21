import os
from datetime import date
from pathlib import Path

# Hermetic environment, set before any mitra module reads configuration (mitra.api builds an app on import).
FIXTURES = Path(__file__).parent / "fixtures"
for name in ("MITRA_API_KEYS", "MITRA_KB_DIRS", "MITRA_CORS_ORIGINS", "MITRA_AS_OF"):
    os.environ.pop(name, None)
os.environ["MITRA_ENV"] = "development"
os.environ["MITRA_SEED_DIR"] = str(FIXTURES)
# Tests never call an embedding or LLM provider, whatever keys the developer has in .env.
# RAG tests inject fakes explicitly.
os.environ["MITRA_EMBEDDINGS"] = "off"
os.environ["MITRA_LLM"] = "off"

import pytest  # noqa: E402

from mitra import config  # noqa: E402
from mitra.agent import Assistant  # noqa: E402
from mitra.kb import KnowledgeBase  # noqa: E402
from mitra.seed import CitizenStore  # noqa: E402

TODAY = date(2026, 11, 21)  # the "current" date in the knowledge base's world


@pytest.fixture(scope="session")
def kb() -> KnowledgeBase:
    # The shipped KB plus the resolved-grievance fixtures, so tests can prove grievances never leak into answers.
    return KnowledgeBase.load([*config.kb_dirs(), FIXTURES])


@pytest.fixture(scope="session")
def citizens() -> CitizenStore:
    store = CitizenStore.load(FIXTURES)
    assert len(store), "test fixtures are missing"
    return store


@pytest.fixture(scope="session")
def assistant(kb, citizens) -> Assistant:
    return Assistant(kb, citizens)
