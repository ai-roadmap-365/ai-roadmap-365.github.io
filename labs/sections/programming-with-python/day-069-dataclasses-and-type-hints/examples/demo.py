"""A guided tour of the reference solution: exercises 1-5 and 7.

Run from the lab directory:  python3 examples/demo.py

Every line of output is deterministic — no clocks, no random numbers, no
memory addresses — so you can compare it against
expected-output/sample-run.txt character for character.
"""

import sys
from dataclasses import FrozenInstanceError, asdict, astuple, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mini_dataclass import MiniRecord, RealRecord  # noqa: E402
from records import (  # noqa: E402
    EvalRecord,
    HandWrittenRecord,
    RunKey,
    records_from_json,
    records_to_json,
    rescore,
)


def rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def exercise_1_hand_written_vs_dataclass() -> None:
    rule("1. Hand-written class vs dataclass")
    hand = HandWrittenRecord("2+2?", "4")
    auto = EvalRecord("2+2?", "4")
    print("hand-written repr:", repr(hand))
    print("dataclass repr:   ", repr(auto))
    print("hand-written equal by value:", hand == HandWrittenRecord("2+2?", "4"))
    print("dataclass equal by value:   ", auto == EvalRecord("2+2?", "4"))
    print("dataclass differs when a field differs:", auto == EvalRecord("2+2?", "5"))


def exercise_2_mutable_default() -> None:
    rule("2. The mutable default trap")

    def add_tag(tag, bucket=[]):
        """A plain function with a shared list default — silently wrong."""
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

    first = EvalRecord("a?", "a")
    second = EvalRecord("b?", "b")
    first.tags.append("math")
    print("default_factory gives each instance its own list:")
    print("  first.tags =", first.tags)
    print("  second.tags =", second.tags)


def exercise_3_post_init() -> None:
    rule("3. __post_init__ validation and a derived field")
    good = EvalRecord("Capital of France?", "Paris", 1.0, ["geo"])
    print("valid record:", good)
    print("derived prompt_length:", good.prompt_length)
    for bad_args, note in [
        (("   ", "4", 0.5), "blank prompt"),
        (("2+2?", "4", 3.0), "score out of range"),
    ]:
        try:
            EvalRecord(*bad_args)
        except ValueError as err:
            print(f"rejected ({note}): ValueError: {err}")


def exercise_4_frozen() -> None:
    rule("4. A frozen dataclass is hashable and orderable")
    key = RunKey("arithmetic", 7)
    print("key:", key)
    print("equal keys hash the same:", hash(key) == hash(RunKey("arithmetic", 7)))
    counts = {RunKey("arithmetic", 7): 12, RunKey("geography", 1): 4}
    print("usable as a dict key:", counts[RunKey("arithmetic", 7)])
    print("sorted by suite then seed:", sorted([RunKey("geo", 2), RunKey("arith", 9), RunKey("arith", 1)]))
    try:
        key.seed = 8
    except FrozenInstanceError as err:
        print("assignment refused: FrozenInstanceError:", err)


def exercise_5_json_round_trip() -> None:
    rule("5. JSON round trip with asdict and a rebuild function")
    records = [
        EvalRecord("2+2?", "4", 0.5, ["math"]),
        EvalRecord("Capital of France?", "Paris", 1.0, ["geo", "easy"]),
    ]
    print("asdict of one record:", asdict(records[0]))
    print("astuple of one record:", astuple(records[0]))
    text = records_to_json(records)
    print("JSON text, first 5 lines:")
    for line in text.splitlines()[:5]:
        print("  " + line)
    rebuilt = records_from_json(text)
    print("rebuilt == original:", rebuilt == records)
    print("replace() makes a validated copy:", rescore(records[0], 0.9))


def exercise_7_mini_dataclass() -> None:
    rule("7. mini_dataclass generates the same shapes")
    mini = MiniRecord("2+2?", "4")
    real = RealRecord("2+2?", "4")
    print("mini repr:", repr(mini))
    print("real repr:", repr(real))
    same_shape = repr(mini).split("(", 1)[1] == repr(real).split("(", 1)[1]
    print("same repr shape (fields and formatting):", same_shape)
    print("mini equality works:", mini == MiniRecord("2+2?", "4"),
          "and differs:", mini == MiniRecord("2+2?", "5"))
    print("keyword arguments work:", MiniRecord(prompt="a", expected="b", score=0.5))
    try:
        MiniRecord("only-one")
    except TypeError as err:
        print("missing argument: TypeError:", err)


if __name__ == "__main__":
    exercise_1_hand_written_vs_dataclass()
    exercise_2_mutable_default()
    exercise_3_post_init()
    exercise_4_frozen()
    exercise_5_json_round_trip()
    exercise_7_mini_dataclass()
    print()
    print("Exercise 6 lives in examples/inspect_runtime.py; the optional")
    print("type-checker step lives in examples/check_types.sh.")
