"""YOUR WORKING FILE — exercises 1 to 6.

Complete the numbered exercises below, in order. Each unfinished piece
raises NotImplementedError on purpose, so an empty function can never be
mistaken for a working one. The reference solution is in
`examples/records.py`; use it only when you are genuinely stuck.

After each exercise, check your progress from the lab directory:

    python3 starter/demo.py
    bash tests/run_tests.sh
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


# --- Given: the hand-written class, for comparison --------------------------
# Read this before you write anything. Count the lines, and count how many
# times `prompt` appears: parameter list, left of the assignment, right of
# the assignment, __repr__, __eq__ — five times, for one field.
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


# --- EXERCISE 1: convert the class above into a dataclass -------------------
# EXERCISE 2: give `tags` a per-instance list default.
# EXERCISE 3: add __post_init__ validation and a derived field.
#
# 1. Decorate EvalRecord with @dataclass. Declare four fields with
#    annotations, in this order:
#       prompt: str            (required)
#       expected: str          (required)
#       score: float           default 0.0
#       tags: list[str]        default: a NEW empty list per instance
#    Verify first that `tags: list[str] = []` raises ValueError when the
#    class is defined — then replace it with field(default_factory=list).
# 2. Add a fifth field that is computed, not passed in:
#       prompt_length: int = field(init=False, repr=False, default=0)
# 3. Write __post_init__ so it raises ValueError when `prompt` is blank
#    (use .strip()), when `expected` is blank, or when `score` is outside
#    0.0 to 1.0 inclusive — the message must contain the offending score —
#    and otherwise sets self.prompt_length to len(self.prompt).
class EvalRecord:
    """One evaluation record: a prompt, the expected answer, a score, tags."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Exercises 1-3: make EvalRecord a @dataclass with annotated "
            "fields, field(default_factory=list) for tags, and __post_init__ "
            "validation."
        )


# --- EXERCISE 4: a frozen dataclass ----------------------------------------
# Decorate RunKey with @dataclass(frozen=True, order=True) and declare two
# annotated fields: `suite: str` and `seed: int`, in that order.
# frozen=True blocks attribute assignment (raising FrozenInstanceError) and
# therefore lets Python generate a safe __hash__, so instances work as dict
# keys and set members. order=True generates the comparison methods, so a
# list of RunKeys sorts by suite and then by seed.
class RunKey:
    """Identifies one evaluation run. Should be frozen, hashable, orderable."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Exercise 4: make RunKey a @dataclass(frozen=True, order=True) "
            "with fields suite: str and seed: int."
        )


# --- EXERCISE 5: JSON round trip -------------------------------------------
def records_to_json(records: list) -> str:
    """Serialise records to indented, key-sorted JSON text.

    Build a list of plain dicts with `asdict(record)` for each record, then
    return `json.dumps(rows, indent=2, sort_keys=True)`. Sorting the keys
    keeps the output deterministic so the tests can compare it.
    """
    raise NotImplementedError("Exercise 5a: use asdict + json.dumps.")


def records_from_json(text: str) -> list:
    """Rebuild records from JSON text produced by `records_to_json`.

    `json.loads(text)` gives a list of dicts. For each one, construct an
    EvalRecord from the `prompt`, `expected`, `score` and `tags` keys. Do
    NOT pass `prompt_length`: it is derived, so __post_init__ recomputes it
    (and it is not an __init__ parameter at all).
    """
    raise NotImplementedError("Exercise 5b: json.loads + rebuild each record.")


def rescore(record, new_score: float):
    """Return a copy of `record` with a different score.

    Use `dataclasses.replace`. It calls __init__ with the changed field, so
    __post_init__ runs again and the new score is validated for free.
    """
    raise NotImplementedError("Exercise 5c: use dataclasses.replace.")


# --- EXERCISE 6: inspect what the interpreter stores ------------------------
def format_annotation(annotation: object) -> str:
    """Render an annotation readably: `str`, `float`, `list[str]`.

    Given. A plain class prints as its short name; a parameterised generic
    such as list[str] already prints readably via str().
    """
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)


def describe_fields(cls: type) -> list:
    """Describe a dataclass's fields as readable lines.

    Loop over `dataclasses.fields(cls)`. For each Field object `spec`,
    append one string shaped like:

        "prompt: str = (required)"
        "score: float = 0.0"
        "tags: list[str] = factory list()"

    Use `format_annotation(spec.type)` for the type part. For the default:
    if `spec.default is not MISSING` use `repr(spec.default)`; else if
    `spec.default_factory is not MISSING` use
    f"factory {spec.default_factory.__name__}()"; else use "(required)".
    """
    raise NotImplementedError("Exercise 6a: read dataclasses.fields(cls).")


def annotation_names(cls: type) -> list:
    """Return the annotated names on `cls`, in declaration order.

    One line: `list(cls.__annotations__)`. This is the very same dictionary
    @dataclass itself reads to decide what the fields are.
    """
    raise NotImplementedError("Exercise 6b: read cls.__annotations__.")
