"""SQL injection, demonstrated rather than warned about.

This script builds a throwaway database in a fresh temporary directory,
attacks it for real, and deletes it on the way out. Nothing outside that
directory is touched, and the directory is removed even if a check fails.

Four acts:

  1. A query built by string concatenation is broken by a crafted input,
     and every private address in the table comes back.
  2. The same trick aimed at destroying a table meets `execute`, which
     refuses more than one statement — an honest limit worth knowing, and
     not a defence you may rely on.
  3. The same string handed to `executescript`, which does accept several
     statements, destroys the table for real. The damage is printed.
  4. The identical hostile strings, bound as parameters, are treated as
     ordinary text: zero rows, nothing dropped, no error.

Run it:  python3 injection_demo.py
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

# The two inputs. Imagine each arriving from a search box, a query string,
# a CSV column, or the output of a language model asked to name an author.
LEAK = "Ada' OR '1'='1"
DESTROY = "Ada'; DROP TABLE members; --"

SCHEMA = """
CREATE TABLE members (
    member_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    email     TEXT NOT NULL,
    pin       TEXT NOT NULL
);
INSERT INTO members (name, email, pin) VALUES
    ('Ada Lovelace',  'ada@example.invalid',   '4417'),
    ('Grace Hopper',  'grace@example.invalid', '9021'),
    ('Alan Turing',   'alan@example.invalid',  '1912');
"""

failures = 0


def check(label: str, ok: bool) -> None:
    global failures
    if ok:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}")
        failures += 1


def rule(text: str) -> None:
    print()
    print(text)
    print("-" * len(text))


def members_table_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'members'"
    ).fetchone()
    return row is not None


def main() -> int:
    sandbox = Path(tempfile.mkdtemp(prefix="day090-injection-"))
    print(f"sandbox: a throwaway database inside {sandbox.name}/ — deleted on exit")
    try:
        return run(sandbox)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)
        print()
        print("sandbox removed. Nothing outside it was ever opened.")


def run(sandbox: Path) -> int:
    path = sandbox / "victim.db"

    # ---------------------------------------------------------------- act 1
    rule("ACT 1 — the string-built query, and what the crafted value does to it")
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)

    honest = "Ada Lovelace"
    print(f'  the ordinary case, input = "{honest}"')
    built = "SELECT name, email, pin FROM members WHERE name = '" + honest + "'"
    print(f"    statement: {built}")
    rows = connection.execute(built).fetchall()
    print(f"    rows: {len(rows)}  -> {rows}")
    check("the concatenated query looks perfectly fine on ordinary input", len(rows) == 1)

    print()
    print(f'  the crafted case, input = "{LEAK}"')
    built = "SELECT name, email, pin FROM members WHERE name = '" + LEAK + "'"
    print(f"    statement: {built}")
    print("    " + " " * (len("statement: ") + built.index("' OR")) + "^ the apostrophe inside the value closed the string early")
    rows = connection.execute(built).fetchall()
    print(f"    rows: {len(rows)}  -> every member, with address and PIN:")
    for row in rows:
        print(f"      {row}")
    check(
        "one apostrophe changed the statement's meaning: the WHERE clause "
        "became name = 'Ada' OR '1'='1', which is true for every row",
        len(rows) == 3,
    )
    print(
        "    Nothing was escaped, nothing was 'hacked'. The value became CODE\n"
        "    because it was inside the string before the parser ever saw it."
    )

    # ---------------------------------------------------------------- act 2
    rule("ACT 2 — the destructive version meets execute(), which takes one statement")
    built = "SELECT name FROM members WHERE name = '" + DESTROY + "'"
    print(f"    statement: {built}")
    try:
        connection.execute(built).fetchall()
        raised = "nothing"
    except sqlite3.Error as error:
        raised = f"{type(error).__name__}: {error}"
    print(f"    raised: {raised}")
    check(
        "sqlite3.Connection.execute refuses more than one statement, so this "
        "particular attack fails here",
        raised.startswith("ProgrammingError"),
    )
    check("the members table is still standing after act 2", members_table_exists(connection))
    print(
        "    Read that carefully. The attack failed because of a limit in the\n"
        "    Python module, NOT because the code was safe. Act 1 already leaked\n"
        "    every row through the same hole, and act 3 removes the limit."
    )

    # ---------------------------------------------------------------- act 3
    rule("ACT 3 — the same string handed to executescript(), which accepts many")
    print(f"    statement: {built}")
    before = connection.execute("SELECT count(*) FROM members").fetchone()[0]
    print(f"    members before: {before} rows")
    connection.executescript(built)
    exists = members_table_exists(connection)
    print(f"    members table exists afterwards: {exists}")
    try:
        connection.execute("SELECT count(*) FROM members").fetchone()
        aftermath = "still queryable"
    except sqlite3.Error as error:
        aftermath = f"{type(error).__name__}: {error}"
    print(f"    querying it now: {aftermath}")
    check("the table was destroyed by a value that arrived as text", not exists)
    check("and the program that did it contained no DROP anywhere", "DROP" not in SCHEMA)
    connection.close()

    # ---------------------------------------------------------------- act 4
    rule("ACT 4 — the identical inputs, bound as parameters")
    path2 = sandbox / "protected.db"
    connection = sqlite3.connect(path2)
    connection.executescript(SCHEMA)

    for label, value in (("leak attempt", LEAK), ("destroy attempt", DESTROY)):
        rows = connection.execute(
            "SELECT name, email, pin FROM members WHERE name = ?", (value,)
        ).fetchall()
        print(f'    {label:16} value = "{value}"')
        print(f"    {'':16} statement: SELECT name, email, pin FROM members WHERE name = ?")
        print(f"    {'':16} rows returned: {len(rows)}")
        check(f"{label}: bound as a value, it matched no member name", rows == [])

    check("the members table is untouched", members_table_exists(connection))
    check(
        "and still holds all three rows",
        connection.execute("SELECT count(*) FROM members").fetchone()[0] == 3,
    )
    print(
        "    The statement was compiled with a '?' in it BEFORE any value\n"
        "    existed. Binding cannot change a compiled statement's shape, so\n"
        "    the apostrophe is just a character in a string that no member is\n"
        "    called. The engine compared it and moved on."
    )
    connection.close()

    rule("SUMMARY")
    print("    concatenated + crafted input  -> 3 private rows leaked, then a table dropped")
    print("    parameterised + same input    -> 0 rows, no error, nothing changed")
    print("    the difference is one character: ? instead of an f-string.")
    print()
    print(f"{failures} failure(s) in this demonstration.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
