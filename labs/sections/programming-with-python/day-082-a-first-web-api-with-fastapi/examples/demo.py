"""A narrated walk through the bookmarks API, driven entirely in-process.

Run it:

    python3 examples/demo.py

Every request below goes through ``TestClient``, so no server is started,
no port is bound and no socket is opened. The clock and the id source are
frozen so that this script prints the same thing every time — which is what
makes its output safe to check in as `expected-output/sample-run.txt`.

Read it top to bottom and you have the day's whole story: a created
resource with a 201 and a Location, a rejected body with a 422 that names
the field, a missing resource with a 404 instead of a crash, a partial
update, a 204 that means "gone", the internal field that never appears, and
the machine-readable contract the framework wrote for you.
"""

from __future__ import annotations

import itertools
import json
import sys
import warnings
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# starlette 1.3.1 warns that a future release prefers httpx2 over the pinned
# httpx 0.28.1. The pinned pair works; the notice would only make this
# script's captured output noisier. troubleshooting.md explains it.
warnings.filterwarnings(
    "ignore", message="Using `httpx` with `starlette.testclient` is deprecated"
)

import api  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from storage import InMemoryStorage  # noqa: E402


def show(label: str, response: object) -> None:
    """Print one exchange the way a reader can check it."""
    status = getattr(response, "status_code")
    text = getattr(response, "text")
    print(f"\n{label}")
    print(f"  -> {status}")
    location = getattr(response, "headers").get("location")
    if location:
        print(f"  -> Location: {location}")
    if text:
        try:
            body = json.dumps(json.loads(text), indent=2, sort_keys=False)
        except json.JSONDecodeError:
            body = text
        for line in body.splitlines():
            print(f"     {line}")
    else:
        print("     (empty body)")


def main() -> int:
    store = InMemoryStorage()
    counter = itertools.count(1)
    api.app.dependency_overrides[api.get_storage] = lambda: store
    api.app.dependency_overrides[api.get_now] = lambda: datetime(
        2026, 7, 19, 9, 30, tzinfo=UTC
    )
    api.app.dependency_overrides[api.get_new_id] = lambda: f"bm-{next(counter):04d}"
    api.app.dependency_overrides[api.get_owner_token] = lambda: "secret-owner-token"

    client = TestClient(api.app)

    print("=" * 72)
    print("Bookmarks API — an in-process session (no server, no socket)")
    print("=" * 72)

    show(
        "POST /bookmarks   (a valid body)",
        client.post(
            "/bookmarks",
            json={
                "title": "The FastAPI documentation",
                "url": "https://fastapi.tiangolo.com/",
                "tags": ["python", "web"],
            },
        ),
    )

    show(
        "POST /bookmarks   (a second one, tagged differently)",
        client.post(
            "/bookmarks",
            json={
                "title": "The pydantic documentation",
                "url": "https://docs.pydantic.dev/latest/",
                "tags": ["python", "validation"],
            },
        ),
    )

    show(
        "POST /bookmarks   (empty title, and the url is not a url)",
        client.post("/bookmarks", json={"title": "", "url": "not a url"}),
    )

    show(
        "POST /bookmarks   (a client trying to choose its own id)",
        client.post(
            "/bookmarks",
            json={"title": "Sneaky", "url": "https://example.com/", "id": "admin"},
        ),
    )

    show("GET  /bookmarks?tag=validation", client.get("/bookmarks?tag=validation"))

    show("GET  /bookmarks?limit=0   (out of range)", client.get("/bookmarks?limit=0"))

    show("GET  /bookmarks/bm-0001", client.get("/bookmarks/bm-0001"))

    show("GET  /bookmarks/nope     (does not exist)", client.get("/bookmarks/nope"))

    show(
        "PATCH /bookmarks/bm-0001  (title only)",
        client.patch("/bookmarks/bm-0001", json={"title": "FastAPI docs"}),
    )

    show("DELETE /bookmarks/bm-0002", client.delete("/bookmarks/bm-0002"))

    show("GET  /bookmarks/bm-0002  (after deletion)", client.get("/bookmarks/bm-0002"))

    show("GET  /health", client.get("/health"))

    print("\n" + "=" * 72)
    print("What the server kept, versus what it sent")
    print("=" * 72)
    kept = store.get("bm-0001")
    assert kept is not None
    print(f"  stored owner_token : {kept.owner_token}")
    sent = client.get("/bookmarks/bm-0001")
    print(f"  owner_token in the response body? {'owner_token' in sent.text}")
    print(f"  the secret string in the response body? {kept.owner_token in sent.text}")

    print("\n" + "=" * 72)
    print("The contract FastAPI generated from the annotations")
    print("=" * 72)
    schema = client.get("/openapi.json").json()
    print(f"  openapi version : {schema['openapi']}")
    print(f"  title / version : {schema['info']['title']} {schema['info']['version']}")
    for path in sorted(schema["paths"]):
        methods = ", ".join(sorted(m.upper() for m in schema["paths"][path]))
        print(f"  {path:28} {methods}")
    print("  component schemas:", ", ".join(sorted(schema["components"]["schemas"])))
    out_fields = sorted(schema["components"]["schemas"]["BookmarkOut"]["properties"])
    print("  BookmarkOut fields:", ", ".join(out_fields))

    api.app.dependency_overrides.clear()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
