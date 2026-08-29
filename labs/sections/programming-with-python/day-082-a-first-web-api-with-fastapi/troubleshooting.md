# Troubleshooting — Day 082 lab

Every symptom below was produced on the authoring machine while building this
lab, or is a mistake the exercises make easy to make. Nothing here is
hypothetical filler.

## `ModuleNotFoundError: No module named 'fastapi'`

The `python3` or `pytest` you ran is not the one you installed into.

```bash
cd labs/sections/programming-with-python/day-082-a-first-web-api-with-fastapi
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest examples
```

`tests/run_tests.sh` resolves `pytest` itself — an explicit `PYTEST=` first,
then `.venv/bin/pytest`, then `PATH` — and then uses the `python3` sitting
beside it. If FastAPI is not importable from that interpreter it stops with
install instructions rather than skipping checks.

## `ModuleNotFoundError: No module named 'api'` (or `models`, or `storage`)

The lab's modules import each other by bare name (`from models import ...`),
which requires their own directory to be on `sys.path`. Both `conftest.py`
files put it there, so running pytest works from anywhere. Running a file
directly does not, which is why `examples/demo.py` and `starter/schema.py`
each insert their directory themselves. If you copy a snippet into a new
file of your own, copy that `sys.path.insert` line too — or run pytest.

## `StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead`

Real, expected, and harmless with the pinned versions. Starlette 1.3.1 is
signalling that a future release will prefer the `httpx2` package over
`httpx` 0.28.1. Everything works today — all 42 reference tests pass — so
the two `pytest.ini` files filter this one message so the captured output
stays readable. It is filtered by its exact text, not by silencing warnings
in general, so a different deprecation would still reach you.

If you would rather see it, delete the `filterwarnings` block from
`examples/pytest.ini`, or run `pytest examples -W always`.

## `422 Unprocessable Content` when you expected a `200`

This is validation working. Read the body — it tells you exactly what is
wrong and where:

```json
{"detail": [{"type": "string_too_short", "loc": ["body", "title"],
             "msg": "String should have at least 1 character", "input": ""}]}
```

`loc` is the path to the offending value: `["body", "title"]` means the
`title` field of the request body; `["query", "limit"]` means the `limit`
query parameter; `["path", "item_id"]` means the value in the URL itself.
The three most common causes in this lab:

- an empty `title` (minimum length 1);
- a `url` that is not an absolute URL — `"fastapi.tiangolo.com"` is not, and
  `"https://fastapi.tiangolo.com/"` is;
- a field the create model does not declare. `extra="forbid"` turns a
  misspelled `titel` or a hopeful `id` into a 422 rather than dropping it
  silently, which is a feature, not an obstacle.

## `AssertionError` comparing a URL to a string

`HttpUrl` normalises what it parses. Send `https://fastapi.tiangolo.com` and
the response carries `https://fastapi.tiangolo.com/` — a trailing slash was
added, because that is the canonical form of a URL with an empty path. Assert
against the normalised value, or send the normalised value in the first
place. This is validation doing its second job: not just rejecting bad input
but canonicalising good input, so downstream code sees one spelling.

## `KeyError` instead of a 404, and a 500 in the response

That is the unfinished `starter/app.py`, Exercise 5. `BOOKMARKS[bookmark_id]`
raises `KeyError` when the id is unknown; nothing catches it; the server
turns any uncaught exception into a 500. Raise
`HTTPException(status_code=404, detail=...)` instead. A missing thing is an
answer, not a failure.

## A 500 with the body `Internal Server Error` and nothing else

Correct and deliberate: a client must never receive a traceback, because a
traceback names your files, your line numbers and your local variables. The
traceback is printed on the server side, where you can read it. Under
`TestClient` the default is to re-raise the exception into your test instead,
which is more useful when debugging;
`examples/test_type_demo.py::test_an_unhandled_exception_becomes_a_500_with_no_traceback`
uses `TestClient(app, raise_server_exceptions=False)` to see what a real
client would see.

## `assert response.status_code == 200` fails with `307`

You asked for a path whose trailing slash does not match the declared route.
The routes here are `/bookmarks` and `/bookmarks/{bookmark_id}`; requesting
`/bookmarks/` redirects. `TestClient` follows redirects by default, so you
normally never notice — until you pass `follow_redirects=False`.

## The response `created_at` changes on every run

Expected, until Exercise 7. The unfinished app calls `datetime.now()` inside
the handler, so the value is different every time and nothing can assert on
it. Inject the clock — `Annotated[datetime, Depends(get_now)]` — and a test
overrides it with a fixed value. That is Day 074's argument applied to time
rather than to the network.

## `AssertionError: the real JsonFileStorage was constructed in a test`

Your override did not take effect, so a handler asked for storage and got the
production one. Check that the key in `app.dependency_overrides` is the
dependency **function object** (`api.get_storage`), not its name and not a
copy imported under a different alias.

## `NetworkAccessAttempted: a test tried to connect to ...`

Something in the run tried to open a socket. That is the guard in
`conftest.py` doing exactly its job. Nothing in this lab should ever trip it;
if your own code does, you have reached for a real service instead of
injecting a fake.

## `uvicorn: command not found`, or the server starts and nothing responds

`uvicorn` lives in the lab's environment, so run `.venv/bin/uvicorn`. From
the lab directory:

```bash
.venv/bin/uvicorn api:app --reload --host 127.0.0.1 --port 8123 --app-dir examples
```

`--app-dir` is what puts `examples/` on the import path so `api:app` resolves.
If port 8123 is already taken, pick another number — the port is yours to
choose, and nothing in the tests depends on it.

## Windows

Use WSL and follow the Linux instructions. Native Windows works too:
substitute `python` for `python3` and `.venv\Scripts\` for `.venv/bin/`.
Nothing in this lab depends on path separators, and no test binds a port, so
firewall prompts never appear.
