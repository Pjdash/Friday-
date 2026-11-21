"""Embed the knowledge base now and write the cache, so the first user question is not the one that pays.

    python scripts/build_index.py [--env-file .env]

Run it at image build or deploy time. It is safe to repeat: only new or changed sections are embedded.
Exit status 1 means embeddings are unavailable (no key, package missing or provider error).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", help="load GOOGLE_API_KEY etc. from this file")
    args = parser.parse_args()
    if args.env_file:
        from dotenv import load_dotenv
        load_dotenv(args.env_file, override=False)

    from mitra import embeddings
    from mitra.kb import KnowledgeBase
    from mitra.retrieval import Retriever

    embedder = embeddings.default_embedder()
    if embedder is None:
        print("embeddings are unavailable: set GOOGLE_API_KEY, install requirements-rag.txt, "
              "and make sure MITRA_EMBEDDINGS is not off", file=sys.stderr)
        return 1
    retriever = Retriever(KnowledgeBase.load(), embedder, cache_path=embeddings.cache_dir())
    if not retriever.warm():
        print("the provider rejected the request; see the log line above for the error type", file=sys.stderr)
        return 1
    print(f"{len(retriever.chunks)} sections indexed with {embedder.model}; cache: {embeddings.cache_dir()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
