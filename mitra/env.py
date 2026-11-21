"""The on/off switches and provider keys for the parts of the assistant that use the network.

Like the rest of the package this reads process environment variables only; it never loads a .env file
(see the README). The helper scripts take an explicit --env-file instead.

Everything networked (embeddings, LLM answers) is optional and fails soft: with a switch off, a missing
key, a missing package or a provider outage, the assistant falls back to offline BM25 retrieval and
quoting the official text. Nothing in this module logs or returns a key's value.
"""
from __future__ import annotations

import os

_OFF = {"off", "0", "false", "no", "disabled"}


def enabled(switch: str) -> bool:
    """False when the environment variable `switch` is set to off/0/false/no."""
    return os.environ.get(switch, "auto").strip().lower() not in _OFF


def get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def google_key() -> str:
    return get("GOOGLE_API_KEY") or get("GEMINI_API_KEY")


def groq_key() -> str:
    return get("GROQ_API_KEY")
