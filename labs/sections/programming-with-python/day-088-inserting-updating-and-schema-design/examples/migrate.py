#!/usr/bin/env python3
"""A migration runner in about 150 lines, built from first principles.

A migration runner answers one question: "which schema changes has this
database already had, and which does it still need?" Everything else is
detail. This one keeps the answer in ``PRAGMA user_version`` -- a 32-bit
integer that lives in the database header, that SQLite itself never touches,
and that is covered by transactions like any other write.

That last property is the whole design. Applying a migration means:

    BEGIN;
      <the migration's statements>
      PRAGMA user_version = <n>;
    COMMIT;

If anything in the middle fails, the rollback undoes the schema change AND the
version bump together. There is no state in which the change half-happened but
the database claims to be at the new version -- which is the failure mode that
makes hand-run migration scripts so unpleasant to recover from.

SQLite makes this possible because its DDL is transactional: CREATE TABLE,
DROP TABLE and ALTER TABLE can all be rolled back. Not every database can do
this, and it is the single biggest reason migrations feel safer here.

Usage
-----
    python3 migrate.py --db app.db --dir migrations
    python3 migrate.py --db app.db --dir migrations --status
    python3 migrate.py --db app.db --dir migrations --dry-run

Exit codes
----------
    0  the database is at the latest version (whether or not work was done)
    1  a migration failed and was rolled back
    2  the migrations directory is malformed
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

# A migration file is called NNN_some_description.sql. The number is the
# version it takes the database TO, and it is the only part that matters.
FILENAME = re.compile(r"^(\d+)_[A-Za-z0-9_.-]+\.sql$")

# A migration must not manage its own transaction: the runner owns that, and a
# stray COMMIT inside a file would end the runner's transaction early and break
# the all-or-nothing guarantee. Catching this at load time turns a subtle
# corruption bug into an error message.
OWNS_TRANSACTION = re.compile(r"^\s*(BEGIN|COMMIT|END|ROLLBACK)\b", re.IGNORECASE | re.MULTILINE)


class MigrationError(Exception):
    """A problem with the migration set itself, not with applying it."""


def discover(directory: Path) -> list[tuple[int, Path]]:
    """Return [(version, path), ...] sorted by version, or raise."""
    if not directory.is_dir():
        raise MigrationError(f"no such migrations directory: {directory}")

    found: dict[int, Path] = {}
    for path in sorted(directory.iterdir()):
        if path.suffix != ".sql":
            continue
        match = FILENAME.match(path.name)
        if not match:
            raise MigrationError(
                f"{path.name}: expected a name like 001_description.sql"
            )
        version = int(match.group(1))
        if version == 0:
            raise MigrationError(f"{path.name}: version 0 is the empty database")
        if version in found:
            raise MigrationError(
                f"two migrations claim version {version}: "
                f"{found[version].name} and {path.name}"
            )
        found[version] = path

    for version, path in found.items():
        body = path.read_text(encoding="utf-8")
        if OWNS_TRANSACTION.search(body):
            raise MigrationError(
                f"{path.name}: contains its own BEGIN/COMMIT/ROLLBACK. "
                "The runner wraps every migration in one transaction; a file "
                "that manages its own would break the all-or-nothing guarantee."
            )

    return sorted(found.items())


def current_version(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


def apply_one(conn: sqlite3.Connection, version: int, path: Path) -> None:
    """Apply one migration and bump the version, atomically."""
    body = path.read_text(encoding="utf-8")
    # PRAGMA user_version does not accept a bound parameter, so the value is
    # formatted in. It is an int() from a regex match on a filename, so there
    # is nothing here an attacker could reach even if they could name files.
    script = f"BEGIN;\n{body}\nPRAGMA user_version = {int(version)};\nCOMMIT;"
    try:
        conn.executescript(script)
    except sqlite3.Error:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply versioned SQL migrations.")
    parser.add_argument("--db", required=True, type=Path, help="database file")
    parser.add_argument("--dir", required=True, type=Path, help="migrations directory")
    parser.add_argument("--status", action="store_true", help="report and do nothing")
    parser.add_argument("--dry-run", action="store_true", help="name what would run")
    args = parser.parse_args(argv)

    try:
        migrations = discover(args.dir)
    except MigrationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not migrations:
        print(f"error: no migrations found in {args.dir}", file=sys.stderr)
        return 2

    latest = migrations[-1][0]
    conn = sqlite3.connect(args.db)
    # Manual transaction control: the runner issues BEGIN and COMMIT itself as
    # part of the migration script, so the driver must not add its own.
    conn.isolation_level = None
    # Foreign keys OFF during a migration, per the documented table-rebuild
    # procedure: a rebuild drops and recreates tables, and enforcement would
    # fire delete rules on rows that are only passing through. This must be set
    # outside a transaction, which is why it happens here and not in a file.
    conn.execute("PRAGMA foreign_keys = OFF")

    try:
        at = current_version(conn)
        pending = [(v, p) for v, p in migrations if v > at]

        print(f"database: {args.db}")
        print(f"current version: {at}")
        print(f"latest available: {latest}")

        if not pending:
            print("up to date -- 0 migration(s) applied")
            return 0

        if args.status or args.dry_run:
            print(f"pending: {len(pending)} migration(s)")
            for version, path in pending:
                print(f"  would apply {version:03d}: {path.name}")
            print("nothing was written")
            return 0

        applied = 0
        for version, path in pending:
            print(f"  applying {version:03d}: {path.name} ... ", end="", flush=True)
            try:
                apply_one(conn, version, path)
            except sqlite3.Error as exc:
                print("FAILED", flush=True)
                print(f"error: {path.name}: {exc}", file=sys.stderr)
                print(
                    f"error: rolled back; database is still at version "
                    f"{current_version(conn)}",
                    file=sys.stderr,
                )
                return 1
            applied += 1
            print("ok")

        # Enforcement was off throughout. Audit before handing the database
        # back, exactly as the table-rebuild procedure requires.
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            print(
                f"error: {len(violations)} foreign key violation(s) after migrating",
                file=sys.stderr,
            )
            return 1

        print(f"now at version {current_version(conn)} -- {applied} migration(s) applied")
        return 0
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
