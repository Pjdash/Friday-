"""Copy the published knowledge base into kb/ so the service is self-contained.

    python scripts/sync_kb.py                      # from the sibling mitrapur_pradesh_* folders
    python scripts/sync_kb.py path/to/dir ...      # from specific directories

Only markdown files with a source_id in their front matter are copied. After copying, the bundled
KB is loaded and checked: the script exits non-zero if a required document is missing or two copies
of a document disagree, so a bad drop of circulars cannot reach the image unnoticed.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mitra import config  # noqa: E402
from mitra.kb import KnowledgeBase, parse_front_matter  # noqa: E402
from mitra.schemes import required_source_ids  # noqa: E402

DEFAULT_SOURCES = ("mitrapur_pradesh_kb_guidelines_policies", "mitrapur_pradesh_circulars_2026",
                   "mitrapur_pradesh_multilingual_2026")


def main(argv: list[str]) -> int:
    sources = [Path(a) for a in argv] or [config.WORKSPACE / name for name in DEFAULT_SOURCES]
    target = config.BUNDLED_KB
    target.mkdir(exist_ok=True)
    copied, unchanged = 0, 0
    for source in sources:
        if not source.is_dir():
            print(f"skip (not a directory): {source}")
            continue
        for path in sorted(source.glob("*.md")):
            text = path.read_text(encoding="utf-8-sig")
            if not parse_front_matter(text)[0].get("source_id"):
                continue
            destination = target / path.name
            if destination.exists() and destination.read_text(encoding="utf-8-sig") == text:
                unchanged += 1
                continue
            shutil.copyfile(path, destination)
            copied += 1
            print(f"updated {destination.name}")
    kb = KnowledgeBase.load([target])
    problems = kb.problems(required_source_ids())
    print(f"{copied} updated, {unchanged} unchanged; {len(kb)} documents in {target}")
    for problem in problems:
        print(f"PROBLEM: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
