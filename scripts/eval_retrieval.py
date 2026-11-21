"""Compare keyword-only and hybrid retrieval on a fixed question set, and calibrate the similarity floor.

    python scripts/eval_retrieval.py                       # keyword baseline only (offline)
    python scripts/eval_retrieval.py --env-file .env       # also hybrid, using the keys in that file
    python scripts/eval_retrieval.py --env-file .env --min-sim 0.6

A question counts as answered when any acceptable source is in the top 3. Out-of-scope questions must
return nothing. The acceptable sets are judgement calls (translations and circulars often answer the
same question), so read the per-question lines, not just the totals.

The last section prints the best dense similarity for in-scope and out-of-scope questions. Choose
MITRA_DENSE_MIN_SIM between the highest out-of-scope value and the lowest in-scope value.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PEN = {"GL-PEN-01", "HI-PEN-01", "KN-PEN-01", "TA-PEN-01"}
FRM = {"GL-FRM-01", "GL-FRM-02", "HI-FRM-01", "TA-FRM-01"}
FRAUD = {"POL-FEE-01", "CIR-2026-09", "HI-FRAUD-01", "KN-FRAUD-01", "TA-FRAUD-01"}

# (question, language, acceptable source ids; None = out of scope, expect no result)
QUERIES: list[tuple[str, str, set[str] | None]] = [
    ("How much monthly pension will I get?", "en", PEN),
    ("What is the income limit for old age pension now?", "en", PEN | {"CIR-2026-01"}),
    ("How much is the drip irrigation subsidy?", "en", {"GL-FRM-02", "HI-FRM-01", "TA-FRM-01"}),
    ("What is the last date to apply for the Balika Vidya scholarship?", "en",
     {"CIR-2026-02", "GL-EDU-01", "MIX-NOT-01", "HI-EDU-01", "TA-EDU-01"}),
    ("Can I still enrol in the Shramik Suraksha insurance scheme?", "en", {"CIR-2026-04", "GL-INS-01"}),
    ("Is a digital land passbook accepted as land proof for the irrigation scheme?", "en", {"CIR-2026-08"}),
    ("How do I appeal if my application is rejected?", "en", {"POL-GRV-01"}),
    ("What must be printed on a school bonafide certificate?", "en", {"CIR-2026-12"}),
    ("What is the closing date for the rural housing grant?", "en", {"CIR-2026-06", "GL-HOU-01"}),
    # GL-HOU-01 itself expired on 2026-11-20 (valid_until), so only the closing circular is in force today.
    ("How is the housing grant paid in instalments?", "en", {"GL-HOU-01", "CIR-2026-06"}),
    ("Can my personal data be used without my consent?", "en", {"POL-PRV-01"}),
    ("monthly money from the government for elderly people", "en", PEN),
    ("someone called asking for my one time code to approve my scheme", "en", FRAUD),
    ("वृद्धजन पेंशन की आय सीमा क्या है?", "hi", PEN | {"CIR-2026-01"}),
    ("किसान को साल में कितना पैसा मिलता है?", "hi", FRM),
    ("ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿಗೆ ಆದಾಯ ಮಿತಿ ಎಷ್ಟು?", "kn", PEN | {"CIR-2026-01"}),
    ("ಪಿಂಚಣಿ ಮೊತ್ತ ಎಷ್ಟು?", "kn", PEN),
    ("முதியோர் ஓய்வூதியம் மாதம் எவ்வளவு?", "ta", PEN),
    ("விவசாயிகளுக்கு எவ்வளவு உதவி கிடைக்கும்?", "ta", FRM),
    ("Can I get a loan for a tractor?", "en", None),
    ("who won the cricket world cup", "en", None),
    ("What is the weather in Mitrapur tomorrow?", "en", None),
    ("How do I renew my driving licence?", "en", None),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", help="load GOOGLE_API_KEY etc. from this file")
    parser.add_argument("--min-sim", type=float, help="dense similarity floor to evaluate (default: the built-in)")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()

    if args.env_file:
        from dotenv import load_dotenv
        load_dotenv(args.env_file, override=False)

    from mitra import embeddings
    from mitra.kb import KnowledgeBase
    from mitra.retrieval import Retriever

    kb = KnowledgeBase.load()
    keyword = Retriever(kb)
    embedder = embeddings.default_embedder() if args.env_file else None
    hybrid = Retriever(kb, embedder, cache_path=embeddings.cache_dir(), dense_min_sim=args.min_sim)
    use_hybrid = embedder is not None and hybrid.warm()
    print(f"{len(kb)} documents, {len(keyword.chunks)} chunks; hybrid: {'on' if use_hybrid else 'OFF (keyword baseline only)'}")
    if args.env_file and not use_hybrid:
        print("  embeddings were requested but are unavailable: check the key, the model name and the network")

    def run(retriever: Retriever, query: str, lang: str) -> list[str]:
        return [h.doc.source_id for h in retriever.search(query, args.as_of, language=lang, k=3)]

    totals = {"keyword": [0, 0, 0], "hybrid": [0, 0, 0]}  # [behaved as expected, asked, top-1 correct]
    in_scope = sum(accept is not None for _, _, accept in QUERIES)
    for query, lang, accept in QUERIES:
        row = []
        for name, retriever in (("keyword", keyword), ("hybrid", hybrid if use_hybrid else None)):
            if retriever is None:
                continue
            got = run(retriever, query, lang)
            ok = (not got) if accept is None else bool(set(got) & accept)
            totals[name][0] += ok
            totals[name][1] += 1
            totals[name][2] += accept is not None and bool(got) and got[0] in accept
            row.append(f"{name}: {'PASS' if ok else 'FAIL'} {got}")
        print(f"[{lang}] {query[:58]:58} | " + " | ".join(row))
    print()
    for name, (passed, asked, top1) in totals.items():
        if asked:
            print(f"{name:8} {passed}/{asked} behaved as expected (acceptable source in top 3, or nothing for "
                  f"out-of-scope); first result correct for {top1}/{in_scope} in-scope questions")

    if use_hybrid:
        print("\nBest dense similarity per question (in-scope should be above the floor, out-of-scope below):")
        best = {"in": [], "out": []}
        index = hybrid._dense_index()
        for query, lang, accept in QUERIES:
            top = max(index.similarities(query))
            best["out" if accept is None else "in"].append(top)
            print(f"  {top:5.3f}  {'out' if accept is None else 'in '}  {query[:60]}")
        low_in, high_out = min(best["in"]), max(best["out"])
        print(f"\nlowest in-scope {low_in:.3f}, highest out-of-scope {high_out:.3f}; floor in use {hybrid._min_sim:.2f}")
        if low_in > high_out:
            print(f"suggested MITRA_DENSE_MIN_SIM = {(low_in + high_out) / 2:.2f}")
        else:
            print("the two ranges overlap: no single floor separates them; keep the floor high and rely on NOT_FOUND")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
