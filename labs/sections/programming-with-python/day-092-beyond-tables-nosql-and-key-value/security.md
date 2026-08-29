# Security notes — Day 092

## What this lab does to your machine

It creates SQLite database files and one `dbm` store, in whatever directory you
point each script at. That is the whole footprint.

- **No network.** Nothing here opens a socket. `tests/run_tests.sh` greps the
  examples and the starter for `socket`, `urllib`, `http` and `requests` and
  fails if any of them appears.
- **No `sudo`, ever.** The same suite greps for a line that would actually
  invoke it, ignoring comments, and fails if one exists.
- **No installation.** No package manager runs. No server is started.
- **Temporary by default.** `tests/run_tests.sh` builds everything under
  `mktemp -d` and removes it in a `trap`, so a completed run leaves your lab
  directory exactly as it found it. The final section of the suite asserts
  that: no `.db` file and no `__pycache__` left behind.

The examples write wherever you tell them to. Give them a scratch directory
rather than your home directory:

```bash
work=$(mktemp -d)
python3 examples/04_docstore.py "$work"
rm -rf "$work"
```

## The data in this lab

The four books and their authors are real, published, checkable works. The
three library members are invented for this lab. No real person's borrowing
history appears anywhere, and nothing here reads a file you did not point it at.

That is a deliberate habit worth keeping. A borrowing record is one of the more
sensitive things a library holds — it is a reading history attached to a named
person — and the fastest way to leak one is to copy production rows into a
teaching example "just to have realistic data".

## The document model changes where the sensitive fields live

This is the security consequence of today's topic, and it is easy to miss.

In the relational shape, a column is a place. `members.email` is one column, in
one table. When somebody asks "where do we hold email addresses?", the schema
answers, and you can grant, revoke, encrypt, redact or drop that one column.

In the document shape, the same address is a key inside a JSON blob, in a
column called `body`, alongside everything else about the member. Three things
follow, and all three are real operational problems:

1. **You cannot grant access to part of a document.** Column-level privileges
   have nothing to bite on. A reader who can see `body` sees every field in it,
   including the ones added last week by somebody who did not think about it.
2. **You cannot enumerate what you hold.** There is no list of fields. Finding
   every place a phone number is stored means scanning every document and
   inferring the shape — which is precisely the audit
   `keys_without_a_title()` performs in the starter, pointed at a different
   field.
3. **A new field appears with no ceremony.** `put()` accepts any shape. Nothing
   reviews it, nothing records it, and the first anyone knows that the store now
   holds a date of birth is when somebody greps for it.

None of this makes the document model wrong. It makes the schema check
somebody's explicit job instead of the database's automatic one, and if nobody
takes that job, nobody does it. That is the same sentence as the schema-on-read
lesson, aimed at your data-protection obligations rather than at a report.

## The field name is interpolated into SQL, and that is why the allow-list exists

`examples/04_docstore.py` and the starter both build SQL text containing the
field name:

```python
f"SELECT body FROM documents WHERE json_extract(body, '$.{field}') = ?"
```

The *value* is bound as a parameter, correctly. The *field* cannot be — a JSON
path passed as a bound parameter defeats the expression index the whole
exercise is about, because the planner can no longer see that the query's
expression matches the index's expression.

So the field name is checked against an allow-list of plain identifiers before
it ever reaches SQL:

```python
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
```

That check is not decoration. `tests/run_tests.sh` calls
`find("shelf'); DROP TABLE documents; --", "A3")` and asserts a `ValueError`.
The rule this generalises to is the one from Week 13, unchanged: **never
interpolate anything into SQL that did not come from an allow-list you wrote.**
A field name from a query string, a form, or a JSON request body is input, and
input never reaches the allow-list side of that line.

This is worth watching for specifically in document-store code, because
"query by any field" is exactly the feature that tempts you to take the field
name from the caller.

## A key-value store's value is opaque, including to your own safeguards

`dbm` never looks inside the bytes you give it. That is its contract and its
speed. It also means:

- **No validation.** Anything you can serialise, it will store. A truncated
  write, a wrongly encoded string, a document with a misspelled field — all
  accepted.
- **Never store a pickle you did not create.** `json` is used throughout this
  lab on purpose. Unpickling untrusted bytes executes code, and a key-value
  store is precisely the kind of place where bytes arrive from somewhere else.
- **Deleting the key is the only deletion.** There is no cascade. The stale
  index at the end of `02_key_value_dbm.py` is the harmless version of this;
  the harmful version is a "delete my account" request that removes the user
  record and leaves their address in three secondary indexes nobody listed.

## Cleanup

```bash
find . -type d -name "__pycache__" -prune -exec rm -rf -- {} +
```

The test suite leaves nothing behind. If you ran the examples against the lab
directory rather than a scratch directory, remove the databases you created by
name — check what is there first, and never with a wildcard:

```bash
ls -1 *.db library_kv* 2>/dev/null
```
