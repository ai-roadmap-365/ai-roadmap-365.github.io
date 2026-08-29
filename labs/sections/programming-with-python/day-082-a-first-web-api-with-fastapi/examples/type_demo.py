"""A three-route application whose only job is to show type conversion.

Everything arriving in a URL is text. ``/items/7`` carries the two
characters ``7``, not the number seven. The annotation is what turns one
into the other — and what produces a 422 when the text cannot be turned
into the declared type at all.

Nothing in here is part of the bookmarks API; it exists so the lesson can
quote real output for the smallest possible case.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI(title="Type conversion demo", version="1.0.0")


@app.get("/items/{item_id}")
def read_item(item_id: int) -> dict[str, object]:
    """``item_id`` is declared ``int``, so the handler receives an int."""
    return {"item_id": item_id, "python_type": type(item_id).__name__}


@app.get("/search")
def search(
    q: str,
    page: int = 1,
    verbose: bool = False,
    sort: Annotated[str | None, Query(max_length=16)] = None,
) -> dict[str, object]:
    """``q`` is required; the other three have defaults, so they are optional.

    ``verbose`` accepts the spellings HTTP actually carries — ``true``,
    ``1``, ``yes``, ``on`` and their opposites — and hands the handler a
    real ``bool``.
    """
    return {"q": q, "page": page, "verbose": verbose, "sort": sort}


@app.get("/ratio/{numerator}/{denominator}")
def ratio(numerator: float, denominator: float) -> dict[str, float]:
    """Deliberately unguarded, to show what an unhandled exception does.

    Ask for ``/ratio/1/0`` and this raises ``ZeroDivisionError``. Nothing
    catches it, so the caller gets a 500 with a five-word body while the
    traceback stays in the server log where it belongs.
    """
    return {"result": numerator / denominator}
