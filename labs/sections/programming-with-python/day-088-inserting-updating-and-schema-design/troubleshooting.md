# Troubleshooting — Day 088

## "no such table: loans"

You have not built the database, or you are in the wrong directory. From the
lab directory:

```bash
sqlite3 library.db < examples/seed.sql
sqlite3 library.db "SELECT count(*) FROM loans;"   # 12
```

## My UPDATE changed far more rows than I expected

That is today's whole subject, and you have just met it for real. If you had
not yet committed, `ROLLBACK` now. If you had, restore your copy:

```bash
cp library-backup.db library.db
```

If you have neither, the rows are gone. This is why step one of the routine is
`cp library.db library-backup.db`, and why step two is writing the SELECT
first. Both take five seconds and neither feels necessary until the one time it
does.

## My DELETE or UPDATE reports "0 rows changed" and I expected some

Almost always the WHERE clause matches nothing. Check the values you are
comparing against, and watch for these three:

- **Type.** In an ordinary (non-STRICT) table, `WHERE copies = '3'` and
  `WHERE copies = 3` can behave differently, because the column may be holding
  text. Check with `SELECT DISTINCT typeof(copies) FROM books;`.
- **Case.** `WHERE split = 'test'` does not match `'Testing'` or `'Test'`.
- **Whitespace.** `'test '` is not `'test'`. Try
  `WHERE trim(lower(split)) = 'test'` to confirm that is the cause.

## A foreign key that should have stopped me did nothing

`PRAGMA foreign_keys` is **off by default**, it is per connection, and it
cannot be stored in the database file. Every connection must set it:

```bash
sqlite3 library.db "PRAGMA foreign_keys = ON; DELETE FROM books WHERE id = 8;"
```

To find damage already done with enforcement off:

```bash
sqlite3 library.db "SELECT * FROM pragma_foreign_key_check;"
```

## "FOREIGN KEY constraint failed" and I cannot tell which one

SQLite's message does not name the constraint. Ask the schema which foreign
keys the table has, then check each one:

```bash
sqlite3 library.db "SELECT * FROM pragma_foreign_key_list('loans');"
sqlite3 library.db "SELECT count(*) FROM loans WHERE book_id = 8;"
```

A non-zero count on a `RESTRICT` reference is your answer.

## "Error: near ..." on ALTER TABLE

You have hit the version boundary. The four operations that work everywhere are
rename table, rename column, add column and drop column. Anything else —
adding a CHECK, adding a UNIQUE, adding a foreign key — needs the
create-copy-drop-rename rebuild in `examples/07-table-rebuild.sql`.

`ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` is a special case: it arrived in
SQLite 3.53.0, so it works on some builds and not others. Check before relying
on it, and remember that your shell and your Python may not agree:

```bash
sqlite3 :memory: 'SELECT sqlite_version();'
python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'
```

## My transaction failed but the earlier changes were kept anyway

This is the most surprising behaviour in the lesson, and it is correct. A
constraint violation undoes only the **failing statement**. The transaction
stays open. If the next thing you send is `COMMIT`, you commit whatever had
already succeeded.

```bash
# Keeps the +10, because COMMIT ran after the error:
sqlite3 library.db "BEGIN; UPDATE books SET copies=copies+10 WHERE id=1;
                    UPDATE books SET copies=-1 WHERE id=5; COMMIT;"

# Stops at the first error, so COMMIT is never reached:
sqlite3 -bail library.db < your-script.sql
```

Use `-bail` for anything that changes a schema, and check the exit code.

## "cannot store TEXT value in INTEGER column"

A STRICT table is refusing a value it cannot convert without losing
information. This is the constraint doing its job. Note that STRICT does
convert *losslessly*: `'7'` into an INTEGER column becomes `7`, and `4.0`
becomes `4`, but `'banana'` and `3.5` are refused.

## "cannot UPDATE generated column"

Generated columns are computed from the other columns of the row, so they
cannot be written to. Change the columns the expression reads instead. To see
which columns are generated:

```bash
sqlite3 app.db "SELECT name FROM pragma_table_xinfo('loans') WHERE hidden = 2;"
```

Note that `pragma_table_info` does **not** list them; only `table_xinfo` does.

## The migration runner says "up to date" but my new migration did not run

`PRAGMA user_version` is already at or above your migration's number. Check:

```bash
sqlite3 app.db "PRAGMA user_version;"
ls examples/migrations/
```

Give the new file a number higher than the current version. Do not renumber a
migration that has already been applied somewhere — an applied migration is
history, and you change history by adding to it.

## The migration runner refuses to start (exit 2)

Three things cause this, and the message says which:

- a file whose name is not `NNN_description.sql`;
- two files claiming the same version number;
- a file containing its own `BEGIN`, `COMMIT` or `ROLLBACK` — the runner owns
  the transaction, and a file that manages its own would break the
  all-or-nothing guarantee.

Nothing is written to the database in any of these cases.

## `shasum: command not found`

On some Linux distributions the tool is `sha256sum`:

```bash
sha256sum library.db
```

The harness uses `shasum -a 256`. If yours does not have it, install `perl` or
edit the two calls in `tests/run_tests.sh`.

## The tests pass but I want to see one fail

Change an expected value in `tests/run_tests.sh` — for example make
`check_eq "seed has 6 members" "6"` say `"999"` — and re-run. You should see a
`FAIL:` line naming both the expected and the actual value, a non-zero final
count, and exit status 1. A suite you have never seen fail is a suite you have
no reason to trust.

## Windows

Use WSL and follow the Linux instructions. On native Windows the `sqlite3`
shell exists but `tests/run_tests.sh` is a bash script and `shasum` is absent.
No captures were taken on native Windows, so nothing here claims what it would
print.
