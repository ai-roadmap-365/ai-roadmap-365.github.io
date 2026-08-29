"""Runs YOUR starter code, exercise by exercise. Given — do not edit.

Each exercise is run on its own, so an unfinished one prints a note instead
of stopping the whole script. Work through starter/records.py and
starter/mini_dataclass.py until every section prints real results, then
compare with `python3 examples/demo.py`.

Run from the lab directory:  python3 starter/demo.py
"""

import sys
from dataclasses import FrozenInstanceError, asdict, astuple, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mini_dataclass as mini_module  # noqa: E402
import records as records_module  # noqa: E402


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def exercise_1() -> None:
    rule("1. Hand-written class vs dataclass")
    hand = records_module.HandWrittenRecord("2+2?", "4")
    auto = records_module.EvalRecord("2+2?", "4")
    print("hand-written repr:", repr(hand))
    print("dataclass repr:   ", repr(auto))
    print("hand-written equal by value:", hand == records_module.HandWrittenRecord("2+2?", "4"))
    print("dataclass equal by value:   ", auto == records_module.EvalRecord("2+2?", "4"))


def exercise_2() -> None:
    rule("2. The mutable default trap")

    def add_tag(tag, bucket=[]):
        bucket.append(tag)
        return bucket

    print("plain function, call 1:", add_tag("math"))
    print("plain function, call 2:", add_tag("logic"), "<- the list was shared")

    try:
        @dataclass
        class Broken:
            name: str
            tags: list[str] = []
    except ValueError as err:
        print("dataclass refuses it: ValueError:", err)

    first = records_module.EvalRecord("a?", "a")
    second = records_module.EvalRecord("b?", "b")
    first.tags.append("math")
    print("  first.tags =", first.tags)
    print("  second.tags =", second.tags)


def exercise_3() -> None:
    rule("3. __post_init__ validation and a derived field")
    good = records_module.EvalRecord("Capital of France?", "Paris", 1.0, ["geo"])
    print("valid record:", good)
    print("derived prompt_length:", good.prompt_length)
    for bad_args, note in [(("   ", "4", 0.5), "blank prompt"), (("2+2?", "4", 3.0), "score out of range")]:
        try:
            records_module.EvalRecord(*bad_args)
            print(f"NOT rejected ({note}) — __post_init__ is not validating yet")
        except ValueError as err:
            print(f"rejected ({note}): ValueError: {err}")


def exercise_4() -> None:
    rule("4. A frozen dataclass is hashable and orderable")
    key = records_module.RunKey("arithmetic", 7)
    print("key:", key)
    print("equal keys hash the same:", hash(key) == hash(records_module.RunKey("arithmetic", 7)))
    counts = {records_module.RunKey("arithmetic", 7): 12}
    print("usable as a dict key:", counts[records_module.RunKey("arithmetic", 7)])
    try:
        key.seed = 8
        print("assignment ALLOWED — the class is not frozen yet")
    except FrozenInstanceError as err:
        print("assignment refused: FrozenInstanceError:", err)


def exercise_5() -> None:
    rule("5. JSON round trip with asdict and a rebuild function")
    records = [
        records_module.EvalRecord("2+2?", "4", 0.5, ["math"]),
        records_module.EvalRecord("Capital of France?", "Paris", 1.0, ["geo"]),
    ]
    print("asdict of one record:", asdict(records[0]))
    print("astuple of one record:", astuple(records[0]))
    text = records_module.records_to_json(records)
    for line in text.splitlines()[:5]:
        print("  " + line)
    print("rebuilt == original:", records_module.records_from_json(text) == records)
    print("replace() makes a validated copy:", records_module.rescore(records[0], 0.9))


def exercise_6() -> None:
    rule("6. What the interpreter stores, and what it ignores")
    print("annotation names:", records_module.annotation_names(records_module.EvalRecord))
    for line in records_module.describe_fields(records_module.EvalRecord):
        print("  " + line)


def exercise_7() -> None:
    rule("7. mini_dataclass generates the same shapes")
    small = mini_module.MiniRecord("2+2?", "4")
    real = mini_module.RealRecord("2+2?", "4")
    print("mini repr:", repr(small))
    print("real repr:", repr(real))
    same_shape = repr(small).split("(", 1)[1] == repr(real).split("(", 1)[1]
    print("same repr shape (fields and formatting):", same_shape)
    print("mini equality works:", small == mini_module.MiniRecord("2+2?", "4"),
          "and differs:", small == mini_module.MiniRecord("2+2?", "5"))
    try:
        mini_module.MiniRecord("only-one")
        print("missing argument NOT rejected yet")
    except TypeError as err:
        print("missing argument: TypeError:", err)


if __name__ == "__main__":
    for number, run in enumerate(
        [exercise_1, exercise_2, exercise_3, exercise_4, exercise_5, exercise_6, exercise_7],
        start=1,
    ):
        try:
            run()
        except NotImplementedError as err:
            print()
            print(f"Exercise {number}: not finished yet — {err}")
    print()
    print("Optional: bash examples/check_types.sh (skips cleanly with no checker).")
