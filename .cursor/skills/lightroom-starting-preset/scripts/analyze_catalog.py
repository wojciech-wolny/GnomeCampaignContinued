#!/usr/bin/env python3
"""Measure a folder of photos or a Lightroom .lrcat catalog.

Writes a JSON summary the preset writer consumes. The catalog is opened
read-only. Nothing in Lightroom is modified.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import presetlib


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure photos or a Lightroom catalog for a starting-point preset.")
    parser.add_argument("--catalog", required=True, help="Folder of photos, or a .lrcat file.")
    parser.add_argument("--out", help="Write the JSON summary here. Prints it to stdout when omitted.")
    parser.add_argument("--limit", type=int, default=80, help="How many photos to measure. Default 80, spread across the set.")
    parser.add_argument("--collection", help="Lightroom collection name. Catalogs only.")
    args = parser.parse_args()
    try:
        stats = presetlib.analyze_catalog(Path(args.catalog), limit=args.limit, collection=args.collection)
    except presetlib.PresetError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    text = json.dumps(stats, indent=2, ensure_ascii=False)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    print(
        f"{stats['source']}: {stats['sampled']} measured, {stats['photo_count']} considered.",
        file=sys.stderr,
    )
    for warning in stats["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    for note in stats["observations"]:
        print(f"observe: {note}", file=sys.stderr)
    if stats["review_paths"]:
        print("review:", file=sys.stderr)
        for path in stats["review_paths"]:
            print(f"  {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
