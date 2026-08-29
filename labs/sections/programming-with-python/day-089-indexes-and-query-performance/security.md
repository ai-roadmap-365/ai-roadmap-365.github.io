# Security notes — Day 089

This lab starts no server, opens no port, needs no credential and never
reaches the network. It generates data, measures it, and deletes it. The
security content below is the part that is genuinely about indexes rather
than ceremony.

## What this lab does to your machine

- Creates ordinary files: `events.db` and a few smaller databases, in
  directories you name or in a `mktemp -d` directory.
- Runs `python3` and `sqlite3`, both already installed.
- Writes about **30 MB** for the main table and up to about **35 MB** more
  during the write-cost experiment, all of it removable.
- Needs no `sudo`, no privileged port, no system configuration, no service.
- `tests/run_tests.sh` builds every database inside a `mktemp -d`
  directory removed by a `trap`, and one of its checks asserts that
  nothing was left in the lab directory.

## An index is a copy of your data

This is the security fact of the day, and it is easy to miss because an
index feels like metadata.

`CREATE INDEX ix_email ON members(email)` writes **every email address in
the table into a second structure inside the same file**, sorted. So:

- **Deleting a column's contents is not enough.** If you scrub a sensitive
  column, the values may still be sitting in an index built over it, and
  in freed pages that `VACUUM` has not yet reclaimed. Drop the index too,
  then `VACUUM`.
- **A partial index is a disclosure decision.** `CREATE INDEX ... WHERE
  status = 'flagged'` creates a compact, sorted list of exactly the
  flagged rows. That is useful, and it is also a tidy summary of something
  you may not want summarised.
- **An expression index stores the answer.** An index on
  `lower(email)` stores lowercased addresses; an index on
  `substr(card, -4)` stores the last four digits, in the clear, sorted.
  Whatever the expression computes is now on disk as data.
- **Retention applies to indexes.** If a policy says a field is kept for
  ninety days, the index over it is that field.

None of this is a reason not to index. It is a reason to know that an
index is data.

## Timing is an information channel

A lab about measuring query time is a good place to mention that other
people can measure it too. If an attacker can ask your system questions
and time the answers, the difference between a seek and a scan can leak
what your data contains — a lookup that returns instantly because an index
found nothing, against one that takes ten milliseconds because it had to
check. This is the same family as timing attacks on password comparison.

You are unlikely to meet it in a personal project. Know it exists before
you build something that answers untrusted queries, and remember that the
usual defence is to make the timing independent of the secret rather than
to try to make it fast.

## The parameter habit still applies, and matters more here

Everything Day 85 said about SQL injection is unchanged: pass values as
parameters, never build a statement out of a string.

```python
# WRONG. The value can become part of the statement.
connection.execute(f"SELECT * FROM events WHERE trace_id = '{trace}'")

# RIGHT. The value is compared, never parsed.
connection.execute("SELECT * FROM events WHERE trace_id = ?", (trace,))
```

Two additions specific to today:

- **Parameters are for values, not identifiers.** You cannot write
  `CREATE INDEX ... ON events(?)` or `ORDER BY ?`. If a column name has to
  be chosen at runtime — which happens in reporting tools — validate it
  against an allow-list you wrote. Every script in this lab that builds an
  index name into SQL does so from a literal in the file, never from
  input.
- **Do not let untrusted input decide what gets indexed.** `CREATE INDEX`
  is a schema change, it is not cheap on a large table, and an endpoint
  that lets a stranger trigger one is a denial-of-service tool.

## A slow query is an availability problem

The most common real-world consequence of a missing index is not a
complaint about speed. It is one expensive query holding a connection open
while others queue behind it, and in SQLite, where there is one writer at a
time for the whole database, a long-running statement is felt by everything
else. "Add the index" and "keep the service up" are often the same task.

The other half is the reason to measure before adding one: an index that
nothing queries costs a slower write on every insert forever, and that cost
is invisible in exactly the timings people look at.

## What this lab deliberately does not do

- No server, so no listening socket and no authentication to get wrong.
- No credential of any kind, so nothing to leak.
- No network, asserted mechanically: the suite fails if any executable lab
  file contains a URL.
- No third-party package, asserted the same way — no supply chain beyond
  Python itself.
- No `sudo`, and nothing written outside the lab directory or a temporary
  one.
- No real personal data anywhere. Every row is generated from a seeded
  pseudo-random number generator, and the model names are invented.
