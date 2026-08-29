#!/usr/bin/env python3
"""YOUR WORK — the migration runner, with four gaps to fill.

The finished version is in ``examples/migrate.py``. Try each exercise before
reading it; the gaps are the four decisions that make a runner trustworthy
rather than merely working.

Run it the same way as the finished one:

    python3 starter/migrate.py --db /tmp/app.db --dir examples/migrations
    python3 starter/migrate.py --db /tmp/app.db --dir examples/migrations   # again

The second run must apply nothing. If it re-applies everything, exercise 2 is
not finished. If it half-applies a broken migration, exercise 3 is not.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

FILENAME = re.compile(r"^(\d+)_[A-Za-z0-9_.-]+\.sql$")
OWNS_TRANSACTION = re.compile(r"^\s*(BEGIN|COMMIT|END|ROLLBACK)\b", re.IGNORECASE | re.MULTILINE)


class MigrationError(Exception):
    """A problem with the migration set itself, not with applying it."""


def discover(directory: Path) -> list[tuple[int, Path]]:
    """Return [(version, path), ...] sorted by version, or raise MigrationError."""
    if not directory.is_dir():
        raise MigrationError(f"no such migrations directory: {directory}")

    found: dict[int, Path] = {}
    for path in sorted(directory.iterdir()):
        if path.suffix != ".sql":
            continue
        match = FILENAME.match(path.name)
        if not match:
            raise MigrationError(f"{path.name}: expected a name like 001_description.sql")
        version = int(match.group(1))
        if version == 0:
            raise MigrationError(f"{path.name}: version 0 is the empty database")

        # ------------------------------------------------------------------
        # EXERCISE 1 — refuse two migrations that claim the same version.
        # ------------------------------------------------------------------
        # Two developers branch, both write 005_..., both merge. Now the
        # version number no longer identifies a schema, and two databases that
        # both say "version 5" have different tables in them.
        #
        # If `version` is already a key of `found`, raise MigrationError naming
        # BOTH filenames. Then delete this comment and the line below.
        raise NotImplementedError("exercise 1: detect duplicate version numbers")

        found[version] = path

    # ------------------------------------------------------------------
    # EXERCISE 4 — refuse a migration that manages its own transaction.
    # ------------------------------------------------------------------
    # The runner wraps each file in BEGIN ... COMMIT. A stray COMMIT inside a
    # file ends that transaction early, so the statements after it are no
    # longer covered and a later failure cannot undo them.
    #
    # For each discovered file, read its text and search it with
    # OWNS_TRANSACTION. If it matches, raise MigrationError explaining why.
    # (Do this AFTER the loop above, over everything in `found`.)

    return sorted(found.items())


def current_version(conn: sqlite3.Connection) -> int:
    # ----------------------------------------------------------------------
    # EXERCISE 2 — read the schema version out of the database.
    # ----------------------------------------------------------------------
    # `PRAGMA user_version` is a 32-bit integer in the database header that
    # SQLite never uses for anything itself. Run it, take the first column of
    # the first row, and return it as an int.
    #
    # Why not a table of applied migrations? You could, and the plain-SQL
    # approach in the lesson does exactly that. user_version costs no table,
    # no query and no bootstrapping problem -- but it holds one number, so it
    # cannot record WHEN each migration ran or WHO ran it. That is the trade.
    raise NotImplementedError("exercise 2: return PRAGMA user_version")


def apply_one(conn: sqlite3.Connection, version: int, path: Path) -> None:
    """Apply one migration and bump the version, atomically."""
    body = path.read_text(encoding="utf-8")

    # ----------------------------------------------------------------------
    # EXERCISE 3 — make the change and the version bump one transaction.
    # ----------------------------------------------------------------------
    # Build a script that is, in order:
    #
    #     BEGIN;
    #     <body>
    #     PRAGMA user_version = <version>;
    #     COMMIT;
    #
    # and run it with conn.executescript(). Wrap the call in try/except
    # sqlite3.Error; on error, ROLLBACK if conn.in_transaction, then re-raise.
    #
    # This is the entire safety property of the runner. Bump the version in a
    # separate statement afterwards and a crash in between leaves a database
    # whose schema and whose version number disagree -- and every later run
    # will then either skip a change that never happened or repeat one that
    # did. PRAGMA user_version is covered by the transaction just like any
    # other write, which is what makes the single-script version correct.
    #
    # Note: PRAGMA user_version does not accept a bound parameter. Format the
    # value in with int(version) so the type is unambiguous.
    raise NotImplementedError("exercise 3: apply the migration atomically")


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
    conn.isolation_level = None
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
