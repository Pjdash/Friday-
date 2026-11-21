"""Optional .env loading and the on/off switches for the parts of the assistant that use the network.

Everything networked (embeddings, LLM answers) is optional and fails soft: with a switch off, a missing
key, a missing package or a provider outage, the assistant falls back to offline BM25 retrieval and
quoting the official text. Nothing in this module logs or returns a key's value.
"""
from __future__ import annotations

import os

_OFF = {"off", "0", "false", "no", "disabled"}
_loaded = False


def load() -> None:
    """Read a .env file (if python-dotenv is installed and one exists). Never overrides real variables."""
    global _loaded
    if _loaded:
        return
    _loaded = True
    try:
        from dotenv import find_dotenv, load_dotenv
    except ImportError:
        return
    load_dotenv(find_dotenv(usecwd=True), override=False)


def enabled(switch: str) -> bool:
    """False when the environment variable `switch` is set to off/0/false/no."""
    load()
    return os.environ.get(switch, "auto").strip().lower() not in _OFF


def get(name: str, default: str = "") -> str:
    load()
    return os.environ.get(name, default).strip()


def google_key() -> str:
    return get("GOOGLE_API_KEY") or get("GEMINI_API_KEY")


def groq_key() -> str:
    return get("GROQ_API_KEY")
