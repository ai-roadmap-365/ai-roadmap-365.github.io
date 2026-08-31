#!/usr/bin/env python3
"""The same application, two Dockerfiles, one edited source file."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layer_cache import lint, parse, plan_build

NAIVE = """\
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "-m", "app"]
"""

ORDERED = """\
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
USER 10001
EXPOSE 8000
CMD ["python", "-m", "app"]
"""

# One line of application code changed. Nothing else.
EDIT = {"src/app.py"}


def show(name: str, dockerfile: str) -> None:
    ins = parse(dockerfile)
    cold = plan_build(ins, cold=True)
    warm = plan_build(ins, EDIT)
    print(f"--- {name} ---")
    print(f"  cold build   {cold.summary()}")
    print(f"  after edit   {warm.summary()}")
    miss = warm.first_miss
    if miss:
        print(f"  first miss   line {miss.instruction.line_no}: {miss.instruction.text[:44]}")
        print(f"               {miss.reason}")


def main() -> int:
    show("naive: COPY . . then install", NAIVE)
    show("ordered: manifest, install, then source", ORDERED)

    naive_warm = plan_build(parse(NAIVE), EDIT).seconds
    ordered_warm = plan_build(parse(ORDERED), EDIT).seconds
    print("--- the cost of one edit ---")
    print(f"  naive {naive_warm:.1f}s vs ordered {ordered_warm:.1f}s")
    if ordered_warm:
        print(f"  ordering the same instructions is {naive_warm / ordered_warm:.0f}x faster to rebuild")

    print("--- lint: naive ---")
    for f in lint(parse(NAIVE)):
        print(f"  line {f.line_no:>2} [{f.rule}] {f.message[:66]}")
    print("--- lint: ordered ---")
    found = lint(parse(ORDERED))
    for f in found:
        print(f"  line {f.line_no:>2} [{f.rule}] {f.message[:66]}")
    if not found:
        print("  no findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
