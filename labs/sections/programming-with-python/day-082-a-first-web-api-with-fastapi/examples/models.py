"""The data contract of the bookmarks API, written as pydantic models.

Four models, and the reason there are four rather than one is the whole point
of this file:

  * ``BookmarkCreate``  — what a caller is allowed to SEND when creating.
  * ``BookmarkUpdate``  — what a caller is allowed to SEND when patching;
                          every field optional, because a PATCH changes some
                          fields and leaves the rest alone.
  * ``StoredBookmark``  — what the server keeps INTERNALLY. It has one field
                          the outside world must never see: ``owner_token``.
  * ``BookmarkOut``     — what a caller is allowed to RECEIVE.

A single shared model would have been fewer lines and a security bug. The
create model has no ``id`` and no ``created_at``, so a caller cannot choose
its own identifier or backdate a record; the output model has no
``owner_token``, so an internal secret cannot leak just because somebody
returned the wrong object. FastAPI enforces the output side for you: declare
``response_model=BookmarkOut`` on a handler and whatever the handler returns
is filtered down to those fields before it is serialized.

Note what the annotations are doing here, because it is different from
Day 069 and Day 075. There, an annotation was a claim a separate program
checked before you ran. Here the annotation is read at import time by
pydantic, compiled into a validator, and executed against real data at
runtime. Same syntax; a completely different job.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# `extra="forbid"` turns an unexpected field into a 422 instead of silently
# ignoring it. Silently ignoring is the default and it is the reason people
# spend afternoons wondering why `titel="..."` had no effect.
STRICT = ConfigDict(extra="forbid")


class BookmarkCreate(BaseModel):
    """The request body of ``POST /bookmarks``."""

    model_config = STRICT

    title: str = Field(
        min_length=1,
        max_length=80,
        description="Human-readable name. Must not be empty.",
    )
    url: HttpUrl = Field(description="Absolute http or https URL.")
    tags: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Up to eight short labels.",
    )


class BookmarkUpdate(BaseModel):
    """The request body of ``PATCH /bookmarks/{bookmark_id}``.

    Every field is optional and defaults to ``None``, which is how a partial
    update says "leave this one alone". ``model_dump(exclude_unset=True)``
    then tells you which fields the caller actually sent — note that this is
    genuinely different from which fields are ``None``, because a caller may
    legitimately send a field whose value is null.
    """

    model_config = STRICT

    title: str | None = Field(default=None, min_length=1, max_length=80)
    url: HttpUrl | None = None
    tags: list[str] | None = Field(default=None, max_length=8)


class StoredBookmark(BaseModel):
    """What the server keeps. Never returned to a client as-is."""

    id: str
    title: str
    url: HttpUrl
    tags: list[str]
    created_at: datetime
    owner_token: str
    """An internal server-side secret. If this ever appears in a response
    body, the API has a data-leak bug. The lab's test suite asserts on its
    absence explicitly, because a leak is invisible until someone looks."""


class BookmarkOut(BaseModel):
    """What a client receives. Deliberately a subset of ``StoredBookmark``."""

    id: str
    title: str
    url: HttpUrl
    tags: list[str]
    created_at: datetime


class HealthOut(BaseModel):
    """The body of ``GET /health``."""

    status: str
    bookmarks: int
