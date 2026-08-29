# Security notes — Day 094

Validation is a security control. It is easy to file it under tidiness, because
most of the time it catches typos — but the boundary where you decide what
counts as a valid record is the same boundary an attacker has to cross, and a
schema is one of the few controls that is cheap enough to apply everywhere.

## What this lab does and does not touch

| Concern | This lab |
| --- | --- |
| Network at run time | None. The only network step is the one-off `pip install` of two pinned packages. Section 7 of `tests/run_tests.sh` greps the lab's Python sources to confirm nothing opens a socket. |
| Credentials, tokens, API keys | None. `requires_api_key: false`. There is nothing to leak because there is nothing here. |
| Files written | `out/accepted.jsonl` and `out/rejects.json` inside the lab directory, plus temporary directories the tests create and delete themselves. Nothing system-wide, no `sudo`. |
| Code execution from data | None. The batch is read with `json.load`. Nothing is `eval`'d, `pickle`'d or imported from data. |
| Personal data | All invented. See below. |

## The data is invented, and that is a deliberate choice

Every station code, site name, operator initial and measurement in
`data/raw-readings.json` and in the test fixtures is made up for this lab.
There is no real monitoring network, no real person, and no real measurement
anywhere in this directory. The operator initials in particular — `R. Nayar`,
`T. Oyelaran`, `M. Ferreira`, `A. Invented` — are invented specifically so that
nothing here resembles a record about a living individual.

If you adapt this lab to a real feed, that stops being true immediately, and
the next three sections start to matter.

## Rejected records are still data, and often the most sensitive kind

The single most common way a validation gate leaks is through its own error
report. `ValidationError` entries carry an `input` field, which is **the value
that failed** — and by design, because a report you cannot act on is useless.
That is fine when the bad value is `118`. It is not fine when the bad value is
a password that arrived in the wrong field, a full payment card number that
failed a length check, or a personal identifier that failed a pattern.

Three rules follow, and they are worth adopting before you need them:

1. **Decide where the report goes before you decide what it contains.** A
   rejects file sitting in an object store with wide read access is a different
   risk from one on the operator's terminal.
2. **Redact `input` for fields you have classified as sensitive.** The `_tidy`
   function in `examples/gate.py` is the single place that would change; it
   already exists as a chokepoint for exactly this reason. Keeping `loc` and
   `type` and dropping `input` still tells the source owner which field and
   which rule, which is usually enough.
3. **Never log the whole raw record on failure.** `_tidy` keeps four keys per
   error rather than dumping the record, and the report names the record by
   index and id rather than reproducing it. Note that in this lab a `missing`
   error's `input` *is* the whole record — that is pydantic's behaviour for a
   missing key, and it is exactly the case you would want to redact on a real
   feed.

## `extra="forbid"` is a security setting, not a style preference

The default in pydantic is `extra="ignore"`: an unexpected key is silently
dropped. That is convenient and it hides two different problems.

The mild one is the typo. `humidty_pct` in record 5 of this batch would be
discarded in silence, `humidity_pct` would be absent, and depending on your
model you would either get a confusing "missing" error or a plausible-looking
record with a default in it.

The serious one is **mass assignment**. If a model is ever constructed from
user-supplied data and the model has a field the user should not control —
`is_admin`, `owner_id`, `price` — then whether an unexpected key is ignored or
forbidden decides whether that is a vulnerability. `extra="forbid"` turns a
silent success into a loud refusal. Set it deliberately.

Related: use separate input and output models when a stored record carries
anything the caller must not see. Day 082 made that argument about a
`response_model`; it is the same argument.

## Validation is one layer of three, and it cannot be the only one

- **The type checker (Day 075)** runs before the program does. It catches code
  that could never work — a `str` passed where an `int` was declared. It cannot
  see a single byte of runtime data.
- **The validator (today)** runs as data arrives. It catches data that is wrong
  *now*. It cannot see what happens after the object leaves its hands.
- **The database constraint (Day 088)** runs as data is stored. It catches
  anything that reached the table by any route — a migration, a manual `UPDATE`,
  a second service, a bug that bypassed your gate entirely.

A `NOT NULL` in the schema and a required field in the model are not redundant.
The model protects the path through your application; the constraint protects
the table from every path, including the ones you did not write. Anyone who
tells you to drop one because the other exists is proposing that a future
mistake go uncaught.

None of the three is an authorization check. A record can be perfectly valid and
still be one the caller has no business submitting.

## Denial of service through validation

Two failure modes are worth knowing about before you meet them:

- **Unbounded input.** A model with an unconstrained `str` or `list` will
  happily try to validate a 500 MB field. Set `max_length` on strings and use
  bounded collection types on anything crossing a real boundary.
- **Regex patterns.** `StringConstraints(pattern=...)` compiles a regular
  expression, and a carelessly written one can be made to backtrack
  catastrophically on hostile input. The two patterns in this lab —
  `^ST-[A-Z]{3}$` and `^RD-\d{4}$` — are anchored, fixed-length and have no
  nested quantifiers, which is what makes them safe. Prefer patterns with that
  shape.

## Supply chain

`requirements/requirements.txt` pins exact versions rather than ranges, so the
lab installs the same two packages it was written against. pydantic's validation
core is a compiled Rust extension shipped as a wheel; install it from PyPI over
HTTPS with a pinned version, and in a real project add a hash-checked lockfile.
Nothing in this lab installs anything system-wide, and `rm -rf .venv` removes
every trace of it.
