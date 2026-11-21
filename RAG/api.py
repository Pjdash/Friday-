"""FastAPI service. Run with:  uvicorn mitra.api:app

`escalate_to` in responses is a signal for the host application; this service does not file
fraud reports or grievance tickets.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import date
from functools import lru_cache
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import config
from .agent import Assistant
from .eligibility import evaluate
from .schemes import SCHEMES
from .seed import CitizenStore

app = FastAPI(title="MitraSeva scheme assistant", version="0.1.0")


@lru_cache(maxsize=1)
def assistant() -> Assistant:
    return Assistant()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    citizen_id: str | None = None
    profile: dict[str, Any] | None = None
    language: str | None = Field(default=None, pattern="^(en|hi|kn|ta)$")
    as_of: date | None = None


class EligibilityRequest(BaseModel):
    scheme_id: str
    citizen_id: str | None = None
    profile: dict[str, Any] | None = None
    as_of: date | None = None


def _resolve_profile(citizen_id: str | None, profile: dict[str, Any] | None) -> dict[str, Any]:
    if profile:
        return profile
    if citizen_id:
        record = assistant().citizens.get(citizen_id)
        if record is None:
            raise HTTPException(404, f"Unknown citizen_id {citizen_id!r}")
        if not CitizenStore.has_consent(record):
            raise HTTPException(403, "Consent is not recorded for this citizen (POL-PRV-01).")
        return record
    raise HTTPException(422, "Provide either profile or citizen_id.")


@app.get("/health")
def health() -> dict[str, Any]:
    kb = assistant().kb
    return {"status": "ok", "documents": len(kb), "conflicts": len(kb.conflicts), "as_of": config.today().isoformat()}


@app.get("/schemes")
def schemes() -> list[dict[str, str]]:
    return [{"scheme_id": s.scheme_id, "name": s.name, "department": s.department, "benefit": s.benefit}
            for s in SCHEMES.values()]


@app.post("/eligibility")
def eligibility(req: EligibilityRequest) -> dict[str, Any]:
    if req.scheme_id not in SCHEMES:
        raise HTTPException(404, f"Unknown scheme_id {req.scheme_id!r}")
    raw = _resolve_profile(req.citizen_id, req.profile)
    try:
        verdict = evaluate(req.scheme_id, raw, assistant().kb, req.as_of or config.today())
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, f"Invalid profile: {exc}") from exc
    return asdict(verdict)


@app.post("/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    try:
        answer = assistant().ask(req.message, citizen_id=req.citizen_id, profile=req.profile,
                                 as_of=req.as_of, language=req.language)
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, f"Invalid input: {exc}") from exc
    return answer.to_dict()
