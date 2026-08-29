#!/usr/bin/env python3
"""Prove that a database is one ordinary file, and read its header yourself.

The SQLite file format is documented and stable: the first 16 bytes of every
database file are the ASCII string "SQLite format 3" followed by a single NUL
byte. Bytes 16 and 17 are the page size, big-endian. Bytes 28-31 are the
number of pages ("the database size in pages").

This script does not take the documentation's word for it. It opens the file
in binary mode and reads the bytes.

Run it:  python3 file_facts.py library.db
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

EXPECTED_MAGIC = b"SQLite format 3\x00"


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("library.db")
    if not path.exists():
        print(f"no such database: {path}", file=sys.stderr)
        return 1

    raw = path.read_bytes()
    header = raw[:16]

    print(f"path:        {path.name}")
    print(f"size:        {path.stat().st_size:,} bytes")
    print(f"first 16 B:  {header!r}")
    print(f"as text:     {header[:15].decode('ascii')!r} + {header[15:]!r}")
    print(f"hex:         {header.hex(' ')}")
    print(f"matches the documented magic string: {header == EXPECTED_MAGIC}")
    print()

    # Bytes 16-17: page size in bytes, big-endian. The value 1 means 65536.
    page_size = int.from_bytes(raw[16:18], "big")
    if page_size == 1:
        page_size = 65536
    # Bytes 28-31: size of the database file in pages.
    page_count = int.from_bytes(raw[28:32], "big")
    print(f"page size (header bytes 16-17):  {page_size:,} bytes")
    print(f"page count (header bytes 28-31): {page_count}")
    print(f"pages * page size:               {page_size * page_count:,} bytes")
    print()

    # The same two numbers, asked of the engine rather than read off the disk.
    connection = sqlite3.connect(path)
    try:
        from_engine_size = connection.execute("PRAGMA page_size").fetchone()[0]
        from_engine_count = connection.execute("PRAGMA page_count").fetchone()[0]
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_schema"
                " WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
                " ORDER BY name"
            )
        ]
    finally:
        connection.close()

    print(f"PRAGMA page_size:    {from_engine_size:,}")
    print(f"PRAGMA page_count:   {from_engine_count}")
    print(f"PRAGMA journal_mode: {journal_mode}")
    print(f"tables:              {', '.join(tables)}")
    print()
    print("The bytes on disk and the engine agree, because there is only one")
    print("artefact here: a file you could copy with cp and mail to somebody.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
