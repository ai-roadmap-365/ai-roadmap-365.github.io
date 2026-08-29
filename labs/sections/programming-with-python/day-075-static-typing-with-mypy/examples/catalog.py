"""The fixed catalogue: identical behaviour on the tested paths, clean under
mypy --strict.

Compare this file with starter/catalog.py line by line. Four things changed:

  1. describe() now handles the None the lookup can return, so the checker
     can narrow `Model | None` down to `Model` before the attributes are read.
  2. split_cost() uses floor division, so the value handed to estimate_cost
     really is an int.
  3. format_price() is annotated, so strict mode accepts both the definition
     and the calls to it.
  4. load_settings() checks the loaded object at the boundary instead of
     passing Any through, so the returned dict genuinely is dict[str, float].

Note what did NOT change: the tests. Every test in test_catalog.py passes
before and after. The bugs were never on a tested path — which is exactly why
a checker is not a substitute for tests, and tests are not a substitute for a
checker.
"""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    """One row of the catalogue."""

    name: str
    context_tokens: int
    price_per_million_input: float


CATALOG: dict[str, Model] = {
    "small": Model(name="small", context_tokens=8_000, price_per_million_input=0.25),
    "medium": Model(name="medium", context_tokens=128_000, price_per_million_input=3.0),
    "large": Model(name="large", context_tokens=200_000, price_per_million_input=15.0),
}


def find_model(name: str) -> Model | None:
    """Look a model up by name, or return None when the name is unknown."""
    return CATALOG.get(name)


def describe(name: str) -> str:
    """One-line human summary of a model.

    FIX A. The early return is the narrowing. After `if model is None:
    return ...`, mypy knows that on every remaining line `model` is a Model,
    not a `Model | None`, so reading .name and .context_tokens is safe. The
    guard is for the reader, the runtime and the checker at once.
    """
    model = find_model(name)
    if model is None:
        return f"{name}: unknown model"
    return f"{model.name}: {model.context_tokens:,} token context"


def estimate_cost(name: str, tokens: int) -> float:
    """Dollar cost of sending `tokens` input tokens to `name`."""
    model = find_model(name)
    if model is None:
        raise KeyError(name)
    return tokens / 1_000_000 * model.price_per_million_input


def split_cost(name: str, tokens: int, parts: int) -> float:
    """Cost of one part when a job of `tokens` tokens is split into `parts`.

    FIX B. Floor division keeps the value an int, which is what a token count
    is. `/` would have produced a float, and a fractional token is not a
    thing that exists.
    """
    per_part = tokens // parts
    return estimate_cost(name, per_part)


def format_price(value: float) -> str:
    """Format a price in dollars. FIX: annotated, so strict mode is happy."""
    return f"${value:.2f}"


def price_line(name: str) -> str:
    """Human-readable price for one model."""
    model = find_model(name)
    if model is None:
        return f"{name}: unknown model"
    return f"{name}: {format_price(model.price_per_million_input)} per million tokens"


def load_settings(path: str) -> dict[str, float]:
    """Read numeric settings from a JSON file.

    FIX: json.load returns Any, and returning Any from a function that
    promises dict[str, float] is a promise you have not kept. Binding the
    result to a name annotated `object` throws away the Any immediately, and
    then the isinstance check narrows it to a dict the checker will let you
    iterate. The conversion to float is the value check that no type system
    can do for you.
    """
    with open(path, encoding="utf-8") as handle:
        raw: object = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a JSON object at the top level")
    settings: dict[str, float] = {}
    for key, value in raw.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{path}: setting {key!r} is not a number")
        settings[str(key)] = float(value)
    return settings
