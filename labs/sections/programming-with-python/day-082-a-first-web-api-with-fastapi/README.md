# Day 082 lab — Serve Something Real

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** A First Web API with FastAPI
- **Day number:** 82 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-082-a-first-web-api-with-fastapi
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-082-a-first-web-api-with-fastapi` when the site is running.
<!-- generated-links:end -->

## Purpose

Four days ago you learned to be an HTTP client. On Day 82 you become the
server, and this lab is where that inversion becomes concrete: every status
code, header and JSON body you were *reading* is now something you *choose*
and are answerable for.

You build a small bookmarks API — create, list with filtering, fetch one,
update part of one, delete — and you build it the way a working one is built
rather than the way a tutorial one is. That means four things:

1. **Separate models for input and output.** The stored record carries an
   internal `owner_token`; the output model does not; `response_model` is
   what stands between them. The suite asserts that field's *absence*
   explicitly, because a data leak is invisible until somebody looks.
2. **Real validation at the boundary.** A title must be non-empty and at
   most 80 characters, a URL must actually be a URL, an unexpected field is
   rejected rather than ignored, and every rejection is a 422 whose
   structured `detail` names the exact field.
3. **Deliberate status codes.** 201 with a `Location` header for creation,
   204 with an empty body for deletion, 404 for a thing that is not there —
   an answer, not a crash.
4. **Injected boundaries.** Storage, the clock and the id source all arrive
   through `Depends`, so the tests hand the application an in-memory fake and
   no test touches a file, a database or a socket.

And the point the whole week has been building to: **the tests drive the
application through `TestClient`, which speaks to the app object in this
process through httpx and opens no socket at all.** That is the cleanest
possible form of Week 12's network rule — not a local server on an ephemeral
port that must be started and waited for and shut down, but no server. The
reference suite additionally runs behind a guard that raises on any outbound
connection, and section 7 of the harness proves the guard is armed by making
a test trip it on purpose.

The starter is the naive version — one shared model, a module-level
dictionary, every response a 200, a missing bookmark a crash. Eight exercises
turn it into the reference implementation.

## Learning objectives

- Declare a path operation with FastAPI and explain what the decorator, the
  path string and the function signature each contribute.
- Use path parameters, query parameters with defaults and constraints, and a
  pydantic model as a request body, and describe how an annotation causes
  conversion and validation to happen at runtime.
- Read a 422 response: find the offending field in `detail[n].loc` and the
  reason in `detail[n].type`, and fix the request accordingly.
- Declare a response model and state two things it buys you — a documented
  contract and a filter that stops internal fields leaving the process.
- Choose status codes deliberately: 200, 201 with `Location`, 204, 404, 422,
  and the 500 you never choose.
- Raise `HTTPException` for a known negative answer, and explain why a
  traceback must never reach a client.
- Inject a dependency with `Depends`, override it with
  `app.dependency_overrides`, and test the application without touching the
  real boundary.
- Read the generated OpenAPI schema and check it against what you meant to
  promise, including checking that no internal field appears in it.
- Explain why `TestClient` needs no server, no port and no readiness wait.

## Prerequisites

- The Day 82 lesson — read it first; this lab is its exercise set.
- Day 78: HTTP itself. Methods, status codes, headers, query strings, JSON
  request and response bodies. Today is the same vocabulary from the other
  side of the wire.
- Days 67–70: classes, dataclasses, and modelling a domain with objects.
  A pydantic model is a class whose annotations do work.
- Day 75: type annotations and what a static checker does with them. Today
  the same annotations are read by a different tool at a different moment.
- Day 74: injecting a boundary so a test can substitute a fake. `Depends` is
  that idea with framework support.
- Days 71–73: pytest, fixtures, and writing tests that can fail.
- Day 43: `python3 -m venv` and installing packages with `pip`.
- A text editor, a terminal, and one-time network access to install five
  packages.

## Supported operating systems

- **macOS** — fully supported (tested on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.10 or newer,
  bash and `pip`).
- **Windows** — use WSL and follow the Linux path. Native Windows works too:
  substitute `python` for `python3` and `.venv\Scripts\` for `.venv/bin/`.
  Nothing here depends on path separators or line endings, and because no
  test binds a port, no firewall prompt ever appears.

## Hardware requirements

Any computer that runs Python 3. The whole lab is a few dozen kilobytes of
source; the reference suite runs 42 tests in under a second and uses a few
tens of megabytes. No GPU, no special memory, no large download beyond the
packages themselves.

## Required software

- `python3` — **3.11 or newer** (the code uses `datetime.UTC`, added in
  3.11, and `X | None` annotations from 3.10). Tested on 3.14.0.
- `fastapi` 0.139.2, `uvicorn` 0.51.0, `httpx` 0.28.1, `pytest` 9.1.1 and
  `pydantic` 2.13.4, all from
  [`requirements/requirements.txt`](requirements/requirements.txt).
- `bash` for the test runner (preinstalled on macOS and Linux).
- Standard library only in the lab's own logic: `json`, `datetime`,
  `pathlib`, `typing`, `secrets`, `uuid`, `os`, `itertools`.

## Free and open-source options

Everything here is free and open source, with no account, no key and no paid
tier anywhere. FastAPI, Starlette, pydantic, uvicorn, httpx and pytest are
all MIT-licensed and developed in the open.

If you would rather not install a framework at all, the standard library's
`http.server` will serve JSON over HTTP with no dependencies — and writing
even a two-route API with it makes vivid what FastAPI is doing for you,
because you will hand-write the routing, the JSON parsing, the validation and
every status code yourself. The lesson's Alternatives section compares
FastAPI with Flask, Django plus Django REST Framework, Litestar and
`http.server`, states plainly which are installed here (FastAPI is; Flask and
Django are not), and describes the others without inventing output for tools
that were never run.

## Installation

```bash
cd labs/sections/programming-with-python/day-082-a-first-web-api-with-fastapi
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/python3 -c "import fastapi, pydantic; print(fastapi.__version__, pydantic.VERSION)"
```

Expect `0.139.2 2.13.4`. The install needs the network once. **Nothing after
it does** — see "Tests" below.

## File structure

```
day-082-a-first-web-api-with-fastapi/
├── README.md                  this file
├── metadata.yml               machine-readable lab record
├── troubleshooting.md         real symptoms and their causes
├── security.md                validation vs authorization, leaks, CORS, secrets
├── requirements/
│   ├── requirements.txt       five pinned packages
│   └── README.md              what each one is for, and why pydantic is pinned
├── starter/                   YOUR work — runnable now, eight exercises
│   ├── app.py                 the naive version, with the exercises in place
│   ├── test_app.py            10 tests: 1 passing, 9 waiting for you
│   ├── schema.py              Exercise 8 — print the generated contract
│   ├── conftest.py            import path, clean slate, network guard
│   └── pytest.ini
├── examples/                  the reference implementation
│   ├── models.py              four pydantic models and why there are four
│   ├── storage.py             a Protocol and two implementations
│   ├── api.py                 six routes, four injected dependencies
│   ├── type_demo.py           a tiny app for conversion and the 500 case
│   ├── demo.py                a narrated in-process session
│   ├── test_api.py            34 tests over the API
│   ├── test_type_demo.py      8 tests over conversion and error handling
│   ├── conftest.py            import path and the network guard
│   └── pytest.ini
├── tests/
│   └── run_tests.sh           the outer harness: 39 checks
└── expected-output/           captured from real runs on 2026-07-19
    ├── test-run.txt           the full harness output
    ├── sample-run.txt         examples/demo.py
    ├── pytest-examples.txt    the reference suite, verbose
    ├── starter-run.txt        the starter suite before you begin
    └── openapi.json           the generated contract, in full
```

## How to run

From the lab directory, in this order:

```bash
# 1. See the finished API answer real requests, in-process.
.venv/bin/python3 examples/demo.py

# 2. Run the reference suite.
.venv/bin/pytest examples

# 3. See where you are starting from: 1 passed, 9 skipped.
.venv/bin/pytest starter

# 4. Ask your application what it currently promises.
.venv/bin/python3 starter/schema.py

# 5. Work through the eight exercises in starter/app.py, deleting the
#    matching @pytest.mark.skip line each time, and rerun step 3.

# 6. The full harness — this is what has to pass.
bash tests/run_tests.sh
```

And, entirely optionally, run it as a real server:

```bash
.venv/bin/uvicorn api:app --reload --host 127.0.0.1 --port 8123 --app-dir examples
```

Then point a browser at `/docs` on that host and port for the interactive
documentation, or fetch `/openapi.json` for the machine-readable contract.
Stop it with `Ctrl-C`. **No test needs this**, and none of the captured
output came from it — it is here because an application you can only test is
not an application you can ship.

## What the commands do

| Command | What it does | Why it is here |
| --- | --- | --- |
| `python3 examples/demo.py` | Drives the finished API through `TestClient` and prints twelve exchanges with their status codes and bodies | Shows the whole day in one page of output: 201 with a Location, two flavours of 422, a 404 with a detail, a partial update, a 204, and the leak check |
| `pytest examples` | Runs 42 tests over the reference implementation | The assertions the lesson claims exist, actually running |
| `pytest starter` | Runs your suite: 1 passing baseline, 9 skipped exercises | A green baseline first, so a later failure is your code and not your setup |
| `python3 starter/schema.py` | Prints the OpenAPI schema your app generates, then checks it for the leak | Exercise 8 — reading the contract the framework wrote from your annotations |
| `bash tests/run_tests.sh` | The outer harness: 39 checks across eight sections | The grader. It re-verifies every claim independently of the lab's own test files, and proves the leak check and the network guard are not vacuous |
| `uvicorn api:app --host 127.0.0.1 --port 8123 --app-dir examples` | Serves the app for real on the loopback interface | Optional. The honest answer to "but how do I actually run it?" |

## Expected output

Every file in `expected-output/` was captured from a real run on the
authoring machine on 19 July 2026 (macOS 26.5.1, Apple Silicon, Python
3.14.0, fastapi 0.139.2, pydantic 2.13.4, pytest 9.1.1). Absolute paths have
been replaced with `<repo>` and `<venv>`; nothing else was edited.

The harness ends with:

```text
39 checks, 0 failure(s).
```

`examples/demo.py` opens like this — a valid creation, answered with a 201
and a `Location` header:

```text
POST /bookmarks   (a valid body)
  -> 201
  -> Location: /bookmarks/bm-0001
     {
       "id": "bm-0001",
       "title": "The FastAPI documentation",
       "url": "https://fastapi.tiangolo.com/",
       "tags": [
         "python",
         "web"
       ],
       "created_at": "2026-07-19T09:30:00Z"
     }
```

and a request with two bad fields is answered with one 422 naming both:

```text
POST /bookmarks   (empty title, and the url is not a url)
  -> 422
     {
       "detail": [
         {
           "type": "string_too_short",
           "loc": [
             "body",
             "title"
           ],
           "msg": "String should have at least 1 character",
           "input": "",
           "ctx": {
             "min_length": 1
           }
         },
         {
           "type": "url_parsing",
           "loc": [
             "body",
             "url"
           ],
           "msg": "Input should be a valid URL, relative URL without a base",
           "input": "not a url",
           "ctx": {
             "error": "relative URL without a base"
           }
         }
       ]
     }
```

The leak check, at the end of the same run:

```text
  stored owner_token : secret-owner-token
  owner_token in the response body? False
  the secret string in the response body? False
```

The starter, before you begin, is `1 passed, 9 skipped`. The full text of all
five captures is in `expected-output/`.

## Validation steps

Work through these in order; each one is a thing you can check for yourself.

1. `.venv/bin/pytest examples` exits 0 and reports `42 passed`.
2. `.venv/bin/pytest starter` exits 0 and reports `1 passed, 9 skipped`.
   Every skip reason names the exercise that removes it.
3. `python3 examples/demo.py` prints `-> 201` for the first creation and
   `Location: /bookmarks/bm-0001` beneath it.
4. In that same output, the two-bad-fields request prints **two** entries
   under `detail`, one with `"loc": ["body", "title"]` and one with
   `"loc": ["body", "url"]`. Validation reports everything wrong at once.
5. `owner_token in the response body? False` appears near the end. Then open
   `examples/api.py` and delete `response_model=BookmarkOut,` from the create
   route, rerun, and watch it become `True`. Put the line back.
6. `python3 starter/schema.py` exits 0 and, before you start, prints
   `No BookmarkOut schema yet — Exercise 2 creates it.` After Exercise 2 it
   prints the field list and `No leak: owner_token is stored but never
   declared as output.`
7. Search `expected-output/openapi.json` for `owner_token`. It is not there —
   the internal field is absent from the published contract as well as from
   the responses.
8. `bash tests/run_tests.sh` ends `39 checks, 0 failure(s).` and exits 0.
9. `find . -name 'bookmarks.json'` finds nothing after any of the above.

## Tests

```bash
bash tests/run_tests.sh
```

Eight sections, 39 checks, exit 0 only if all of them pass:

1. **Versions** — reprints every installed version and compares it against
   `requirements/requirements.txt`, including pydantic, which nobody
   installed on purpose.
2. **The reference suite** — 42 tests pass, and the eight assertions the
   lesson names are confirmed to exist by test id, not just by count.
3. **Nineteen claims, re-verified independently of pytest** — the harness
   drives the same application from a plain script, so a broken test file
   cannot make the lab look correct: 201 and the response shape, the
   `Location` header, the 422 and the field it names, the 404 and its
   detail, the 204 and its empty body, the resource being gone, the internal
   field being stored and not sent, the schema and its paths and status
   codes, the injected storage, and no file on disk.
4. **The demo script** — runs and contains the exact fragments the lesson
   quotes.
5. **The starter** — runs green with the exercises unfinished, and
   `schema.py` reports the unfinished state honestly.
6. **The starter suite is not vacuous** — the reference implementation is
   dropped in as `app.py`, the skips are stripped, and all 10 starter tests
   must pass; then `response_model=BookmarkOut` is deleted from a copy and
   the suite must go RED, naming the leak check. A test that cannot fail
   protects nothing.
7. **No socket** — a throwaway test that deliberately calls
   `socket.create_connection` must fail with `NetworkAccessAttempted`,
   proving the guard is armed; the reference run must show no such error;
   and no lab source may contain a real client call or a port bind.
8. **No disk** — no `bookmarks.json` anywhere under the lab afterwards.

**The tests need no network.** Installing the packages does, once. After
that, everything runs offline and deterministically: `TestClient` drives the
application in-process, so there is no server to start, no port to pick, no
readiness loop to wait on, and nothing to leave running if a test fails.

## Cleanup

```bash
rm -f bookmarks.json
rm -rf examples/.pytest_cache starter/.pytest_cache
find . -type d -name '__pycache__' -prune -exec rm -rf -- {} +
rm -rf .venv                 # optional: removes the lab virtual environment
git checkout -- starter/     # optional: reset your work
```

The tests themselves leave nothing behind. `bookmarks.json` only ever exists
if you ran the server by hand and created something through it.

## Troubleshooting

See [`troubleshooting.md`](troubleshooting.md) — it covers the missing-module
errors, the starlette/httpx deprecation notice you will genuinely see, how to
read a 422, why `HttpUrl` adds a trailing slash to your assertion, the
`KeyError`-instead-of-404 in the unfinished starter, the empty 500 body, the
`307` from a trailing slash, why `created_at` moves until you inject the
clock, and the `uvicorn` invocation with `--app-dir`.

## Security notes

See [`security.md`](security.md). In short: nothing here opens a socket or
writes a file, and the harness proves both. The substantive content is the
five lessons the lab exists to teach — validation is not authorization,
never trust a client-supplied id, declare what you return or leak it, a
traceback is never a response, and secrets come from the environment while
CORS is a browser mechanism rather than a security feature. It also lists,
by name, the six protections this lab deliberately does **not** have.

## Extension exercises

1. **Add `PUT` beside `PATCH`.** A `PUT` replaces the whole resource, so its
   body model has no optional fields. Decide what `PUT` to a non-existent id
   should do — 404, or create it and return 201 — and write the test that
   pins your decision.
2. **Make the list endpoint paginated.** Add `offset` alongside `limit`,
   return a total count, and decide whether the count goes in the body or in
   a header. Both are defensible; write down why you chose one.
3. **Add a second internal field and try to leak it.** Put `internal_note` on
   `StoredBookmark`, watch the existing tests stay green, then write the test
   that would have caught it. This is the honest way to learn what a test
   suite does not cover.
4. **Swap the storage without touching a handler.** Write a third `Storage`
   implementation — a CSV file, using Day 65's tools — and change only
   `get_storage`. If any handler needs editing, the boundary was not as
   clean as it looked.
5. **Version the API.** Move every route under `/v1/` using an `APIRouter`
   with a prefix, and check the generated schema still lists everything.
6. **Write the same two routes with `http.server`.** No framework: parse the
   path yourself, read the body, validate it by hand, choose the status code,
   and write the JSON. Then count the lines and decide what FastAPI was worth.
7. **Add a dependency that fails.** Write a `require_api_key` dependency that
   raises `HTTPException(401)` when a header is missing, apply it to the
   write routes, and note that your existing tests now need to supply it —
   which is exactly the moment authentication stops being free.

## Navigation

- Previous lab: [Day 081](../day-081-scheduling-and-background-jobs/)
- Next lab: [Day 083](../day-083-packaging-and-distributing-python-code/)
- Subsection index: [Python in Practice](../)
- Section index: [Programming with Python](../../)
