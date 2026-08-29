# What must match, and what may legitimately differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16 (macOS 26.5.2, Apple Silicon, `sqlite3` shell 3.51.0 at
`/usr/bin/sqlite3`, Python 3.14.0 with its bundled SQLite 3.53.3, bash 3.2.57).

## Must match exactly

These are facts about SQL and about this schema, not about this machine.

| Value | Where | Why it is fixed |
| --- | --- | --- |
| `12` rows changed by the WHERE-less UPDATE | `expensive-mistake.txt` | The seed has exactly 12 loans |
| `8` outstanding, `4` returned before | `expensive-mistake.txt` | Fixed seed data |
| `1` row matched by the SELECT-first check | `expensive-mistake.txt` | Loan 2 is one row |
| Every `CHECK constraint failed: ...` message | `constraints.txt` | SQLite echoes the constraint expression verbatim |
| `UNIQUE constraint failed: examples_strict.text` | `constraints.txt` | Names the table and column |
| `NOT NULL constraint failed: examples_strict.label` | `constraints.txt` | Names the table and column |
| `cannot store TEXT value in INTEGER column` | `constraints.txt` | STRICT table behaviour |
| `4` rows surviving after 7 rejections | `constraints.txt` | Every bad row was refused |
| `FOREIGN KEY constraint failed` | `cascade-and-restrict.txt` | The RESTRICT rule firing |
| `members_deleted=1 loans_left=9` | `test-run.txt` | CASCADE removed member 3's three loans |
| `0` for `PRAGMA foreign_keys` on a new connection | `test-run.txt` | Enforcement is off by default |
| `13` loans after the rebuild | `table-rebuild.txt` | 12 copied plus 1 inserted afterwards |
| `2` foreign keys on the rebuilt table | `table-rebuild.txt` | Both were retyped in step 1 |
| `4 migration(s) applied`, then `0` | `migrations.txt` | The whole idempotence claim |
| `rolled back; database is still at version 4` | `migrations.txt` | The whole atomicity claim |
| `101 checks, 0 failure(s).` | `test-run.txt` | The harness result |

## May differ on your machine

| Value | Why |
| --- | --- |
| `sqlite3 shell library: 3.51.0` | Whatever your `sqlite3` is. The four documented `ALTER TABLE` operations work on any version this lab supports |
| `python3 sqlite3 library: 3.53.3` | Python bundles its own SQLite, and it is often a *different* version from the shell's — see below |
| `ALTER COLUMN expected: no` | `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` arrived in SQLite 3.53.0. The harness asserts that your build agrees with its own version number, so this check passes either way |
| The SHA-256 checksum in section 2 | The value is not asserted; only that it is *identical before and after the rollback*. Different SQLite versions may lay out pages differently |
| `<workdir>` paths | Every run uses a fresh `mktemp -d`. The captures are sanitised |
| `journal_mode: delete` | The byte-for-byte claim is made in rollback-journal mode. In WAL mode the main database file plus its `-wal` sidecar together hold the state, so comparing only the `.db` file is not the right test — the harness prints the mode it observed |

## The two SQLite versions on one machine

Section 0 of `test-run.txt` prints two different version numbers, and that is
not a mistake. The `sqlite3` shell and Python's `sqlite3` module each link
their own copy of the library. On the authoring machine the shell is 3.51.0 and
Python's is 3.53.3, which is a two-release gap — and 3.53.0 is exactly where
`ALTER TABLE ... ALTER COLUMN` was added. So the same statement is a syntax
error in one and valid in the other, on one computer, on the same afternoon.

This is why the lesson insists on the create-copy-drop-rename rebuild for
anything beyond the four documented operations: it is the procedure that works
on every version, and it is the only one you can write down once.
