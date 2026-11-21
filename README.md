# MitraSeva scheme assistant

A citizen-facing assistant for Mitrapur Pradesh welfare schemes. It answers from the official guidelines,
policies and circulars, applying the rules **in force on a given date**, and never claims a final decision:
the implementing department decides.

Covered for automated eligibility and document checks: Kisan Samriddhi Yojana (`SCH-FRM-01`), Krishi Sinchai
Sahayata (`SCH-FRM-02`), Vriddhjan Pension Yojana (`SCH-PEN-01`). Questions about any other scheme in the
knowledge base are answered with the official text and a clear notice that no automated check exists yet.

Everything is deterministic and offline: no LLM and no network calls.

## Quick start (development)

```
python -m venv venv && venv\Scripts\activate          # Windows; use source venv/bin/activate elsewhere
pip install -r requirements-dev.txt
python -m pytest -q
python -m mitra ask "I am 64 years old with income of Rs 1,35,000. Am I eligible for the pension?"
python -m mitra ask "Which schemes am I eligible for?" --citizen C1021   # demo citizen, dev only
python -m mitra serve --port 8000                                       # API, interactive docs at /docs
python -m mitra kb                                                      # knowledge-base health check
```

`requirements.txt` is the project-wide list (LangChain, Groq and Gemini providers, Chroma, FAISS, ...). The
assistant needs only `requirements-dev.txt` (tests) or `requirements-prod.lock` (runtime) and then answers from
offline keyword search. Embedding-based retrieval and LLM-worded answers are optional: add `requirements-rag.txt`
and API keys (see [RAG.md](RAG.md)); without them the assistant behaves exactly as before.

The code reads configuration from process environment variables only. It does **not** load `.env`, so values in a
`.env` file take effect only if your shell or `docker run --env-file .env` exports them.

## Running in production

```
docker build -t mitra .
docker run -d -e MITRA_API_KEYS=<key1>,<key2> -p 8000:8000 mitra
```

The Dockerfile has not been built in the environment this was written in (no Docker there). CI builds it and
smoke-tests auth and readiness (`.github/workflows/ci.yml`); confirm that run before relying on it.

| Variable | Default | Meaning |
|---|---|---|
| `MITRA_ENV` | `development` | `production` refuses to start without API keys or with an unhealthy KB, hides `/docs`, and never loads demo citizens. |
| `MITRA_API_KEYS` | none | Comma-separated keys, sent as `X-API-Key`. With none (development only) the API is open and logs a warning. |
| `MITRA_KB_DIRS` | bundled `kb/` | `os.pathsep`-separated directories of knowledge-base documents. |
| `MITRA_SEED_DIR` | dev: sibling seed folder; production: none | Directory with `citizens_diverse.csv`. |
| `MITRA_AS_OF` | today | Pin the "as of" date (testing and demos). |
| `MITRA_CORS_ORIGINS` | none (CORS off) | Comma-separated allowed origins. |
| `MITRA_ALLOW_TRACING` | unset | Set to `1` to allow LangSmith tracing. Off by default, see Privacy. |

Rotate keys by adding the new key to the list, deploying, moving clients over, then removing the old one.
Terminate TLS and apply rate limiting at the gateway or load balancer; neither is done in the app.

Use `/health` for liveness and `/ready` for readiness. `/ready` returns 503 when a document the rules cite is
missing or two copies of a document disagree.

## API

All endpoints except `/health` and `/ready` need `X-API-Key`. Send `X-Request-ID` (letters, digits, `-`, `_`,
up to 64) to correlate logs; it is echoed back, or generated.

| Endpoint | Purpose |
|---|---|
| `GET /schemes` | The schemes with automated checks. |
| `POST /eligibility` | `{scheme_id, citizen_id \| profile, as_of?}` returns a verdict: `meets_criteria`, `does_not_meet`, `needs_info` or `not_open`, with per-condition results, the documents to bring, and the circulars that changed each limit. |
| `POST /chat` | `{message, citizen_id? \| profile?, language?, as_of?}` returns `{text, intent, scheme_id, escalate_to, citations, flags, needs, verdicts}`. |

Errors: 401 bad key, 403 no recorded consent, 404 unknown scheme or citizen, 422 invalid input, 500 generic
(`request_id` in the body, details only in the log).

`escalate_to` (`fraud_desk`, `human_review`) is a **signal for the host application**. This service does not file
fraud reports or grievance tickets, and its answers never say it did.

## How answers are decided

- **Precedence (`POL-PRV-01`).** A document is in force on a date only if its `effective_from`/`valid_until`
  window covers it and no later authoritative document `supersedes` it. A later circular overrides the
  conflicting clause of its guideline; other clauses stay. Example: the pension income cap is ₹1,20,000 until
  2026-09-09 and ₹1,50,000 from 2026-09-10 (`CIR-2026-01`).
- **Authority.** Only guidelines, policies, amendments and circulars count. Resolved grievances and FAQs are
  informational: grievances are never retrievable, so their stale answers cannot reach a citizen.
- **Rules live in `mitra/schemes.py`**, each citing its source document. `tests/test_drift.py` checks every
  threshold, benefit, department and document list against the markdown, so an edited guideline fails the tests
  instead of silently leaving the code out of date. Circular dates are read from the circular's own front matter.
- **Safety.** Fraud, bribe, OTP and fee-demand text in English, Hindi, Kannada, Tamil and Hinglish gets the
  official anti-fraud answer and `escalate_to=fraud_desk`. Sentences that try to instruct the assistant
  ("ignore previous instructions...") are removed before anything else runs, so they cannot change a verdict.
- **Consent.** A saved citizen record is used only if `consent_given` is `Y`.

## Updating the knowledge base

1. Put the new or changed markdown in the source folders and run `python scripts/sync_kb.py` (or pass
   directories). It copies into `kb/`, then exits non-zero if a cited document is missing or copies conflict.
2. Run `python -m pytest -q`. If a circular changed a number, the drift tests fail until `mitra/schemes.py` is
   updated to match.
3. Rebuild and deploy the image.

To add a scheme, add a `Scheme` to `mitra/schemes.py` (rules, overrides, document notes), add it to `SCHEMES`,
and add its numbers to the drift tests' expectations. Deadline and open/closed windows are not modelled yet.

## Privacy

- Logs are JSON and carry metadata only (route, status, intent, scheme, flags, timings, request id). They never
  contain message text, profile values or citizen ids; `tests/test_api.py` asserts this.
- LangGraph can upload traces, inputs included, to LangSmith. `mitra/__init__.py` forces tracing off unless
  `MITRA_ALLOW_TRACING=1`.
- With the optional RAG layer on, the sanitised text of an information question is sent to the embedding provider
  (Gemini) and the LLM provider (Groq or Gemini), with phone/Aadhaar/OTP-like digit runs and e-mail addresses masked
  first. Profiles, citizen ids and eligibility questions are never sent. Set `MITRA_EMBEDDINGS=off` and
  `MITRA_LLM=off` (or supply no keys) if citizens' text must not leave your infrastructure. LangSmith tracing stays
  forced off (above), so these calls are not traced either.
- Demo citizens exist only for development and tests. In production wire your own store: anything with a
  `get(citizen_id)` returning a record and the `CitizenStore.has_consent` check.
- Responses are `Cache-Control: no-store`.

## Known limits

- Automated checks cover 3 of the 8 schemes. The other five (`EDU-01`, `EDU-02`, `DIS-01`, `HOU-01`, `INS-01`)
  need rule definitions plus open/closed and deadline handling for circulars like `CIR-2026-02/04/05/06`.
- Eligibility detail lines are English. Only the disclaimer, fee and fraud text are localised, using the official
  Hindi, Kannada and Tamil sentences from the knowledge base. Native-speaker review is still advisable.
- Offline retrieval is BM25: it does not match across languages and relies on scheme names and a same-language
  boost. Optional embeddings (RAG.md) address that, but their quality is unmeasured until `scripts/eval_retrieval.py`
  has been run with real keys.
- Free-text extraction is conservative (for example "I am 64" is not read as an age); missing facts are asked for.
- Fraud detection is keyword-based and favours false alarms over misses. It agreed with all 25 labelled
  grievances, but the keyword lists were written after seeing them, so it is not a held-out result.
- Data gaps in the supplied files: a grievance cites `POL-SLA-01` (45-day rule), which is not in the knowledge
  base and is therefore never quoted; seeded applications reference citizens `C1017`/`C1018`, who have no records.
- One process, in-memory only; no persistence, rate limiting or ticketing integration.

## Layout

```
mitra/        kb, precedence, schemes, eligibility, retrieval, safety, extract, i18n, agent (LangGraph), api, cli
kb/           bundled knowledge base (refresh with scripts/sync_kb.py)
tests/        unit, drift, API and privacy tests; fixtures/ holds demo citizens and resolved grievances
scripts/      sync_kb.py
Dockerfile, requirements-prod.txt / .lock, requirements-dev.txt, .github/workflows/ci.yml
```
