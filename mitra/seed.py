"""Demo citizen records (seed CSV). Stands in for a real citizen database."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from . import config


class CitizenStore:
    def __init__(self, records: dict[str, dict[str, Any]]):
        self._records = records

    @classmethod
    def load(cls, directory: Path | None = None) -> "CitizenStore":
        directory = directory or config.seed_dir()
        if directory is None:  # production default: no demo citizens
            return cls({})
        path = directory / "citizens_diverse.csv"
        if not path.exists():
            return cls({})
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return cls({row["citizen_id"]: row for row in csv.DictReader(handle)})

    def get(self, citizen_id: str) -> dict[str, Any] | None:
        return self._records.get(citizen_id)

    @staticmethod
    def has_consent(record: dict[str, Any]) -> bool:
        # POL-PRV-01 section 2: sensitive data is used only with the applicant's informed consent.
        return str(record.get("consent_given", "")).strip().upper() == "Y"

    def __len__(self) -> int:
        return len(self._records)
