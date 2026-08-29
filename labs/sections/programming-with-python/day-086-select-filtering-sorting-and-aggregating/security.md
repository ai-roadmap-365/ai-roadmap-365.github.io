# Security notes

This lab reads a local file with a local tool and never opens a socket. The
security surface is small, and it is worth being precise about where the real
risk in querying lives, because it is not where beginners expect.

## What this lab does and does not touch

- **No network.** Nothing here resolves a hostname or opens a connection. The
  test suite has a check that fails if any file under `examples/`, `starter/` or
  `tests/` so much as contains a URL.
- **No credentials.** SQLite has no users, no passwords and no `GRANT`. Access
  to the data is exactly filesystem access to the file. That simplicity is a
  feature here and a limitation in production, and the lesson says so.
- **No `sudo`.** The only privileged command anywhere in this lab is the
  optional `apt`/`dnf` install of the `sqlite3` shell, in the troubleshooting
  notes, for machines that do not have it. Nothing in the lab runs it for you.
- **No daemon, no port, no background process.** SQLite is a library and a file.
  When the shell exits, nothing is left running.
- **Nothing outside the lab directory.** The seed writes `examples/library.db`;
  the test harness writes only inside a `mktemp -d` directory it removes in a
  `trap`. Both are deletable with `rm`.

## The real risk in this topic: string-built SQL

Every query in this lab is a fixed file. The moment you build a query by pasting
a value into it — which is the very next thing anyone does — you have created
the most common serious vulnerability in application software.

```python
# NEVER do this. The value is CODE, not data.
cur.execute("SELECT * FROM books WHERE author = '" + name + "'")
```

If `name` is `x' OR '1'='1`, that query returns the whole table. If it contains
a statement separator and your driver executes more than one statement, it can
do considerably worse. The fix is not to escape quotes yourself — people have
been getting that wrong for thirty years. The fix is to never build the string:

```python
# Parameterised. The value can never be parsed as SQL.
cur.execute("SELECT * FROM books WHERE author = ?", (name,))
```

Python's `sqlite3` module takes `?` placeholders, and a tuple of values. The
driver sends the query text and the values along separate paths, so no value can
change the shape of the statement no matter what characters it contains.

`examples/groupby_from_scratch.py` uses a fixed query string with no
interpolation at all, which is the other correct answer: when there is no
user input, there is nothing to inject.

**The thing that is not a defence:** a `WHERE` clause is not an access control.
It filters what a query returns; it does not stop the same connection from
running a different query without it. If a piece of code must not see certain
rows, that has to be enforced by what the code is allowed to connect to, not by
the text of the queries you hope it will write.

## A privacy point that belongs to today specifically

This lesson is about aggregation, and aggregation is routinely offered as a
privacy measure: "we only publish counts, never individual records." Treat that
claim carefully. A `GROUP BY` whose buckets are small does not anonymise
anything — a count of 1 in a bucket identifies exactly one person, and two
published aggregates that differ by one row tell you what that row contained.
The habit worth forming now, while the stakes are a fictional library, is to
look at the smallest bucket in any grouped result before publishing it.

The seed data here is invented. The member names are fictional and every email
address uses the `.invalid` top-level domain, which
[RFC 2606](https://www.rfc-editor.org/rfc/rfc2606) reserves permanently so that
it can never be registered and never routes anywhere.

## Deleting everything

```bash
rm -f examples/library.db
```

That is the entire cleanup. There is no service to stop, no package to remove,
no configuration to revert, and nothing was written outside this directory.
