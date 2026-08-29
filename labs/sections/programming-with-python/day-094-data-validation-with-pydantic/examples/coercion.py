"""Which conversions pydantic performs by default, and which it refuses.

This is the part of pydantic that surprises people, so rather than describe it,
this module asks. Every row of the table it prints is the result of an actual
call to ``TypeAdapter(...).validate_python(...)`` in this interpreter, once in
the default (lax) mode and once with ``strict=True``.

Run it directly:

    python3 examples/coercion.py
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, NamedTuple, get_origin

from pydantic import TypeAdapter, ValidationError

CASES: list[tuple[Any, Any]] = [
    ("42", int),
    ("42.0", int),
    ("  42  ", int),
    ("forty-two", int),
    (42.0, int),
    (42.7, int),
    (True, int),
    ("3.14", float),
    (3, float),
    (42, str),
    (None, str),
    ("yes", bool),
    ("true", bool),
    (1, bool),
    ("2026-08-15T06:00:00Z", datetime),
    ("15/08/2026", date),
    (1786773600, datetime),
    ("[1, 2]", list[int]),
    ((1, 2), list[int]),
    # A set of small ints, deliberately: CPython hash-randomises strings, so a
    # set of strings would print in a different order on a different run and
    # this table would stop being reproducible.
    ({1, 2}, list[int]),
]


class Row(NamedTuple):
    """One question asked twice."""

    value: Any
    target: Any
    lax: str
    strict: str


def _target_name(target: Any) -> str:
    if get_origin(target) is not None:
        return str(target).replace("typing.", "")
    return getattr(target, "__name__", None) or str(target)


def _ask(value: Any, target: Any, *, strict: bool) -> str:
    """Return either the validated value's repr or the error ``type``."""
    adapter = TypeAdapter(target)
    try:
        return repr(adapter.validate_python(value, strict=strict))
    except ValidationError as exc:
        return f"refused: {exc.errors()[0]['type']}"


def coercion_table() -> list[Row]:
    rows = []
    for value, target in CASES:
        rows.append(
            Row(
                value=value,
                target=target,
                lax=_ask(value, target, strict=False),
                strict=_ask(value, target, strict=True),
            )
        )
    return rows


def render(rows: list[Row]) -> str:
    header = f"{'input':<24} {'declared as':<12} {'lax (default)':<34} strict=True"
    lines = [header, "-" * len(header) + "----"]
    for row in rows:
        # A set has no defined order, so print it in a stable form.
        shown = sorted(row.value, key=str) if isinstance(row.value, set) else row.value
        prefix = "set" if isinstance(row.value, set) else ""
        lines.append(
            f"{prefix + repr(shown):<24} {_target_name(row.target):<12} {row.lax:<34} {row.strict}"
        )
    return "\n".join(lines)


def main() -> int:
    print(render(coercion_table()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
