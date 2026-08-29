# Day 022 lab — Call Your First APIs

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** What an API Is and Why Everything Has One
- **Day number:** 22 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-022-what-an-api-is-and-why
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-022-what-an-api-is-and-why` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 22's lesson explained what an API is: a contract two programs agree on so
one can ask the other to do work. This lab makes it real. You call three free,
public, no-key web APIs from the terminal, read their JSON responses, and see
for yourself that an API call is just an HTTP request to an endpoint that comes
back as structured data — the same move that later reaches a hosted model.

## Learning objectives

- Call a web API with `curl` and read its JSON response.
- Fetch two different resources (`/todos/1`, `/users/1`) from one API and see
  how the endpoint selects what comes back.
- Send a query parameter and watch httpbin echo it back in an `args` object.
- Read **live** data (the space station's current position) and tell it apart
  from fixed sample data.
- Pretty-print JSON with `python3 -m json.tool` (no `jq` required).

## Prerequisites

- The Day 22 lesson, and days 15–21 (the networking category).
- Day 21 comfort with `curl`.
- A terminal with `curl` and `python3`, and an internet connection.

## Supported operating systems

- **macOS** and **Linux** — fully supported (`curl` and `python3` preinstalled).
- **Windows** — `curl` ships with Windows 10+ and `python3` is a free install;
  or run everything unmodified inside WSL.

## Hardware requirements

Any computer with an internet connection. The lab only makes ordinary web
requests and reads the responses.

## Required software

- `curl` — to send the requests (preinstalled on macOS/Linux).
- `python3` — only to pretty-print JSON via `python3 -m json.tool`
  (preinstalled on macOS/Linux). `jq` is **optional**, never required.

See `requirements/README.md`.

## Free and open-source options

Everything here is free: `curl` and Python are open source, and all three test
APIs — JSONPlaceholder, httpbin, and Open Notify — are free public endpoints
with no account and no key.

## Installation

None. Change into this directory:

```bash
cd labs/sections/computing-foundations/day-022-what-an-api-is-and-why
```

## File structure

```text
day-022-what-an-api-is-and-why/
├── README.md
├── metadata.yml
├── starter/
│   ├── call_apis.sh          ← YOUR working file (4 exercises)
│   └── api-worksheet.md      ← record the values you got back
├── examples/
│   └── call_apis.sh          ← completed reference implementation
├── tests/
│   └── run_tests.sh
├── expected-output/
│   └── sample-run.txt        ← a real captured run
├── requirements/README.md
├── troubleshooting.md
└── security.md
```

## How to run

```bash
# 1. See the finished tool first (needs network)
bash examples/call_apis.sh

# 2. Complete the four exercises in the starter, then run it
bash starter/call_apis.sh

# 3. Check your work
bash tests/run_tests.sh
```

## What the commands do

- `bash examples/call_apis.sh` — makes four API calls and explains each:
  JSONPlaceholder `/todos/1` and `/users/1`, httpbin `/get` with a query
  parameter, and Open Notify's live `iss-now.json`. It pretty-prints each JSON
  response with `python3 -m json.tool`, and if a service returns something that
  is not JSON it prints the raw body instead of crashing. It degrades
  gracefully offline (clear message, exit 0).
- `bash starter/call_apis.sh` — the same skeleton with four numbered exercises;
  each names the exact `curl` command to run and what to record.
- `bash tests/run_tests.sh` — always verifies structure (files present, both
  scripts parse, the example calls all three APIs and does not require `jq`,
  the starter names four exercises, `python3` is available), then — when
  online — checks that each API returns parseable JSON with its documented key
  (`title`, `email`, `args`, `iss_position`). Offline or during a transient
  outage, the affected live checks are **skipped** (never failed). Exits 0 when
  no structure check fails.

## Expected output

See [`expected-output/sample-run.txt`](expected-output/sample-run.txt) for a
real captured run. The JSONPlaceholder data is fixed sample data, but the ISS
latitude/longitude and timestamp are live, so yours will differ.

## Validation steps

1. `bash examples/call_apis.sh` prints all four sections without errors.
2. You can point at each response and identify it as JSON with named fields.
3. You found your `course` and `day` parameters echoed by httpbin's `args`.
4. You ran the ISS call twice and saw the coordinates change.
5. The tests pass.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line online: `17 checks, 0 failure(s), 0 skip(s).` (a
transiently down service turns its check into a skip, never a failure; offline,
all four live checks skip). Exit 0 on success.

## Cleanup

Nothing to clean up — the scripts only make web requests and write no files.
Reset your edited starter with `git checkout -- starter/call_apis.sh`.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) — no network, unindented JSON,
httpbin 503s, the ISS `http`-vs-`https` gotcha, and shell-quoting URLs with `&`.

## Security notes

See [security.md](security.md). Short version: only public, no-auth endpoints;
never send secrets to an echo service; an API key is a password.

## Extension exercises

1. Filter with a parameter: `curl -s "https://jsonplaceholder.typicode.com/todos?userId=1" | python3 -m json.tool`
   returns only user 1's to-dos. Count how many came back.
2. Add response headers with `curl -i https://jsonplaceholder.typicode.com/todos/1`
   and find the `Content-Type: application/json` header.
3. Time a call with `curl -o /dev/null -s -w 'status:%{http_code} total:%{time_total}s\n' https://jsonplaceholder.typicode.com/todos/1`
   and compare it with how long a local calculation takes.

## Navigation

- **Previous day:** Day 21 — Inspecting Traffic with curl and Developer Tools.
- **Next day:** Day 23 — REST Fundamentals: Resources and Verbs.
