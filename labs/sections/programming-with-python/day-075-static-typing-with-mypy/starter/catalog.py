"""A small model catalogue — annotated, tested, and quietly wrong.

This module is the subject of the whole lab. Every function carries type
annotations, and the pytest suite in `test_catalog.py` passes green. It still
contains real bugs, because a passing test suite only proves that the paths
the tests walk behave as expected. mypy reads every path.

Your exercises are numbered below. Do NOT fix anything before you have run
both tools once and seen the difference for yourself.

  Exercise 1 — run the tests and watch them pass:
      python3 -m pytest starter/test_catalog.py
  Exercise 2 — run mypy on this file and read the report:
      python3 -m mypy starter/catalog.py
  Exercise 3 — write down each error's file, line, message and error code.
  Exercise 4 — fix bug A (marked below) so [union-attr] disappears.
  Exercise 5 — fix bug B (marked below) so [arg-type] disappears.
  Exercise 6 — run mypy in strict mode and handle what it adds:
      python3 -m mypy --strict starter/catalog.py
  Exercise 7 — prove the Any cautionary point with starter/any_demo.py.

The finished, strict-clean version is in examples/catalog.py. Compare only
after you have tried.
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

    BUG A. find_model returns `Model | None`, and this function reads
    attributes off the result without ever asking whether it is None. Every
    test calls describe() with a name that exists, so the suite never walks
    the None path. Exercise 4: teach the checker (and the reader) that the
    None case is handled, by returning early when the lookup fails.
    """
    model = find_model(name)
    return f"{model.name}: {model.context_tokens:,} token context"


def estimate_cost(name: str, tokens: int) -> float:
    """Dollar cost of sending `tokens` input tokens to `name`."""
    model = find_model(name)
    if model is None:
        raise KeyError(name)
    return tokens / 1_000_000 * model.price_per_million_input


def split_cost(name: str, tokens: int, parts: int) -> float:
    """Cost of one part when a job of `tokens` tokens is split into `parts`.

    BUG B. In Python 3 the `/` operator always produces a float, even when
    both operands are integers and the division is exact. estimate_cost is
    annotated to take an int. The test happens to use numbers that divide
    evenly, so the arithmetic is right and the test is green — but the type
    is wrong, and the day it stops dividing evenly you get a fractional token
    count nobody asked for. Exercise 5: use floor division instead.
    """
    per_part = tokens / parts
    return estimate_cost(name, per_part)


def format_price(value):
    """Format a price in dollars.

    Exercise 6: this function has no annotations at all. Under default
    settings mypy simply skips it. Under --strict it is an error, and so is
    calling it from an annotated function. Annotate it.
    """
    return f"${value:.2f}"


def price_line(name: str) -> str:
    """Human-readable price for one model."""
    model = find_model(name)
    if model is None:
        return f"{name}: unknown model"
    return f"{name}: {format_price(model.price_per_million_input)} per million tokens"


def load_settings(path: str) -> dict[str, float]:
    """Read numeric settings from a JSON file.

    Exercise 6 (continued): json.load is annotated to return Any, so this
    function hands back Any while promising dict[str, float]. Default mypy
    says nothing. --strict turns on warn_return_any and reports it. The fix
    is not to silence the warning but to check the value at the boundary:
    narrow the loaded object with isinstance, then build the dict you
    promised.
    """
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
