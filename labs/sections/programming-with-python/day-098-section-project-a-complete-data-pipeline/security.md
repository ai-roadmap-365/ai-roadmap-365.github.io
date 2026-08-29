# Security notes

## What this lab touches

- **The network:** once, to `pip install` three pinned packages. After that,
  nothing in this lab opens a socket to anything except 127.0.0.1. Section 10
  of `tests/run_tests.sh` scans every `.py`, `.sh`, `.ini` and `.toml` file in
  the lab and fails if any URL points anywhere else.
- **The filesystem:** the demo works inside a temporary directory it creates and
  removes; the test harness works inside `mktemp -d` and removes it; the CLI
  writes `pipeline.db` into whatever directory you run it from. The harness
  asserts that no `.db` file and no `__pycache__` is left inside the lab.
- **Privileges:** none. No `sudo` anywhere, and the harness proves it.

## The secret, and why it is not decorative

The fixture server requires `Authorization: Bearer demo-token-value`, and the
pipeline reads that token from `PIPELINE_API_TOKEN`. That arrangement exists so
the leak test proves something. If the lab simply never sent a token, redaction
would be trivially "working" for the wrong reason.

Three properties are enforced and tested:

1. **The token never appears in the provenance table.** `--explain-config`
   prints `api_token  ***redacted***  environment` — the *source* of a secret is
   operationally important and its *value* never is.
2. **The token never appears in the log.** Not because nobody wrote code to log
   it — because `logs.redact` scans every string in every record, at any depth,
   before the line is written.
3. **The leak it catches is a real one.** charlie's 500 response body says
   `upstream credentials rejected for token demo-token-value`. Nobody logged the
   token; an upstream service put it in an error message and the error message
   went to the log. Real services do this. Redaction that depends on every
   developer remembering is not redaction.

The general rule, from Day 97 and from the Twelve-Factor App: **secrets come
from the environment, never from a file in version control**, and the sanitizing
step lives in one place that cannot be forgotten rather than at every call site
that might one day print something.

## SQL injection

Every value that reaches the database goes through SQLAlchemy — either through
the ORM's `insert()` construct or through a `select()` with bound comparisons.
Nothing in this lab builds SQL by string concatenation, and none of the values
in question came from a trusted place: they are records fetched over HTTP from
a source the pipeline does not control.

What SQLAlchemy does **not** protect: `text()` with an f-string in it, and
identifiers. A user-chosen sort column or table name cannot be bound as a
parameter and must be validated against an allow-list you control.

## The data-quality gate is a security boundary

It is easy to file "humidity of 155 per cent" under data quality and stop
thinking. Treat the gate as a boundary instead, because it is the last thing
between an untrusted source and your storage:

- `extra="forbid"` means a source that starts sending new fields is a visible
  event rather than a silent one. That is the same reasoning as rejecting
  unexpected parameters at an API boundary.
- Length limits on `station_id` and `reading_id` bound what one malicious or
  broken source can write into your table.
- A record that is *valid but wrong* — bravo's 41.3 Celsius five minutes after
  15.0 — is stored and **flagged**, never silently dropped. Silently dropping
  anomalous data is how a compromised sensor becomes invisible.

## Retry as an amplification risk

Retrying is not free and it is not always kind. Three attempts against a
struggling service is three times the load at exactly the moment it can least
afford it, and a fleet of clients all retrying in lockstep is a thundering herd.
This lab retries at most three times with exponential backoff (`0.05`, `0.10`
seconds by default) and never retries a 4xx other than 429. In production, add
jitter to the backoff and honour `Retry-After` when the server sends it.

## The run id and the audit trail

Every stored row carries `ingested_by_run`, and every run gets a row in `runs`.
That is not bookkeeping for its own sake: it is what makes
`DELETE FROM readings WHERE ingested_by_run = 'run-abc123'` a complete and safe
undo of one bad backfill. A pipeline that cannot say which run wrote a row
cannot undo anything without guessing.

## Invented data

Every station name, reading and token in this lab is invented. `demo-token-value`
is not a credential for anything and never was; it exists so a redaction test
has something real to redact.

## What is not covered here

Transport security (this is plain HTTP to a loopback fixture server, so there is
nothing to encrypt and no certificate to verify — a real pipeline uses HTTPS and
verifies certificates), authentication beyond a bearer token, secret rotation,
key management services, and at-rest encryption of the SQLite file. None of them
is exercised, so none of them is claimed.
