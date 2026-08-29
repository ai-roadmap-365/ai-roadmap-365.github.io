"""Exercise 6 (required): what the interpreter stores, and what it ignores.

Annotations are real objects that Python keeps in `__annotations__`, and
@dataclass reads them to decide what the fields are. What Python never does
is check a value against one. This script proves both halves.

Run from the lab directory:  python3 examples/inspect_runtime.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from records import EvalRecord, annotation_names, describe_fields  # noqa: E402


def show_stored() -> None:
    print("What Python STORES")
    print("------------------")
    print("EvalRecord.__annotations__ names:", annotation_names(EvalRecord))
    print()
    print("dataclasses.fields(EvalRecord):")
    for line in describe_fields(EvalRecord):
        print("  " + line)
    print()


def show_ignored() -> None:
    print("What Python does NOT check")
    print("--------------------------")
    # Every annotation below is contradicted, and every line runs happily.
    wrong = EvalRecord(prompt="2+2?", expected="4", score=0.5, tags=["math"])
    wrong.score = "not a number"          # annotated float
    wrong.tags = 17                       # annotated list[str]
    print("assigned a str to .score ->", repr(wrong.score))
    print("assigned an int to .tags  ->", repr(wrong.tags))
    print()

    def double(number: int) -> int:
        return number * 2

    print("double.__annotations__ names:", list(double.__annotations__))
    print("double('ab') ->", repr(double("ab")))
    print()
    print("Nothing above raised. Annotations are documentation the")
    print("interpreter records and a type checker reads; only __post_init__")
    print("(or an explicit isinstance check) enforces anything at runtime.")


if __name__ == "__main__":
    show_stored()
    show_ignored()
