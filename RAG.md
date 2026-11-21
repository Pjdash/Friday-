# Retrieval-augmented answers

Information questions ("what is the income limit?", "when does it close?") are answered in three stages.
Eligibility checks, document lists, fee answers, appeals and fraud handling stay deterministic and never reach a model.

```
question -> sanitize -> fraud check -> classify -> info
                                                    |
        1. retrieve   BM25 keywords + Gemini embeddings, fused (reciprocal rank)
        2. generate   Groq, else Gemini, words an answer from the retrieved passages
        3. verify     reject the reply unless every citation and every number is in the passages
                      -> otherwise quote the official text (the offline behaviour)
```

Each stage degrades on its own. No key, a missing package, a provider outage or a rejected reply each fall back
one step, down to keyword retrieval that quotes the official text, which needs no network at all.

## Guarantees that do not depend on the model

* **Filters come first.** Documents not in force on the date, other schemes' documents and resolved grievances are
  excluded before ranking, so embeddings cannot surface them. A later circular that amends a clause is sent to the
  model as `LATER AMENDMENT` and listed in the citations.
* **Numbers and sources are checked.** A reply is discarded if it cites a source that was not retrieved, cites
  nothing, or contains an amount, limit, day count or year found in neither the passages nor the question.
* **Citations and the disclaimer are not the model's.** The citation list comes from retrieval; the localised
  "department makes the final decision" line is always appended by the code.
* **Out-of-scope questions get "not found".** Dense matches need a similarity floor, and the model is told to answer
  `NOT_FOUND` when the passages do not help.
* **Privacy.** Only the sanitised question text and public knowledge-base passages are sent to a provider; phone,
  Aadhaar/OTP-like digit runs and e-mail addresses are masked first. Profiles and citizen ids never leave the process.
  Logs hold metadata only; queries are never cached.

## Setup

```
pip install -r requirements-rag.txt
export GOOGLE_API_KEY=...       # embeddings and Gemini answers
export GROQ_API_KEY=...         # Groq answers (optional; Gemini alone is enough)
python scripts/build_index.py   # optional: embed the KB now instead of on the first question
python scripts/eval_retrieval.py     # compare keyword vs hybrid, calibrate the floor
```

The package reads process environment variables only and never loads `.env` (see the README). The two scripts accept
`--env-file path/to/.env` if you keep the keys in a file. `mitra/__init__.py` keeps LangSmith tracing off, so
the provider calls made here are not traced.

The production image installs `requirements-prod.lock`, which does not contain the provider packages, so it runs
keyword-only (and logs why) until you add `requirements-rag.txt` to the image and regenerate the lock.

| Variable | Default | Purpose |
|---|---|---|
| `MITRA_EMBEDDINGS` | `auto` | `off` disables dense retrieval |
| `MITRA_LLM` | `auto` | `off` disables model-written answers |
| `MITRA_LLM_PROVIDERS` | `groq,gemini` | order tried; a provider without a key is skipped |
| `MITRA_GROQ_MODEL` / `MITRA_GEMINI_MODEL` | `llama-3.3-70b-versatile` / `gemini-2.5-flash` | chat models |
| `MITRA_EMBED_MODEL` / `MITRA_EMBED_DIMENSIONS` | `gemini-embedding-001` / `768` | embedding model |
| `MITRA_DENSE_MIN_SIM` | `0.62` | similarity a section needs to be offered on meaning alone |
| `MITRA_LLM_TIMEOUT` / `MITRA_EMBED_TIMEOUT` | `20` | seconds |
| `MITRA_CACHE_DIR` | `.cache/mitra` | embedding cache (content-hashed, per model) |

## Not yet verified against the real providers

The model names and the `0.62` similarity floor are defaults, not measurements. They were written without a working API
key, so the test suite uses fakes. Before relying on this in production, run `scripts/eval_retrieval.py` (with the keys
exported, or `--env-file`):
it reports keyword vs hybrid results on 23 questions in four languages and suggests a floor for `MITRA_DENSE_MIN_SIM`.
If a model name has been retired, set `MITRA_GROQ_MODEL` / `MITRA_GEMINI_MODEL`; until then answers fall back to quoting.
