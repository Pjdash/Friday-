# Not built or run in the environment this was written in (no Docker available there): build and smoke-test it
# in CI or locally before relying on it:  docker build -t mitra . && docker run --rm -e MITRA_API_KEYS=... -p 8000:8000 mitra
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MITRA_ENV=production

WORKDIR /app

# Dependencies first so this layer is cached until the lock file changes.
COPY requirements-prod.lock .
RUN pip install -r requirements-prod.lock

# Application and the bundled knowledge base (refresh it with scripts/sync_kb.py before building).
COPY mitra ./mitra
COPY kb ./kb

RUN useradd --system --uid 10001 --no-create-home mitra
USER mitra

EXPOSE 8000

# Liveness only; use /ready for orchestrator readiness (it fails when the knowledge base is unhealthy).
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"

# MITRA_API_KEYS must be supplied at runtime: the app refuses to start in production without it.
# One worker keeps memory low (the KB is small); scale with replicas. --proxy-headers trusts X-Forwarded-* from
# the load balancer in front of it.
CMD ["uvicorn", "mitra.api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--no-server-header"]
