import os
from datetime import date

# Hermetic: tests never call an embedding or LLM provider, whatever keys the developer has in .env.
# Set before any mitra module reads configuration. RAG tests inject fakes explicitly.
os.environ["MITRA_EMBEDDINGS"] = "off"
os.environ["MITRA_LLM"] = "off"

import pytest  # noqa: E402

from mitra.agent import Assistant  # noqa: E402
from mitra.kb import KnowledgeBase  # noqa: E402
from mitra.seed import CitizenStore  # noqa: E402

TODAY = date(2026, 11, 21)  # the "current" date in the knowledge base's world


@pytest.fixture(scope="session")
def kb() -> KnowledgeBase:
    return KnowledgeBase.load()


@pytest.fixture(scope="session")
def citizens() -> CitizenStore:
    store = CitizenStore.load()
    if not len(store):
        pytest.skip("seed citizens not found")
    return store


@pytest.fixture(scope="session")
def assistant(kb, citizens) -> Assistant:
    return Assistant(kb, citizens)
