"""A fully annotated module that contains two deliberate type errors.

This file exists so you can see what a static type checker adds. Read the
annotations: they say exactly what each function takes and returns. Two of
the statements below contradict those annotations. Python itself does not
care — annotations are stored, never enforced — so one bug only shows up
when the program crashes at runtime and the other never shows up at all.

Run `bash examples/check_types.sh` to have a type checker point at both
before you run anything. If no checker is installed, that script says so and
exits cleanly; nothing in this lab requires one.
"""

from dataclasses import dataclass, field


@dataclass
class EvalRecord:
    prompt: str
    expected: str
    score: float = 0.0
    tags: list[str] = field(default_factory=list)


def mean_score(records: list[EvalRecord]) -> float:
    """Average score across a list of records."""
    return sum(record.score for record in records) / len(records)


def label(record: EvalRecord) -> str:
    """BUG 1: the annotation promises str, the body returns a float."""
    return record.score


def main() -> None:
    records = [EvalRecord("2+2?", "4", 0.5), EvalRecord("Capital?", "Paris", 1.0)]
    # BUG 2: mean_score wants a list of records; this passes a single record.
    print(mean_score(records[0]))


if __name__ == "__main__":
    main()
