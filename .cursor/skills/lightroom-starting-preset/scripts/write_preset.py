#!/usr/bin/env python3
"""Turn a catalog summary into a Lightroom .xmp preset and a notes file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import presetlib


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a Lightroom starting-point preset from catalog stats.")
    parser.add_argument("--list-styles", action="store_true", help="Print built-in style ids and exit.")
    parser.add_argument("--stats", help="JSON from analyze_catalog.py.")
    parser.add_argument("--style", default="match", help="Built-in style id, an alias, or 'custom'.")
    parser.add_argument("--strength", type=float, help="1 keeps a built-in recipe. Match mode defaults lower.")
    parser.add_argument("--name", help="Preset name shown in Lightroom.")
    parser.add_argument("--group", default="Starting Points", help="Preset group. Default: Starting Points.")
    parser.add_argument("--out", help="Destination .xmp path.")
    parser.add_argument("--notes", help="Notes markdown path. Defaults to the .xmp path with .notes.md.")
    parser.add_argument("--no-notes", action="store_true")
    parser.add_argument("--set", action="append", default=[], dest="sets", metavar="KEY=VALUE", help="Final slider value. Repeatable.")
    parser.add_argument("--allow-strong", action="store_true", help="Raise the starting-point caps. Use only when asked.")
    parser.add_argument("--no-white-balance", action="store_true", help="Do not write temperature or tint.")
    args = parser.parse_args()

    if args.list_styles:
        styles = presetlib.load_styles()
        for style_id, recipe in styles.items():
            print(f"{style_id}: {recipe['summary']}")
        print("custom: sliders passed with --set only.")
        return 0

    if not args.stats or not args.out:
        parser.error("--stats and --out are required unless you pass --list-styles.")

    try:
        stats = presetlib.read_stats(Path(args.stats))
        overrides = dict(presetlib.parse_override(item) for item in args.sets)
        preset = presetlib.build_preset(
            stats,
            style=args.style,
            strength=args.strength,
            overrides=overrides,
            allow_strong=args.allow_strong,
            white_balance=not args.no_white_balance,
            name=args.name,
            group=args.group,
        )
        xmp_path = Path(args.out)
        notes_path = None if args.no_notes else Path(args.notes) if args.notes else xmp_path.with_suffix(".notes.md")
        presetlib.write_outputs(preset, xmp_path, notes_path)
    except presetlib.PresetError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(xmp_path.resolve())
    if notes_path is not None:
        print(notes_path.resolve())
    print(f"style={preset['style']} strength={preset['strength']}", file=sys.stderr)
    for key, value in presetlib.ordered_sliders(preset["sliders"]).items():
        print(f"  {key}={presetlib.format_value(key, value)}", file=sys.stderr)
    if preset.get("curve"):
        print(f"  curve={preset['curve']}", file=sys.stderr)
    for warning in preset["warnings"]:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
