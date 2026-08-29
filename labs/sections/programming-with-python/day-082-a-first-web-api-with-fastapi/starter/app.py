"""Your bookmarks API — a working skeleton with eight exercises.

This file RUNS right now. Prove it before you change anything:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements/requirements.txt
    .venv/bin/pytest starter -q

You should see one test pass and nine skipped. Each skipped test names the
exercise that makes it pass. Work through them in order; after each one,
rerun the command above and delete the `@pytest.mark.skip` line from the
test you just satisfied.

What is here already is deliberately the *naive* version — the version
somebody writes on the first afternoon and regrets on the second:

  * one shared model for input and output, so a client can set fields it
    has no business setting, and the server returns fields it should never
    send;
  * a module-level dictionary for storage, which Day 074 told you makes a
    boundary untestable;
  * every response a 200, because nobody chose a status code;
  * no error handling, so a missing bookmark is a crash.

The exercises turn it into the version in `examples/`. Run the reference
implementation any time you want to see where you are heading:

    python3 examples/demo.py

To run this app for real, from the lab directory:

    .venv/bin/uvicorn app:app --reload --host 127.0.0.1 --port 8123 --app-dir starter

Then visit /docs on that host and port in a browser. The tests never do
this — they use TestClient, which drives the app in this process and opens
no socket.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Bookmarks API", version="0.1.0")

# EXERCISE 7 replaces this module-level dictionary with an injected
# dependency. Until then, storage is a global — which is exactly why the
# tests below cannot start from a clean slate without reaching in and
# clearing it.
BOOKMARKS: dict[str, "Bookmark"] = {}


class Bookmark(BaseModel):
    """One model doing three jobs badly.

    EXERCISE 1: give `title` a minimum length of 1 and a maximum of 80, and
                change `url` from `str` to pydantic's `HttpUrl`, so that an
                empty title and the text "not a url" are both rejected with
                a 422 before any handler runs.
                Import them with:  from pydantic import Field, HttpUrl

    EXERCISE 2: split this into three models.
                  BookmarkCreate  — title, url, tags. No id, no created_at,
                                    no owner_token. Add
                                    model_config = ConfigDict(extra="forbid")
                                    so an unexpected field is a 422 rather
                                    than being silently dropped.
                  StoredBookmark  — everything, including owner_token.
                  BookmarkOut     — everything EXCEPT owner_token.
                Then put `response_model=BookmarkOut` on every handler that
                returns a bookmark. That single declaration is what stops
                the internal field leaving the process.
    """

    id: str = ""
    title: str
    url: str
    tags: list[str] = []
    created_at: datetime | None = None
    owner_token: str = ""


@app.get("/health")
async def health() -> dict[str, object]:
    """Already correct, and already `async def` — which is allowed and,
    here, gains nothing, because this handler never waits for anything."""
    return {"status": "ok", "bookmarks": len(BOOKMARKS)}


@app.post("/bookmarks")
def create_bookmark(payload: Bookmark) -> Bookmark:
    """Creates a bookmark and returns 200.

    EXERCISE 3: a creation is a 201, not a 200. Add
                `status_code=status.HTTP_201_CREATED` to the decorator
                (import `status` from fastapi), and set a Location header
                naming the new resource. To set a header, add a parameter
                `response: Response` and assign
                `response.headers["Location"] = f"/bookmarks/{record.id}"`.
    """
    record = payload.model_copy(
        update={
            "id": secrets.token_hex(4),
            "created_at": datetime.now(tz=UTC),
            "owner_token": secrets.token_hex(8),
        }
    )
    BOOKMARKS[record.id] = record
    return record


@app.get("/bookmarks")
def list_bookmarks() -> list[Bookmark]:
    """Returns everything, always.

    EXERCISE 4: add two query parameters.
                  tag: str | None = None   — return only bookmarks carrying
                                             this tag; absent means "all".
                  limit: int = 20          — how many at most. Constrain it
                                             with
                                             Annotated[int, Query(ge=1, le=100)]
                                             so that ?limit=0 is a 422 that
                                             names `limit`.
    """
    return list(BOOKMARKS.values())


@app.get("/bookmarks/{bookmark_id}")
def get_bookmark(bookmark_id: str) -> Bookmark:
    """Crashes with a KeyError when the bookmark is not there.

    EXERCISE 5: look the bookmark up, and when it is missing raise
                HTTPException(status_code=404, detail=...) instead. A
                missing thing is an ANSWER, not a failure — and a client
                must never receive a traceback, because a traceback names
                your files, your line numbers and your local variables.
    """
    return BOOKMARKS[bookmark_id]


# EXERCISE 6: add the two routes this API is missing.
#
#   @app.patch("/bookmarks/{bookmark_id}")  — a partial update. Take a
#       BookmarkUpdate model whose fields are all optional, and apply only
#       the ones the caller actually sent:
#           changes = payload.model_dump(exclude_unset=True)
#           updated = found.model_copy(update=changes)
#       404 when the bookmark does not exist.
#
#   @app.delete("/bookmarks/{bookmark_id}")  — status_code 204. A 204 means
#       "it worked and there is deliberately nothing to say", so the body
#       must be empty: return Response(status_code=204). 404 when there was
#       nothing to delete.
#
# EXERCISE 7: stop using the BOOKMARKS global.
#   Write a `get_storage()` function that returns a storage object, annotate
#   each handler's storage parameter as
#       Annotated[Storage, Depends(get_storage)]
#   and let FastAPI pass it in. Then a test can swap it with
#       app.dependency_overrides[get_storage] = lambda: InMemoryStorage()
#   and no test ever touches a real file. Do the same for the clock
#   (`get_now`) and the id source (`get_new_id`) so `created_at` and `id`
#   become values a test can assert on rather than moving targets.
#   `examples/storage.py` has a Protocol and two implementations to copy.
#
# EXERCISE 8: ask the application what it now promises.
#   Run `python3 starter/schema.py` to print the generated OpenAPI schema.
#   Check that every path you declared is there, that the 201, 204 and 404
#   you chose are recorded, and that `owner_token` appears nowhere in
#   `components.schemas.BookmarkOut.properties`.
