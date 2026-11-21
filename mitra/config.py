"""Runtime configuration, read from environment variables (see README for the full table)."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = REPO_ROOT.parent
BUNDLED_KB = REPO_ROOT / "kb"


def is_production() -> bool:
    return os.environ.get("MITRA_ENV", "development").strip().lower() == "production"


def kb_dirs() -> list[Path]:
    """Directories scanned for knowledge-base documents.

    1. MITRA_KB_DIRS (os.pathsep-separated), if set.
    2. The bundled kb/ directory (plus the repo root) when it exists. This is what ships in the image.
    3. Otherwise, for local development, the sibling mitrapur_pradesh_* folders.

    When two copies share a source_id and last_updated, the earlier directory wins; differing text
    is reported as a conflict (see KnowledgeBase.problems).
    """
    override = os.environ.get("MITRA_KB_DIRS")
    if override:
        return [Path(p) for p in override.split(os.pathsep) if p]
    if BUNDLED_KB.is_dir():
        return [BUNDLED_KB, REPO_ROOT]
    siblings = sorted(p for p in WORKSPACE.glob("mitrapur_pradesh_*") if p.is_dir())
    return [REPO_ROOT, *siblings]


def seed_dir() -> Path | None:
    """Directory holding citizens_diverse.csv, the demo citizen records.

    Never defaults in production: demo citizens must not be reachable there. Set MITRA_SEED_DIR
    explicitly if you really want them, or plug in your own store (see CitizenStore).
    """
    override = os.environ.get("MITRA_SEED_DIR")
    if override:
        return Path(override)
    if is_production():
        return None
    return WORKSPACE / "mitrapur_pradesh_seed_and_grievances_2026" / "data" / "seed"


def today() -> date:
    """The 'as of' date used when a caller does not give one. MITRA_AS_OF=YYYY-MM-DD pins it."""
    override = os.environ.get("MITRA_AS_OF")
    return date.fromisoformat(override) if override else date.today()


def api_keys() -> frozenset[str]:
    """Accepted API keys from MITRA_API_KEYS (comma-separated)."""
    raw = os.environ.get("MITRA_API_KEYS", "")
    return frozenset(key.strip() for key in raw.split(",") if key.strip())


def cors_origins() -> list[str]:
    raw = os.environ.get("MITRA_CORS_ORIGINS", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
