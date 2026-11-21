# MitraSeva web

Citizen-facing UI for the MitraSeva scheme assistant (the Python API in the repo root). Next.js (App
Router), TypeScript, Tailwind. Four languages: English, Hindi, Kannada, Tamil.

> This is Next.js 16 with Cache Components. APIs differ from older versions: read the guides in
> `node_modules/next/dist/docs/` before changing framework-level code (see `AGENTS.md`).

## What it does

| Page | Purpose |
|---|---|
| `/` | Scheme list (from the API), fee and OTP safety notice |
| `/check` | Eligibility form. Per scheme: outcome, how each rule was checked, documents to bring, printable |
| `/chat` | Ask the assistant. Shows fraud/review escalation banners and asks only for details it needs |
| `/about` | How it works, privacy, the official wording |

## Architecture

```
Browser -> Next.js route handlers (app/api/*)  -> Mitra FastAPI
           validate, rate limit, add X-API-Key    deterministic rules + KB
```

The browser never talks to the Mitra API. The route handlers in `app/api/` validate the request with
zod (`lib/schemas.ts`), rate limit, attach `MITRA_API_KEY`, and map failures to a small vocabulary
(`unavailable`, `rate_limited`, `invalid`, `upstream`, `not_found`). Raw upstream errors are never
forwarded.

Design rules worth keeping:

- **Official wording is not re-translated.** The fee, OTP and final-decision sentences in
  `lib/i18n.ts` (`OFFICIAL`) are copied from `mitra/i18n.py`. Keep them in sync.
- **The UI never claims an action happened.** `escalate_to` is only a signal; the banner tells the
  citizen what to do themselves.
- **No personal data at rest.** Profile details live in component state only. The only thing in
  `localStorage` is the language choice. The proxy does not log bodies, and rejects `citizen_id`
  so saved demo records cannot be read through the UI.
- **Rule text from the backend is English.** It is shown as is, marked `lang="en"`, with a note in
  the other languages. Localising it is a backend change.
- **Types mirror the backend** (`lib/types.ts`). Change them first when the API shape changes.

## Local development

```bash
# 1. API (repo root). Pick a port that is free; 8000 may be taken by something else.
MITRA_API_KEYS=local-test-key python -m mitra serve --port 8765

# 2. UI
cd web
cp .env.example .env.local        # set MITRA_API_URL=http://127.0.0.1:8765, MITRA_API_KEY=local-test-key
npm install
npm run dev
```

Checks: `npx tsc --noEmit`, `npm run lint`, `npm run build`.

## Adding or changing text

Every language must define every key (`Messages` type in `lib/i18n.ts`), so a missing translation
fails the type check. The hi/kn/ta strings have not had a native-speaker review yet.

## Deployment

See the notes in the repo root `DEPLOY.md`.
