# Troubleshooting — Day 027 lab

## The test server returns 503 or 504, or times out, instead of the status I asked for

**This is expected, and it is the whole point of the lesson.** `httpbin.org` is
a free, shared service; when it is under load its gateway returns `502`/`503`/
`504` or simply times out, even for an endpoint like `/status/429`. A resilient
client must **survive exactly this** — and yours does: the backoff loop treats a
`503` the same as a `429` (both retryable) and keeps its cap, and the `decide`
step rides through transient gateway `5xx`/timeouts to read the endpoint's real,
deliberate status. If a run shows `503` where you expected `429`, that is a real
teaching moment, not a bug. Re-run in a minute for a cleaner picture, or note
the `503` — the client handled it correctly either way.

## `command not found: python3`

The pagination step uses `python3` only to count items in a JSON array. Install
it (macOS: `brew install python`; Debian/Ubuntu: `sudo apt install python3`), or
adapt the counter. See `requirements/README.md`.

## A run seems to hang

It should not — every request uses `--max-time`, and every retry loop has a hard
cap (`MAX_ATTEMPTS`). If your edited starter removed the `--max-time` flag or the
cap, put them back: a timeout turns a hung request into a handled failure, and a
cap turns a retry loop into one that always terminates. The tests wrap each run
in a watchdog that kills and **fails** any run that does not finish in time,
precisely to catch an accidental infinite loop.

## `curl: (6) Could not resolve host` / `(7) Failed to connect`

You are offline or behind a restrictive network. That is a network failure, not
a bug. The script detects it, runs the offline backoff self-test, and exits 0.
Reconnect and re-run for the live demos.

## The tests print `skip:` lines

Skips are not failures. Offline, the live network checks are skipped by design.
If `jsonplaceholder.typicode.com` is transiently down, the pagination-count
check skips rather than failing — an external outage is not your bug. The suite
still exits 0 as long as no structural or termination check failed.

## The backoff waited far longer than I expected

Two causes. First, if the server sends a `Retry-After` header, the client obeys
it exactly (that can be seconds or more) instead of using its own delay — this
is correct behavior. Second, the default base delay doubles each attempt up to
the cap (1, 2, 4, 8, 8 s), so five attempts can wait ~23 s before giving up. Set
`BASE_DELAY` and `DELAY_CAP` lower to move faster while experimenting:
`BASE_DELAY=0 DELAY_CAP=0 bash examples/resilient_client.sh`.
