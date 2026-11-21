"""FastAPI service. Run with:  uvicorn mitra.api:app

Security model
  * Every endpoint except /health and /ready requires an X-API-Key from MITRA_API_KEYS.
  * MITRA_ENV=production refuses to start without keys, hides the interactive docs, and never loads
    demo citizens. Without keys outside production the API is open and logs a loud warning.
  * Logs carry metadata only (see logging_setup), never message text, profile values or citizen ids.
  * `escalate_to` in a chat response is a signal for the host application; this service does not
    file fraud reports or grievance tickets.
"""
from __future__ import annotations

import hmac
import logging
import re
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import date
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from . import config
from .agent import Assistant
from .eligibility import evaluate
from .logging_setup import configure as configure_logging
from .logging_setup import request_id_var
from .schemes import SCHEMES, required_source_ids
from .seed import CitizenStore

log = logging.getLogger("mitra.api")
_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

ProfileValue = str | int | float | None


class _ProfileMixin(BaseModel):
    profile: dict[str, ProfileValue] | None = Field(default=None, max_length=20)
    citizen_id: str | None = Field(default=None, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")

    @field_validator("profile")
    @classmethod
    def _short_values(cls, profile):
        for key, value in (profile or {}).items():
            if len(key) > 64 or (isinstance(value, str) and len(value) > 100):
                raise ValueError("profile keys and values must be short")
        return profile


class ChatRequest(_ProfileMixin):
    message: str = Field(min_length=1, max_length=2000)
    language: str | None = Field(default=None, pattern="^(en|hi|kn|ta)$")
    as_of: date | None = None


class EligibilityRequest(_ProfileMixin):
    scheme_id: str = Field(max_length=32)
    as_of: date | None = None


def create_app(*, api_keys: frozenset[str] | set[str] | None = None, production: bool | None = None,
               cors_origins: list[str] | None = None, assistant: Assistant | None = None) -> FastAPI:
    """Build the app. Arguments default to the environment (see README); tests pass them explicitly."""
    keys = config.api_keys() if api_keys is None else frozenset(api_keys)
    prod = config.is_production() if production is None else production
    origins = config.cors_origins() if cors_origins is None else cors_origins
    if prod and not keys:
        raise RuntimeError("MITRA_ENV=production requires at least one key in MITRA_API_KEYS.")
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.assistant = assistant if assistant is not None else Assistant()
        problems = app.state.assistant.kb.problems(required_source_ids())
        app.state.problems = problems
        if problems:
            log.error("knowledge base is not healthy", extra={"problems": problems})
            if prod:
                raise RuntimeError("Refusing to start: " + "; ".join(problems))
        if not keys:
            log.warning("API authentication is DISABLED: set MITRA_API_KEYS before exposing this service")
        log.info("started", extra={"documents": len(app.state.assistant.kb), "auth": bool(keys),
                                   "production": prod, "citizens_loaded": len(app.state.assistant.citizens)})
        yield

    app = FastAPI(
        title="MitraSeva scheme assistant", version="1.0.0", lifespan=lifespan,
        docs_url=None if prod else "/docs", redoc_url=None, openapi_url=None if prod else "/openapi.json")

    def require_key(request: Request) -> None:
        if not keys:
            return
        supplied = request.headers.get("x-api-key", "").encode()
        if not any(hmac.compare_digest(supplied, key.encode()) for key in keys):
            raise HTTPException(401, "Missing or invalid API key.", headers={"WWW-Authenticate": "ApiKey"})

    protected = [Depends(require_key)]

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        inbound = request.headers.get("x-request-id", "")
        request_id = inbound if _REQUEST_ID.match(inbound) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception as exc:  # noqa: BLE001 - last line of defence, details stay in the log
                log.exception("unhandled error", extra={"error_type": type(exc).__name__})
                response = JSONResponse({"detail": "Internal server error.", "request_id": request_id},
                                        status_code=500)
            response.headers["X-Request-ID"] = request_id
            response.headers["Cache-Control"] = "no-store"  # responses can contain personal data
            response.headers["X-Content-Type-Options"] = "nosniff"
            log.info("request", extra={"method": request.method, "path": request.url.path,
                                       "status": response.status_code,
                                       "duration_ms": round((time.perf_counter() - started) * 1000, 1)})
            return response
        finally:
            request_id_var.reset(token)

    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"],
                           allow_headers=["X-API-Key", "Content-Type", "X-Request-ID"], allow_credentials=False)

    def resolve_profile(request: Request, citizen_id: str | None, profile: dict[str, Any] | None) -> dict[str, Any]:
        if profile:
            return profile
        if citizen_id:
            record = request.app.state.assistant.citizens.get(citizen_id)
            if record is None:
                raise HTTPException(404, "Unknown citizen_id.")
            if not CitizenStore.has_consent(record):
                raise HTTPException(403, "Consent is not recorded for this citizen (POL-PRV-01).")
            return record
        raise HTTPException(422, "Provide either profile or citizen_id.")

    @app.get("/health")
    def health() -> dict[str, str]:
        """Liveness: the process is up. Says nothing about the knowledge base (see /ready)."""
        return {"status": "ok"}

    @app.get("/ready")
    def ready(request: Request) -> JSONResponse:
        """Readiness: 200 only when every document the rules cite is loaded and unambiguous."""
        problems = request.app.state.problems
        if problems:
            return JSONResponse({"status": "not_ready", "problems": problems}, status_code=503)
        return JSONResponse({"status": "ready", "documents": len(request.app.state.assistant.kb),
                             "as_of": config.today().isoformat()})

    @app.get("/schemes", dependencies=protected)
    def schemes() -> list[dict[str, str]]:
        return [{"scheme_id": s.scheme_id, "name": s.name, "department": s.department, "benefit": s.benefit}
                for s in SCHEMES.values()]

    @app.post("/eligibility", dependencies=protected)
    def eligibility(req: EligibilityRequest, request: Request) -> dict[str, Any]:
        if req.scheme_id not in SCHEMES:
            raise HTTPException(404, "Unknown scheme_id.")
        raw = resolve_profile(request, req.citizen_id, req.profile)
        try:
            verdict = evaluate(req.scheme_id, raw, request.app.state.assistant.kb, req.as_of or config.today())
        except (ValueError, TypeError) as exc:
            raise HTTPException(422, f"Invalid profile: {exc}") from exc
        log.info("eligibility", extra={"scheme_id": req.scheme_id, "outcome": verdict.outcome})
        return asdict(verdict)

    @app.post("/chat", dependencies=protected)
    def chat(req: ChatRequest, request: Request) -> dict[str, Any]:
        try:
            answer = request.app.state.assistant.ask(
                req.message, citizen_id=req.citizen_id, profile=req.profile, as_of=req.as_of, language=req.language)
        except (ValueError, TypeError) as exc:
            raise HTTPException(422, f"Invalid input: {exc}") from exc
        log.info("chat", extra={"intent": answer.intent, "scheme_id": answer.scheme_id, "language": answer.language,
                                "flags": answer.flags, "citations": len(answer.citations)})
        if answer.escalate_to:
            log.warning("escalation", extra={"escalate_to": answer.escalate_to, "intent": answer.intent})
        return answer.to_dict()

    return app


app = create_app()
