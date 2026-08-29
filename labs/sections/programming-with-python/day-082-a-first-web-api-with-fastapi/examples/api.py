"""The bookmarks API — six routes, three injected boundaries, no globals.

Run it for real with an ASGI server:

    uvicorn api:app --reload --host 127.0.0.1 --port 8123

Then open the interactive documentation at ``/docs`` on that host and port,
or fetch the machine-readable contract at ``/openapi.json``. The lab's tests
do none of that: they drive this same ``app`` object in-process through
``TestClient``, which opens no socket at all.

The three boundaries this module refuses to reach for:

  * ``get_storage`` — where records live. Production: a JSON file. Tests:
    an in-memory dictionary. The handlers never know which.
  * ``get_now``     — the clock. Tests freeze it, so ``created_at`` is a
    value you can assert on rather than a moving target.
  * ``get_new_id``  — identifier generation. Tests make it a counter, so
    the first bookmark is always ``bm-0001``.

Each is an ordinary function. ``Depends`` calls it per request and passes
the result in. ``app.dependency_overrides`` swaps it in a test. That is the
whole mechanism.
"""

from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from models import (
    BookmarkCreate,
    BookmarkOut,
    BookmarkUpdate,
    HealthOut,
    StoredBookmark,
)
from storage import JsonFileStorage, Storage

app = FastAPI(
    title="Bookmarks API",
    version="1.0.0",
    summary="A small, honest CRUD API used to learn FastAPI on Day 082.",
    description=(
        "Create, list, read, update and delete bookmarks. Every request body "
        "is validated by a pydantic model; every response body is filtered "
        "through a response model so internal fields cannot leak."
    ),
)


# --------------------------------------------------------------------------
# Dependencies — the three boundaries, each replaceable in a test.
# --------------------------------------------------------------------------


def get_storage() -> Storage:
    """Production storage: a JSON file whose path comes from the environment.

    Reading configuration from the environment rather than hard-coding it is
    the same rule Day 078 stated for tokens. The default is deliberately a
    relative filename so that running the server in a scratch directory does
    not scatter files somewhere surprising.
    """
    return JsonFileStorage(Path(os.environ.get("BOOKMARKS_FILE", "bookmarks.json")))


def get_now() -> datetime:
    """Production clock. Timezone-aware and in UTC, always."""
    return datetime.now(tz=UTC)


def get_new_id() -> str:
    """Production identifier source. Server-generated, never client-supplied."""
    return uuid4().hex[:12]


def get_owner_token() -> str:
    """An internal per-record secret. Stored, never returned."""
    return secrets.token_hex(8)


StorageDep = Annotated[Storage, Depends(get_storage)]
NowDep = Annotated[datetime, Depends(get_now)]
NewIdDep = Annotated[str, Depends(get_new_id)]
OwnerTokenDep = Annotated[str, Depends(get_owner_token)]


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------


@app.get("/health", response_model=HealthOut, tags=["meta"])
async def health(storage: StorageDep) -> HealthOut:
    """A liveness check.

    Declared ``async def`` purely to show that it is allowed. This handler
    does no waiting, so it gains nothing from being a coroutine; a handler
    that awaited a network call or a database driver would.
    """
    return HealthOut(status="ok", bookmarks=len(storage.all()))


@app.post(
    "/bookmarks",
    response_model=BookmarkOut,
    status_code=status.HTTP_201_CREATED,
    tags=["bookmarks"],
    summary="Create a bookmark",
)
def create_bookmark(
    payload: BookmarkCreate,
    storage: StorageDep,
    now: NowDep,
    new_id: NewIdDep,
    owner_token: OwnerTokenDep,
    response: Response,
) -> StoredBookmark:
    """201 Created, with a Location header naming the new resource.

    The return annotation is ``StoredBookmark`` — the object with the secret
    in it — and that is safe, because ``response_model=BookmarkOut`` filters
    the response before it is serialized. The handler returns the truth; the
    declaration decides what the client is entitled to see.
    """
    record = StoredBookmark(
        id=new_id,
        title=payload.title,
        url=payload.url,
        tags=payload.tags,
        created_at=now,
        owner_token=owner_token,
    )
    storage.add(record)
    response.headers["Location"] = f"/bookmarks/{record.id}"
    return record


@app.get(
    "/bookmarks",
    response_model=list[BookmarkOut],
    tags=["bookmarks"],
    summary="List bookmarks, optionally filtered by tag",
)
def list_bookmarks(
    storage: StorageDep,
    tag: Annotated[
        str | None,
        Query(description="Return only bookmarks carrying this tag."),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of bookmarks to return."),
    ] = 20,
) -> list[StoredBookmark]:
    """``tag`` is optional; ``limit`` has a default and a validated range.

    ``limit`` arrives from the query string as text and is handed to the
    handler as an ``int``, because the annotation said ``int``. Ask for
    ``?limit=0`` or ``?limit=abc`` and the handler is never entered: the
    caller gets a 422 naming ``limit``.
    """
    items = storage.all()
    if tag is not None:
        items = [b for b in items if tag in b.tags]
    return items[:limit]


@app.get(
    "/bookmarks/{bookmark_id}",
    response_model=BookmarkOut,
    tags=["bookmarks"],
    summary="Fetch one bookmark",
    responses={404: {"description": "No bookmark with that id"}},
)
def get_bookmark(bookmark_id: str, storage: StorageDep) -> StoredBookmark:
    """404 when it is not there — an answer, not a crash.

    ``HTTPException`` is how a handler says "this request has a definite,
    non-exceptional negative answer". The client gets a small JSON body with
    a ``detail`` string. It does not get a traceback, and it must not: a
    traceback names your files, your line numbers and your local variables.
    """
    found = storage.get(bookmark_id)
    if found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bookmark with id {bookmark_id!r}",
        )
    return found


@app.patch(
    "/bookmarks/{bookmark_id}",
    response_model=BookmarkOut,
    tags=["bookmarks"],
    summary="Update part of a bookmark",
    responses={404: {"description": "No bookmark with that id"}},
)
def update_bookmark(
    bookmark_id: str, payload: BookmarkUpdate, storage: StorageDep
) -> StoredBookmark:
    """A partial update: only the fields the caller actually sent change."""
    found = storage.get(bookmark_id)
    if found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bookmark with id {bookmark_id!r}",
        )
    changes = payload.model_dump(exclude_unset=True)
    updated = found.model_copy(update=changes)
    storage.replace(updated)
    return updated


@app.delete(
    "/bookmarks/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["bookmarks"],
    summary="Delete a bookmark",
    responses={404: {"description": "No bookmark with that id"}},
)
def delete_bookmark(bookmark_id: str, storage: StorageDep) -> Response:
    """204 No Content: it worked, and there is deliberately nothing to say.

    A 204 body must be empty — that is what the status code means — so this
    handler returns a bare ``Response`` rather than a model.
    """
    if not storage.delete(bookmark_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bookmark with id {bookmark_id!r}",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
