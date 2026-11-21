"""Structured JSON logging with a per-request id.

Privacy rule: log *metadata* only (route, status, intent, scheme, flags, timings). Never log the
citizen's message, profile values or citizen id. POL-PRV-01 limits personal data to eligibility
checks, benefit release, audit and grievance redressal, and application logs are none of those.
"""
from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        payload.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure(level: str = "INFO") -> None:
    """Route the 'mitra' logger tree to stdout as JSON. Safe to call more than once."""
    logger = logging.getLogger("mitra")
    if any(getattr(h, "_mitra", False) for h in logger.handlers):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler._mitra = True  # type: ignore[attr-defined]
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False
