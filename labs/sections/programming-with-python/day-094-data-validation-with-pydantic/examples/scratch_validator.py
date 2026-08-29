"""A miniature validator built from first principles — no third-party code.

The point of this module is not to compete with pydantic. It is to make every
decision pydantic makes for you visible, by making you make it yourself:

  * where does the list of fields come from?          -> ``__annotations__``
  * what counts as "present"?                         -> a sentinel, not ``None``
  * which conversions are allowed?                    -> the COERCIONS table below
  * what happens on the first failure?                -> nothing; we keep going
  * how does a caller know *where* it went wrong?     -> a ``loc`` tuple

Everything here is the standard library. A model is an ordinary class whose
annotations describe its fields and whose class attributes supply defaults.

    class Station(MiniModel):
        code: str
        name: str
        elevation_m: int

    class Reading(MiniModel):
        reading_id: str
        station: Station
        pm25: float
        notes: str | None = None

    value, errors = validate(Reading, raw_dict)

``errors`` is a list of dictionaries, one per problem, each carrying ``loc``,
``type``, ``msg`` and ``input`` — the same four keys pydantic uses, chosen here
so that the shape of the report is familiar when you meet the real thing.
"""

from __future__ import annotations

import types
import typing
from typing import Any

__all__ = [
    "MISSING",
    "MiniModel",
    "ValidationReport",
    "coerce",
    "format_report",
    "validate",
]


class _Missing:
    """A sentinel meaning "the key was absent", which ``None`` cannot mean.

    This is the first decision a validator forces you to make. If absence were
    represented by ``None``, then a field explicitly set to ``null`` in the
    input would be indistinguishable from a field nobody wrote — and those are
    two different facts about the world.
    """

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return "MISSING"

    def __bool__(self) -> bool:
        return False


MISSING = _Missing()


class MiniModel:
    """Base class for a model. It carries no behaviour beyond field storage."""

    def __init__(self, **values: Any) -> None:
        for name, value in values.items():
            setattr(self, name, value)

    def __repr__(self) -> str:
        hints = declared_fields(type(self))
        pairs = ", ".join(f"{name}={getattr(self, name, MISSING)!r}" for name in hints)
        return f"{type(self).__name__}({pairs})"

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return all(
            getattr(self, name, MISSING) == getattr(other, name, MISSING)
            for name in declared_fields(type(self))
        )

    def as_dict(self) -> dict[str, Any]:
        """The nearest thing this toy has to ``model_dump``."""
        out: dict[str, Any] = {}
        for name in declared_fields(type(self)):
            value = getattr(self, name, MISSING)
            out[name] = value.as_dict() if isinstance(value, MiniModel) else value
        return out


def declared_fields(model: type[MiniModel]) -> dict[str, Any]:
    """Resolve the annotations of ``model`` and its bases into {name: type}.

    ``typing.get_type_hints`` is used rather than reading ``__annotations__``
    directly, because under ``from __future__ import annotations`` every
    annotation is a *string* until something resolves it. That single detail is
    why hand-rolled validators so often work in one module and not in another.
    """
    hints = typing.get_type_hints(model)
    return {name: hint for name, hint in hints.items() if not name.startswith("_")}


def default_for(model: type[MiniModel], name: str) -> Any:
    """A class attribute of the same name is the field's default."""
    return getattr(model, name, MISSING)


# --------------------------------------------------------------------------
# The coercion policy — every entry here is a decision, not a law of nature.
# --------------------------------------------------------------------------


def _str_to_int(value: str) -> int:
    return int(value.strip())


def _str_to_float(value: str) -> float:
    return float(value.strip())


def _int_to_float(value: int) -> float:
    return float(value)


COERCIONS: dict[tuple[type, type], Any] = {
    (str, int): _str_to_int,
    (str, float): _str_to_float,
    (int, float): _int_to_float,
}
"""Which conversions this validator is willing to perform.

Deliberately absent, and each absence is a judgement:

``(float, int)``
    Refused because it loses information silently. ``3.7`` is not ``3``.
``(bool, int)``
    Refused because ``True`` really is an ``int`` in Python — ``isinstance(True,
    int)`` is ``True`` — and letting a checkbox arrive where a count was wanted
    is a bug that survives to production.
``(str, bool)``
    Refused because there is no single right answer. Is ``"0"`` false? Is
    ``"no"``? Every codebase picks differently, so this one picks nothing.
"""

TYPE_NAMES = {int: "int", float: "float", str: "string", bool: "bool"}


def coerce(value: Any, target: type) -> tuple[Any, str | None]:
    """Return ``(converted_value, error_type)``; ``error_type`` is ``None`` on success."""
    name = TYPE_NAMES.get(target, target.__name__)

    # ``bool`` is a subclass of ``int``. Check it before the isinstance below,
    # or every True in the input becomes a perfectly acceptable 1.
    if isinstance(value, bool) and target is not bool:
        return value, f"{name}_type"

    if type(value) is target:
        return value, None
    if isinstance(value, target) and not isinstance(value, bool):
        return value, None

    converter = COERCIONS.get((type(value), target))
    if converter is None:
        return value, f"{name}_type"
    try:
        return converter(value), None
    except (TypeError, ValueError):
        return value, f"{name}_parsing"


# --------------------------------------------------------------------------
# The validator proper
# --------------------------------------------------------------------------


def _optional_inner(hint: Any) -> tuple[Any, bool]:
    """Split ``T | None`` into ``(T, True)``; anything else into ``(hint, False)``."""
    origin = typing.get_origin(hint)
    if origin is types.UnionType or origin is typing.Union:
        args = [arg for arg in typing.get_args(hint) if arg is not type(None)]
        if len(args) == 1 and len(typing.get_args(hint)) == 2:
            return args[0], True
    return hint, False


def validate(
    model: type[MiniModel],
    raw: Any,
    *,
    loc: tuple[Any, ...] = (),
    allow_extra: bool = False,
) -> tuple[MiniModel | None, list[dict[str, Any]]]:
    """Validate ``raw`` against ``model``, collecting **every** problem.

    Returns ``(instance, [])`` on success and ``(None, errors)`` on failure.
    Never raises for bad data; a raise would end the run at the first problem,
    which is exactly the behaviour this module exists to avoid.
    """
    errors: list[dict[str, Any]] = []

    if not isinstance(raw, dict):
        return None, [
            {
                "loc": loc,
                "type": "model_type",
                "msg": f"Input should be an object for {model.__name__}",
                "input": raw,
            }
        ]

    fields = declared_fields(model)
    values: dict[str, Any] = {}

    for name, hint in fields.items():
        inner, nullable = _optional_inner(hint)
        field_loc = (*loc, name)
        supplied = raw.get(name, MISSING)

        if supplied is MISSING:
            fallback = default_for(model, name)
            if fallback is MISSING:
                errors.append(
                    {
                        "loc": field_loc,
                        "type": "missing",
                        "msg": "Field required",
                        "input": raw,
                    }
                )
            else:
                values[name] = fallback
            continue

        if supplied is None:
            if nullable:
                values[name] = None
            else:
                errors.append(
                    {
                        "loc": field_loc,
                        "type": f"{TYPE_NAMES.get(inner, getattr(inner, '__name__', 'value'))}_type",
                        "msg": "Input should be a value, not null",
                        "input": None,
                    }
                )
            continue

        if isinstance(inner, type) and issubclass(inner, MiniModel):
            nested, nested_errors = validate(
                inner, supplied, loc=field_loc, allow_extra=allow_extra
            )
            if nested_errors:
                errors.extend(nested_errors)
            else:
                values[name] = nested
            continue

        converted, error_type = coerce(supplied, inner)
        if error_type is None:
            values[name] = converted
        else:
            expected = TYPE_NAMES.get(inner, getattr(inner, "__name__", "value"))
            verb = "be a valid" if error_type.endswith("_parsing") else "be"
            errors.append(
                {
                    "loc": field_loc,
                    "type": error_type,
                    "msg": f"Input should {verb} {expected}",
                    "input": supplied,
                }
            )

    if not allow_extra:
        for key in raw:
            if key not in fields:
                errors.append(
                    {
                        "loc": (*loc, key),
                        "type": "extra_forbidden",
                        "msg": "Extra inputs are not permitted",
                        "input": raw[key],
                    }
                )

    if errors:
        return None, errors
    return model(**values), []


class ValidationReport:
    """A tiny wrapper so a caller can ask a report questions instead of a list."""

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        self.errors = errors

    def __len__(self) -> int:
        return len(self.errors)

    def __bool__(self) -> bool:
        return bool(self.errors)

    def types(self) -> list[str]:
        return [error["type"] for error in self.errors]

    def locations(self) -> list[tuple[Any, ...]]:
        return [error["loc"] for error in self.errors]

    def at(self, *loc: Any) -> list[dict[str, Any]]:
        return [error for error in self.errors if error["loc"] == loc]


def format_report(errors: list[dict[str, Any]]) -> str:
    """Render errors the way a human wants to read them: location first."""
    if not errors:
        return "no errors"
    lines = [f"{len(errors)} validation error(s)"]
    for error in errors:
        where = ".".join(str(part) for part in error["loc"]) or "<root>"
        lines.append(f"  {where}")
        lines.append(f"    {error['msg']} [type={error['type']}, input={error['input']!r}]")
    return "\n".join(lines)
