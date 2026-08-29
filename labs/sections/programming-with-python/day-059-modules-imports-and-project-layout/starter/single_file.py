#!/usr/bin/env python3
"""single_file.py — the "before": one script that does everything at once.

This is a working word-frequency tool with tokenizing, counting, the report,
and the command-line handling all tangled together in one block. It runs, but
nothing in it can be imported or tested on its own, because the real work only
happens inside the ``if __name__ == "__main__":`` block. Your task in the lab
is to split this into the ``wordstats/`` package, one responsibility per
module. Run it first to see what it does:

    python3 single_file.py sample.txt
"""
import re
import sys
from collections import Counter

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()
    words = re.findall(r"[a-z0-9']+", text.lower())
    counts = Counter(words)
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    print(f"{len(words)} words, {len(set(words))} unique")
    for rank, (word, count) in enumerate(ordered[:5], start=1):
        print(f"{rank}. {word}: {count}")
