# Security notes — Day 088

## What this lab does to your machine

Almost nothing, on purpose.

- Every database it creates lives in a `mktemp -d` directory that is removed by
  a `trap` on exit. The final check in the harness confirms the lab directory
  itself was never written to.
- No network access at any point. `requires_network: false` is literal: there is
  nothing to fetch, and section 9 of the harness greps every file a learner runs
  for `http`, `urllib`, `socket` and `requests.` and requires zero matches.
- No `sudo`, no system configuration, no daemons, no scheduler entries.
- No third-party packages, so no supply chain beyond your operating system's
  own `sqlite3` and `python3`.

If you follow the README by hand you will create `library.db` in the lab
directory. The Cleanup section removes it.

## The genuinely dangerous thing here is the SQL

This lab teaches destructive statements, and it teaches them by running them.
The safety comes from *where* they run, not from making them harmless:

- Every destructive demonstration runs against a **copy**. The pattern
  `cp library.db scratch.db` appears before every one of them.
- The most damaging statement in the lab — `UPDATE loans SET returned = 1;`
  with no WHERE clause — is executed for real, against a throwaway file, and
  the harness asserts it changed 12 rows. Reading about it does not teach it.

**Do not practise on a database you care about.** The routine the lesson
teaches exists precisely because the failure is silent:

1. Take a copy of the file first.
2. Write the statement as a `SELECT` with the exact `WHERE` clause you intend.
3. Run it and read the row count.
4. Convert it to `UPDATE` or `DELETE`, keeping the `WHERE` clause byte for byte.
5. Wrap it in `BEGIN`, check `changes()`, and `ROLLBACK` if the number is wrong.

## SQL injection is not in scope today, and here is why that matters

Every statement in this lab is written by you, in a file, with literal values.
None of it takes input from a user, so none of it is injectable.

That will stop being true the moment you put a schema behind a web form, and
the lesson names the rule now so it is not a surprise later: **build statements
with bound parameters, never with string formatting.** In Python that is

```python
cur.execute("UPDATE loans SET returned = 1 WHERE id = ?", (loan_id,))
```

and never

```python
cur.execute(f"UPDATE loans SET returned = 1 WHERE id = {loan_id}")
```

The second form is the one where a `loan_id` of `1 OR 1=1` becomes today's
WHERE-less UPDATE, executed by a stranger. Constraints limit the damage — a
CHECK still refuses an impossible value — but they do not stop it.

The one place `examples/migrate.py` formats a value into SQL is
`PRAGMA user_version = {int(version)}`, because PRAGMA does not accept bound
parameters. The value is an `int()` of a regex match against a filename, and
the comment in the source says so. That is the standard you should hold your
own exceptions to: unavoidable, narrowed to a type, and explained where it
happens.

## Constraints are a security control, not only a correctness one

A `CHECK` constraint is the last thing standing between a bug in your
application and a permanently wrong row. Application validation runs in one
program; a schema constraint runs for every program, every script, every
console session and every intern, forever. When the two disagree, the schema is
the one that was still enforced at 3am.

For training data specifically — the `examples_strict` table in
`examples/05-constraints.sql` — the constraints prevent a duplicated example, a
missing label, an invented class and a leaked split value. Each of those is a
data-integrity problem that shows up much later as a model problem, and by then
the schema is not where anybody is looking.

## What this lab deliberately does not cover

- **Encryption at rest.** SQLite files are plain files. Anything sensitive needs
  filesystem or full-disk encryption, or an encrypting build of SQLite.
- **Access control.** SQLite has no users, roles or grants. Permission to read
  the file is permission to read everything in it.
- **Backups.** The lab copies a file and calls that a backup, which is fine for
  a lab. A real backup is tested by restoring it.
- **Concurrency.** Locking, WAL mode and busy timeouts are a later day. The
  byte-for-byte rollback proof here is made in rollback-journal mode, and
  `expected-output/FIELDS.md` says so rather than implying it generalises.
