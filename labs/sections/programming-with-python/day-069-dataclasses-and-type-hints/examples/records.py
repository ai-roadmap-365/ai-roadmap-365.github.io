"""Reference solution: evaluation records built with dataclasses.

This is the completed version of `starter/records.py`. Every function and
class here is pure logic plus small, explicit validation — there is no
input or output in this module, so it can be imported and tested with plain
function calls.

The domain is a tiny "evaluation record": a prompt, the answer we expect,
a score between 0.0 and 1.0, and some tags. It is deliberately the shape of
the records you keep when you measure how well a system answers questions.
"""

from dataclasses import (
    MISSING,
    asdict,
    dataclass,
    field,
    fields,
    replace,
)
import json


# --- Exercise 1: the hand-written class, kept for comparison ----------------
# This is what you write WITHOUT @dataclass. Count the lines, and count how
# many times the word `prompt` appears: once in the parameter list, once on
# the left of the assignment, once on the right, once in __repr__, and once
# in __eq__.
class HandWrittenRecord:
    """A record class with __init__, __repr__ and __eq__ written by hand."""

    def __init__(self, prompt, expected, score=0.0):
        self.prompt = prompt
        self.expected = expected
        self.score = score

    def __repr__(self):
        return (
            f"HandWrittenRecord(prompt={self.prompt!r}, "
            f"expected={self.expected!r}, score={self.score!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, HandWrittenRecord):
            return NotImplemented
        return (self.prompt, self.expected, self.score) == (
            other.prompt,
            other.expected,
            other.score,
        )


# --- Exercises 1-3: the same record as a dataclass --------------------------
@dataclass
class EvalRecord:
    """One evaluation record: a prompt, the expected answer, a score, tags.

    `tags` uses `field(default_factory=list)` because a bare `[]` default
    would be shared by every instance — and a dataclass refuses it outright
    with a ValueError.

    `prompt_length` is derived in __post_init__, so it is not an __init__
    parameter (`init=False`) and is left out of the repr (`repr=False`).
    """

    prompt: str
    expected: str
    score: float = 0.0
    tags: list[str] = field(default_factory=list)
    prompt_length: int = field(init=False, repr=False, default=0)

    def __post_init__(self) -> None:
        """Validate the fields and compute the derived one."""
        if not self.prompt.strip():
            raise ValueError("prompt must not be empty")
        if not self.expected.strip():
            raise ValueError("expected must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                f"score must be between 0.0 and 1.0, got {self.score}"
            )
        self.prompt_length = len(self.prompt)


# --- Exercise 4: a frozen dataclass, usable as a dict key -------------------
@dataclass(frozen=True, order=True)
class RunKey:
    """Identifies one evaluation run. Frozen, so hashable and orderable.

    `frozen=True` blocks attribute assignment after construction, which is
    what makes a generated __hash__ safe: the hash can never go stale.
    `order=True` generates __lt__/__le__/__gt__/__ge__ from the fields in
    declaration order, so a list of RunKeys sorts by suite then seed.
    """

    suite: str
    seed: int


# --- Exercise 5: JSON round-tripping ---------------------------------------
def records_to_json(records: list[EvalRecord]) -> str:
    """Serialise records to indented, key-sorted JSON text.

    `asdict` walks the dataclass recursively and returns plain dicts and
    lists, which is exactly what `json.dumps` knows how to write. Sorting
    the keys makes the output deterministic, so a test can compare it.
    """
    return json.dumps([asdict(record) for record in records], indent=2, sort_keys=True)


def records_from_json(text: str) -> list[EvalRecord]:
    """Rebuild records from JSON text produced by `records_to_json`.

    There is no automatic reverse of `asdict`: JSON gives you dicts, and you
    decide how to turn each dict back into an object. `prompt_length` is
    skipped on purpose — it is derived, so __post_init__ recomputes it.
    """
    rebuilt = []
    for row in json.loads(text):
        rebuilt.append(
            EvalRecord(
                prompt=row["prompt"],
                expected=row["expected"],
                score=row["score"],
                tags=list(row["tags"]),
            )
        )
    return rebuilt


def rescore(record: EvalRecord, new_score: float) -> EvalRecord:
    """Return a copy of `record` with a different score.

    `replace` calls the class's __init__ with the changed fields, so
    __post_init__ runs again and the new score is validated.
    """
    return replace(record, score=new_score)


# --- Exercise 6: what the interpreter does and does not enforce -------------
def format_annotation(annotation: object) -> str:
    """Render an annotation readably: `str`, `float`, `list[str]`.

    A plain class prints as its short name; a parameterised generic such as
    `list[str]` is already readable via str(), so it is used as-is.
    """
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)


def describe_fields(cls: type) -> list[str]:
    """Describe a dataclass's fields as readable lines.

    Reads the two things @dataclass itself reads: the class's
    `__annotations__` and the `Field` objects that `dataclasses.fields()`
    returns. Nothing here checks any value against any annotation — that is
    the point of the exercise.
    """
    lines = []
    for spec in fields(cls):
        if spec.default is not MISSING:
            default = repr(spec.default)
        elif spec.default_factory is not MISSING:
            default = f"factory {spec.default_factory.__name__}()"
        else:
            default = "(required)"
        lines.append(f"{spec.name}: {format_annotation(spec.type)} = {default}")
    return lines


def annotation_names(cls: type) -> list[str]:
    """Return the annotated names on `cls`, in declaration order."""
    return list(cls.__annotations__)
