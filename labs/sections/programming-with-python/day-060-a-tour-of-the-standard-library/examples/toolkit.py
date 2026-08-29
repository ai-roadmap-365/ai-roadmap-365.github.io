#!/usr/bin/env python3
"""toolkit.py — Stdlib Toolkit: a directory audit built from the standard
library only.

It walks a folder with pathlib, tallies file extensions with
collections.Counter, stamps the moment with datetime, and writes a JSON
report with json — four drawers of the standard-library toolbox, nothing
installed.

    python3 examples/toolkit.py --dir sample-data
    python3 examples/toolkit.py --dir sample-data --out report.json
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def walk_files(directory):
    """Return a sorted list of every file under directory (recursively).

    Uses pathlib: Path(directory).rglob("*") yields every entry in the tree,
    and .is_file() keeps only files (not subdirectories).
    """
    root = Path(directory)
    return sorted(p for p in root.rglob("*") if p.is_file())


def tally_extensions(items):
    """Tally file extensions across items (paths or names).

    Case-insensitive; a file with no extension is counted as "(none)".
    Returns a plain dict ordered largest-count first.
    """
    counter = Counter()
    for item in items:
        suffix = Path(item).suffix.lower() or "(none)"
        counter[suffix] += 1
    return dict(counter.most_common())


def build_report(directory, files):
    """Assemble the audit report dict from the walked files.

    Stamps the current time with datetime and tallies extensions.
    """
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "directory": str(directory),
        "total_files": len(files),
        "by_extension": tally_extensions(files),
    }


def write_report(path, report):
    """Write the report to path as pretty-printed JSON."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")


def build_parser():
    """Build the argparse parser: --dir to audit, optional --out to save."""
    parser = argparse.ArgumentParser(
        prog="toolkit.py",
        description="Audit a directory: count files by extension and stamp a JSON report.",
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="the directory to audit (walked recursively)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="optional path to also write the JSON report to",
    )
    return parser


def main(argv):
    """Entry point: parse arguments, walk, build the report, print (and save)."""
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    files = walk_files(args.dir)
    report = build_report(args.dir, files)
    if args.out:
        write_report(args.out, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
