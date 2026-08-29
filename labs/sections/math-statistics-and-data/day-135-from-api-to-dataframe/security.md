# Security notes -- Day 135 lab

This lab ingests JSON from an API and turns it into a DataFrame you trust
enough to build on. The security questions are less about the transport
(Day 78 covered that) and more about what you do with a response body once
it has arrived.

## What this lab does and does not reach

Every socket this lab opens goes to `127.0.0.1` -- the loopback interface,
which never leaves your computer -- on a port the operating system assigns
at run time. `examples/api_server.py` binds `("127.0.0.1", 0)` explicitly.
Had it bound `0.0.0.0`, the server would have been reachable from every
other machine on your network. That one string is the whole difference, and
it is worth remembering the next time a quick-start guide tells you to bind
`0.0.0.0` "so you can test from your phone."

The server has no authentication and no meaningful input validation. It is
a test fixture. Do not deploy it, and do not copy it into anything real.

The one moment this lab needs the internet is the initial
`pip install -r requirements/requirements.txt`.

## Trust the body no more than the sender

`json.loads(response.read())` parses whatever arrived. Nothing guarantees
the shape you expect -- not the status code, not a documented schema, and
certainly not a field that happened to be present on every page you have
seen so far. Exercise 5's schema-drift detector exists precisely because
"every record I have seen has this field" is an observation about your
sample, not a guarantee about the API. `check_contract` (exercise 8) is
this lesson's answer: validate the assembled frame's shape before anything
downstream reads it, and name the exact rule a violation broke rather than
raising a generic error a caller has to re-diagnose.

pydantic (described in the lesson, not run in this lab's authoring
environment) does the same job at the level of individual records, closer
to the wire. Either layer is better than none; the two are not mutually
exclusive, and a pipeline that matters usually wants both.

## Idempotent ingestion is also a safety property

A re-run that duplicates rows is not just wasteful -- it silently corrupts
every aggregate computed from the table afterward, in exactly the way the
grain trap (exercise 1) corrupts a sum. `upsert`'s natural-key merge
(exercise 7) means a retried fetch, a re-run job, or a second cron
execution triggered by an at-least-once scheduler cannot double-count a
customer. Treat "what happens if this runs twice" as a question every
ingestion job must answer before it goes anywhere near a schedule.

## Rate limits and being a good citizen

Day 134 covers rate limits and pagination etiquette in depth; this lab's
mock server has none to respect, but a real API does. The incremental-fetch
pattern in exercise 9 exists partly for this reason: fetching only records
updated since the last watermark is both cheaper for you and lighter on the
service you are calling, compared to re-fetching everything on every run.

## Secrets

Nothing in this lab's code contains a credential, and the mock API needs
none. If you point this pipeline's `urllib.request` calls at a real,
authenticated API, the Day 78 rules apply unchanged: read tokens from the
environment, never from a source file; use headers, never a query string;
and never log an `Authorization` header while debugging a response.

## Denial of service, in both directions

**Against you.** `fetch_raw_pages` reads one page response fully into
memory before writing it to JSONL. For an API returning small, page-sized
bodies (as this one does) that is fine; a page unbounded in size is a
memory hazard the same way an unbounded response body was in Day 78, and
the same streaming defence applies.

**Against them.** A retry loop with no backoff and no attempt cap, run
against a real service, is a small denial-of-service tool aimed at whoever
you are calling. This lab's fetch functions do not retry on failure at
all -- that is Day 78's territory -- but if you add retries to an
ingestion pipeline built from this lab, bring Day 78's backoff-and-jitter
policy with you.
