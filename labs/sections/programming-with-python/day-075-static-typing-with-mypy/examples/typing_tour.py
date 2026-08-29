"""A tour of the type system, every line of which passes mypy --strict.

This file is a reference, not an exercise. Read it beside the lesson: each
section is one construct, written the way you would actually use it. Run it
to see the values, and check it to see that the annotations hold:

    python3 examples/typing_tour.py
    python3 -m mypy --strict examples/typing_tour.py
"""

from __future__ import annotations

from typing import Final, Literal, NewType, Protocol, TypedDict, TypeVar, cast

# --- Builtin generics -------------------------------------------------------
# list[int], dict[str, float], tuple[int, ...] are the modern spelling. The
# capitalised List/Dict imports from typing mean the same thing and belong to
# older code.

Scores = dict[str, list[float]]  # a type alias is just a name for a type


def mean(values: list[float]) -> float:
    """Arithmetic mean. Empty input is a value question, not a type question."""
    if not values:
        raise ValueError("mean of no values")
    return sum(values) / len(values)


def best_suite(scores: Scores) -> tuple[str, float]:
    """Return the suite with the highest mean score, and that mean."""
    ranked = sorted(((name, mean(vals)) for name, vals in scores.items()), key=lambda pair: -pair[1])
    return ranked[0]


# --- Optional, and the narrowing that makes it usable -----------------------
# `X | None` is the modern spelling of Optional[X]. They are the same type.


def first_word(text: str | None) -> str:
    """The first word of `text`, or a placeholder when there is no text.

    The two guards are the whole idea. Before them mypy knows `text` is
    `str | None` and refuses `.split()`. After `if text is None: return ...`
    it knows `text` is `str` on every remaining line.
    """
    if text is None:
        return "(nothing)"
    words = text.split()
    if not words:
        return "(blank)"
    return words[0]


def parse_port(raw: object) -> int:
    """Narrowing with isinstance rather than a None check.

    `raw` arrives as `object`, which mypy will let you do almost nothing
    with. Each isinstance branch narrows it to something usable.
    """
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return int(raw)
    raise TypeError(f"cannot read a port from {type(raw).__name__}")


# --- Union of two real types ------------------------------------------------


def token_count(item: str | list[str]) -> int:
    """Accept either a string or a list of strings and count the words."""
    if isinstance(item, str):
        return len(item.split())
    return sum(len(part.split()) for part in item)


# --- Literal ----------------------------------------------------------------
# Literal pins a value to a fixed set. A typo in a call site becomes an error
# instead of a shrug at runtime.

Mode = Literal["semantic", "keyword"]


def search_label(mode: Mode) -> str:
    return f"search mode: {mode}"


# --- TypedDict --------------------------------------------------------------
# For JSON-shaped data you must keep as a dict, TypedDict says which keys
# exist and what each holds.


class RunRecord(TypedDict):
    suite: str
    passed: int
    failed: int


def pass_rate(record: RunRecord) -> float:
    total = record["passed"] + record["failed"]
    if total == 0:
        return 0.0
    return record["passed"] / total


# --- Final and NewType ------------------------------------------------------
# Final says "this name is never rebound". NewType makes a distinct type out
# of an existing one, so two things that are both strings stop being
# interchangeable.

MAX_RETRIES: Final = 3

UserId = NewType("UserId", str)
SessionId = NewType("SessionId", str)


def audit_line(user: UserId, session: SessionId) -> str:
    """Both parameters are strings at runtime, and distinct types to mypy.

    Call this with the arguments the wrong way round and mypy reports it,
    which a plain `(str, str)` signature could never do.
    """
    return f"user={user} session={session}"


# --- TypeVar and generic functions ------------------------------------------
# A TypeVar is a placeholder that means "whatever type came in, that same type
# goes out" — which `Any` cannot express, because Any forgets.

T = TypeVar("T")


def first_or(items: list[T], fallback: T) -> T:
    """Return the first item, or the fallback when the list is empty."""
    return items[0] if items else fallback


# --- Protocol: structural typing --------------------------------------------
# A Protocol describes a shape. Anything with matching methods satisfies it,
# with no inheritance and no registration — which is exactly what you want
# for an injected dependency.


class Clock(Protocol):
    """Anything that can tell you the time, in seconds, as a float."""

    def now(self) -> float: ...


class FrozenClock:
    """A test double. It inherits from nothing and mentions Clock nowhere."""

    def __init__(self, value: float) -> None:
        self.value = value

    def now(self) -> float:
        return self.value


def stamp(clock: Clock, message: str) -> str:
    """Depends on the shape, not on a base class."""
    return f"[{clock.now():.1f}] {message}"


# --- cast: the escape hatch, used sparingly ---------------------------------


def config_name(config: dict[str, object]) -> str:
    """cast asserts a type to the checker and does NOTHING at runtime.

    The values in this dict are `object`, so mypy will not let you return one
    as a str. `cast` tells it to believe you anyway. It generates no check and
    no conversion — if the value is really an int, the cast succeeds silently
    and the wrongness surfaces somewhere else entirely. Prefer isinstance,
    which narrows AND checks; reach for cast only where you know something
    the checker cannot, and say so in a comment.

    (If you write a cast that mypy could already prove — casting a value it
    has narrowed with isinstance — it tells you so, with [redundant-cast].)
    """
    return cast(str, config["name"])


def main() -> None:
    scores: Scores = {"arithmetic": [0.9, 0.8, 1.0], "geometry": [0.5, 0.6]}
    print(f"mean of arithmetic: {mean(scores['arithmetic']):.4f}")
    print(f"best suite: {best_suite(scores)[0]} at {best_suite(scores)[1]:.4f}")
    print(f"first_word(None): {first_word(None)}")
    print(f"first_word('  '): {first_word('  ')}")
    print(f"first_word('hello there'): {first_word('hello there')}")
    print(f"parse_port('8080'): {parse_port('8080')}")
    print(f"token_count('a b c'): {token_count('a b c')}")
    print(f"token_count(['a b', 'c']): {token_count(['a b', 'c'])}")
    print(f"search_label('keyword'): {search_label('keyword')}")
    record: RunRecord = {"suite": "arithmetic", "passed": 7, "failed": 3}
    print(f"pass_rate: {pass_rate(record):.4f}")
    print(f"MAX_RETRIES: {MAX_RETRIES}")
    print(audit_line(UserId("u-1"), SessionId("s-9")))
    print(f"first_or([], 'fallback'): {first_or([], 'fallback')}")
    print(f"first_or([4, 5], 0): {first_or([4, 5], 0)}")
    print(stamp(FrozenClock(1234.5), "structural typing works"))
    print(f"config_name: {config_name({'name': 'production', 'retries': 3})}")


if __name__ == "__main__":
    main()
