# Day 023 lab — CRUD Against a REST API

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** REST Fundamentals: Resources and Verbs
- **Day number:** 23 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-023-rest-fundamentals-resources-and-verbs
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-023-rest-fundamentals-resources-and-verbs` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 23's lesson built the resource-and-verb model of REST. This lab puts it in
your hands: you run a full **create-read-update-delete** cycle against a real
public REST API, using nothing but the HTTP verbs and two resource addresses.
You read a representation of an item, list a collection, create a new item and
watch the server assign its id, replace an item, and delete one — reading the
real status code the server returns for each verb.

## Learning objectives

- Read a resource's JSON representation with `GET` on an item and a collection.
- Create a resource by `POST`ing to the collection and confirm a `201 Created`.
- Replace a resource with `PUT` and read the `200 OK` response.
- Delete a resource with `DELETE` and read its status code.
- Explain why `POST` targets the collection while `GET`/`PUT`/`DELETE` target
  an item, and why a practice API's faked writes do not persist.

## Prerequisites

- The Day 23 lesson, Day 18 (HTTP methods), and Day 22 (what an API is).
- A terminal with `curl` and network access. `python3` is optional (it only
  pretty-prints the JSON; the lab works without it).

## Supported operating systems

- **macOS** and **Linux** — fully supported (`curl` preinstalled).
- **Windows** — `curl` ships with Windows 10+; or run under WSL.

## Hardware requirements

Any computer with an internet connection. The lab only makes ordinary web
requests.

## Required software

`curl` only — preinstalled everywhere. `python3` is optional. See
`requirements/README.md`.

## Free and open-source options

Everything here is free: `curl` is open source, and the test service
(`jsonplaceholder.typicode.com`) is a free public REST API that needs no
account or key.

## Installation

None. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-023-rest-fundamentals-resources-and-verbs
```

## File structure

```text
day-023-.../
├── README.md
├── metadata.yml
├── starter/
│   ├── rest_crud.sh          ← YOUR working file (4 exercises)
│   └── rest-worksheet.md     ← record your status codes and the new id
├── examples/
│   └── rest_crud.sh          ← completed reference implementation
├── tests/
│   └── run_tests.sh
├── expected-output/
│   └── sample-run.txt        ← real captured run
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished CRUD cycle first (needs network)
bash examples/rest_crud.sh

# 2. Complete the four exercises in the starter, then run it
bash starter/rest_crud.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/rest_crud.sh` — runs the five REST exchanges against
  `jsonplaceholder.typicode.com`: `GET /posts/1` (read an item), `GET /posts`
  (list the collection), `POST /posts` (create — returns `201` and a new id),
  `PUT /posts/1` (replace — returns `200`), and `DELETE /posts/1` (remove —
  returns `200`). It pretty-prints JSON with `python3 -m json.tool` when
  available and degrades gracefully offline.
- `bash starter/rest_crud.sh` — the same skeleton with four numbered
  exercises; each names the exact `curl` command to use for GET, POST, PUT,
  and DELETE.
- `bash tests/run_tests.sh` — always verifies structure (files present, both
  scripts parse, the example exercises each verb, the starter names four
  exercises), then — when online — checks the real behaviour: `GET /posts/1`
  returns `200` with the expected keys and `POST /posts` returns `201`.
  Offline, the live checks are skipped (never failed). Exits 0 on success.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for a
real captured run. The `GET` bodies are fixed by the service; the created id
is always `101` on JSONPlaceholder.

## Validation steps

1. `bash examples/rest_crud.sh` prints all five sections without errors.
2. The `POST` section shows `HTTP 201` and a body containing `"id": 101`.
3. The `PUT` and `DELETE` sections show `HTTP 200`.
4. The tests pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `15 checks, 0 failure(s), 0 skip(s).` online (the three
live checks skip, never fail, when offline). Exit 0 on success.

## Cleanup

Nothing to clean up — the scripts only make web requests and write no files
(and JSONPlaceholder fakes its writes, so nothing persists server-side).
Reset your edited starter with `git checkout -- starter/rest_crud.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — faked writes not persisting,
missing `python3`, status codes stuck to the body, and offline behaviour.

## Security notes

See [security.md](security.md). Only a public test API; never send real
secrets to a practice service; keep tokens in headers, never in URLs.

## Extension exercises

1. Send a `PATCH /posts/1` with only `{"title":"just the title"}` and compare
   the returned representation to what a full `PUT` returned.
2. Fetch a nested collection — `GET /posts/1/comments` and `GET /users/1/todos`
   — and note how the URL reads as a path through related resources.
3. Run the same `DELETE /posts/1` twice and confirm the outcome is identical
   (idempotency), then explain why `POST /posts` twice would differ.

## Navigation

- **Previous day:** Day 22 — What an API Is and Why Everything Has One.
- **Next day:** Day 24 — JSON and Data Serialization.
