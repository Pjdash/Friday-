"""Command line:  python -m mitra ask "..." [--citizen C1021] [--as-of 2026-11-21] | serve | kb"""
from __future__ import annotations

import argparse
import sys
from datetime import date


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy codepage
    parser = argparse.ArgumentParser(prog="mitra")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="ask the assistant a question")
    ask.add_argument("message")
    ask.add_argument("--citizen", help="demo citizen id, e.g. C1021")
    ask.add_argument("--as-of", type=date.fromisoformat, help="evaluate rules as of YYYY-MM-DD (default: today)")
    ask.add_argument("--language", choices=["en", "hi", "kn", "ta"])

    serve = sub.add_parser("serve", help="run the FastAPI server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    sub.add_parser("kb", help="summarise the loaded knowledge base")
    args = parser.parse_args(argv)

    if args.command == "serve":
        import uvicorn
        uvicorn.run("mitra.api:app", host=args.host, port=args.port)
        return 0

    from .agent import Assistant
    assistant = Assistant()
    if args.command == "kb":
        from collections import Counter
        from .schemes import required_source_ids
        print(f"{len(assistant.kb)} documents:", dict(Counter(d.doc_type for d in assistant.kb)))
        for source_id, paths in assistant.kb.conflicts:
            print(f"CONFLICT {source_id}: {paths[0]} vs {paths[1]}")
        problems = assistant.kb.problems(required_source_ids())
        for problem in problems:
            print(f"PROBLEM: {problem}")
        return 1 if problems else 0

    answer = assistant.ask(args.message, citizen_id=args.citizen, as_of=args.as_of, language=args.language)
    print(answer.text)
    print(f"\n[intent={answer.intent} scheme={answer.scheme_id} lang={answer.language} "
          f"escalate_to={answer.escalate_to} flags={answer.flags}]")
    print("Sources:", ", ".join(answer.citations) or "-")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
