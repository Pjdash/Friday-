# Deploying to Vercel

Goal: everything on Vercel (UI in `web/`, Python API in `mitra/`).

## Status

| | |
|---|---|
| UI built, type-checked, linted, production-built | done |
| UI verified against the real API locally (proxy, validation, rate limit, outage, 4 languages, mobile) | done |
| Python packaging for Vercel (`pyproject.toml`, `uv.lock`, `.python-version` = 3.12), 204 tests pass on 3.12 | done |
| `vercel.json` | **not written: see "Decision needed"** |
| Deployed | **no.** The Vercel CLI token on this machine is invalid; `vercel login` must be run by a person. |

## Decision needed: project layout

Vercel's *services* feature (one project, a Next.js service plus a FastAPI service, shared domain) is the
best fit: the API can stay private and be reached by the UI through an internal service binding.
The docs ([services](https://vercel.com/docs/services), [config reference](https://vercel.com/docs/services/config-reference))
show sibling roots (`frontend/`, `backend/`). They do not document keeping a nested folder out of a
service whose root is `.`. Here the API lives at the repo root with `web/` inside it, so choose one:

- **A. Move the API into `backend/`** (`mitra/`, `kb/`, `tests/`, `scripts/`, `pyproject.toml`, `uv.lock`,
  `.python-version`), keeping `web/` as is. Matches the documented layout. Cost: a large move of files
  that another branch (`feature/rag-pipeline`, worktree `Friday-rag-wt`) is also editing, so do it after
  that work merges.
- **B. Two Vercel projects from this repo**: UI with Root Directory `web`, API with Root Directory `.` and a
  `.vercelignore` excluding `web/`. No move needed. Cost: the API gets its own public URL, and if
  Deployment Protection is on, server-to-server calls from the UI are blocked unless a protection
  bypass secret is added to the proxy. The API key still guards it.

Recommendation: **A** once the RAG branch has merged, **B** if you need to deploy before that.

## Unverified until the first preview deploy

These come from docs that are silent, not from a test:

1. Path seen by FastAPI when the UI calls it over a binding (`new URL("chat", MITRA_API_URL)` should arrive as
   `/chat`). If a prefix appears, add a small ASGI prefix-stripping wrapper as the entrypoint.
2. Where `pyproject.toml` / `uv.lock` must sit relative to a service `root`.
3. That `kb/` ships inside the function bundle. The API refuses to start in production without a healthy KB,
   so a missing folder fails loudly (it will not serve wrong answers).

## RAG (LLM answers) on Vercel is a separate decision

`pyproject.toml` lists only the four production dependencies, so the deployed API runs the deterministic,
offline mode (keyword retrieval, official text quoted). The RAG pipeline merged on `production-hardening`
is opt-in: it needs the packages in `requirements-rag.txt`, provider keys (`GROQ_API_KEY`,
`GOOGLE_API_KEY`) and, if wanted, a switch (`MITRA_LLM`, `MITRA_EMBEDDINGS`). Turning it on means citizens'
question text is sent to those providers, which should be a deliberate, privacy-reviewed choice. The UI
already labels such answers (the `llm_generated` and `llm_not_found` flags).

## Environment variables

API service (production):

| Name | Value |
|---|---|
| `MITRA_ENV` | `production` (hides docs, requires keys, never loads demo citizens) |
| `MITRA_API_KEYS` | one or more long random keys, comma separated |
| `MITRA_AS_OF` | leave unset so "today" is real; set only to pin a date for a demo |

UI service: `MITRA_API_URL` (a binding injects it for services; otherwise the API's URL) and `MITRA_API_KEY`
(one of the API's keys). Both are server-side only. See `web/.env.example`.

## First deploy, in order

1. `vercel login`, then link the project(s).
2. Add the env vars above to Preview and Production.
3. Deploy a **preview** and run the smoke test.
4. Turn on Deployment Protection while it is a demo.

## Smoke test

```bash
curl -s https://<preview-url>/api/ready                 # 200, {"status":"ready","documents":37,...}
curl -s https://<preview-url>/api/schemes | jq length   # 3
curl -s -X POST https://<preview-url>/api/eligibility -H 'Content-Type: application/json' \
  -d '{"scheme_id":"SCH-PEN-01","profile":{"age":68,"annual_household_income":138000}}'   # outcome meets_criteria
```

## Before it is public

- Native-speaker review of the Hindi, Kannada and Tamil strings in `web/lib/i18n.ts`.
- Remove `robots: { index: false }` in `web/app/layout.tsx` when you decide to launch.
- Add a Vercel WAF rate-limit rule on `/api/*`. The in-app limiter is per instance and only a courtesy.
- Decide whether the backend's English rule text should be localised (backend change).
