"""Locations and defaults. Every path can be overridden with an environment variable."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = REPO_ROOT.parent


def kb_dirs() -> list[Path]:
    """Directories scanned for knowledge-base documents.

    Order matters: when two copies of a document share a source_id and last_updated,
    the earlier directory wins. MITRA_KB_DIRS (os.pathsep-separated) overrides the default.
    """
    override = os.environ.get("MITRA_KB_DIRS")
    if override:
        return [Path(p) for p in override.split(os.pathsep) if p]
    siblings = sorted(p for p in WORKSPACE.glob("mitrapur_pradesh_*") if p.is_dir())
    return [REPO_ROOT, *siblings]


def seed_dir() -> Path:
    """Directory holding citizens_diverse.csv (demo citizen records)."""
    override = os.environ.get("MITRA_SEED_DIR")
    if override:
        return Path(override)
    return WORKSPACE / "mitrapur_pradesh_seed_and_grievances_2026" / "data" / "seed"


def today() -> date:
    """The 'as of' date used when a caller does not give one. MITRA_AS_OF=YYYY-MM-DD pins it."""
    override = os.environ.get("MITRA_AS_OF")
    return date.fromisoformat(override) if override else date.today()
