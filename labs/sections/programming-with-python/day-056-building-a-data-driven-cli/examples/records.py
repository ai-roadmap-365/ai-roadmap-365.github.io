#!/usr/bin/env python3
"""records.py — a small, data-driven command-line tool.

Manages a list of contact records that persist between runs as a JSON file.
It is a complete rehearsal for the Week 8 project (the Terminal Task
Manager): the same skeleton of argparse subcommands, a JSON store, records
modelled as a list of dicts, and the command -> load -> mutate -> save ->
report loop, with proper exit codes and errors on standard error.

Subcommands:
    add     add a new record
    list    list every record
    find    search records by a field
    delete  remove a record by id

The data file is chosen with the global --store option, which goes BEFORE
the subcommand:

    python3 records.py --store data.json add --name "Ada Lovelace" --email ada@example.com
    python3 records.py --store data.json list
    python3 records.py --store data.json find --field name --query ada
    python3 records.py --store data.json delete --id 1

Input comes entirely from command-line arguments (never an interactive
prompt), so the tool can be tested and automated without a human.
"""
import argparse
import json
import sys


def load_records(path):
    """Return the list of records stored at path.

    A missing file is treated as an empty store (the first run is not an
    error). A file that exists but is not valid JSON, or does not hold a
    JSON list, raises ValueError with a readable message.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as err:
        raise ValueError(f"{path} is not valid JSON ({err})")
    if not isinstance(data, list):
        raise ValueError(f"{path} does not hold a list of records")
    return data


def save_records(path, records):
    """Write records to path as pretty-printed, human-diffable JSON."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def next_id(records):
    """Return the next id: one more than the largest existing id, or 1."""
    return max((record["id"] for record in records), default=0) + 1


def validate_new(name, email):
    """Raise ValueError if a new record's name or email is unacceptable."""
    if not name.strip():
        raise ValueError("name must not be empty")
    if "@" not in email:
        raise ValueError(f"'{email}' is not a valid email (needs '@')")


def format_record(record):
    """Return the one-line, human-readable form of a record."""
    return f"#{record['id']}: {record['name']} <{record['email']}>"


def cmd_add(args):
    """add: load, append a validated record, save, and report it."""
    records = load_records(args.store)
    validate_new(args.name, args.email)
    record = {
        "id": next_id(records),
        "name": args.name.strip(),
        "email": args.email.strip(),
    }
    records.append(record)
    save_records(args.store, records)
    print(f"added {format_record(record)}")
    return 0


def cmd_list(args):
    """list: print every record, or a clear notice when the store is empty."""
    records = load_records(args.store)
    if not records:
        print("no records")
        return 0
    for record in records:
        print(format_record(record))
    return 0


def cmd_find(args):
    """find: print records whose field contains the query.

    Returns exit code 0 when at least one record matches and 1 when none
    do, so a caller (or a script) can branch on "did we find anything?".
    """
    records = load_records(args.store)
    needle = args.query.lower()
    matches = [
        record
        for record in records
        if needle in str(record.get(args.field, "")).lower()
    ]
    if not matches:
        print(f"no records match {args.field}={args.query!r}", file=sys.stderr)
        return 1
    for record in matches:
        print(format_record(record))
    return 0


def cmd_delete(args):
    """delete: remove the record with the given id, or report it is absent."""
    records = load_records(args.store)
    kept = [record for record in records if record["id"] != args.id]
    if len(kept) == len(records):
        print(f"error: no record with id {args.id}", file=sys.stderr)
        return 1
    save_records(args.store, kept)
    print(f"deleted #{args.id}")
    return 0


def build_parser():
    """Build the argparse parser: a global --store plus four subcommands."""
    parser = argparse.ArgumentParser(
        prog="records.py",
        description="Manage a JSON-backed list of contact records.",
    )
    parser.add_argument(
        "--store",
        default="records.json",
        help="path to the JSON data file (default: records.json)",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="{add,list,find,delete}",
    )

    add_parser = subparsers.add_parser("add", help="add a new record")
    add_parser.add_argument("--name", required=True, help="the contact's name")
    add_parser.add_argument("--email", required=True, help="the contact's email")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="list every record")
    list_parser.set_defaults(func=cmd_list)

    find_parser = subparsers.add_parser("find", help="search records by a field")
    find_parser.add_argument(
        "--field",
        default="name",
        choices=["name", "email"],
        help="which field to search (default: name)",
    )
    find_parser.add_argument("--query", required=True, help="text to search for")
    find_parser.set_defaults(func=cmd_find)

    delete_parser = subparsers.add_parser("delete", help="delete a record by id")
    delete_parser.add_argument(
        "--id", type=int, required=True, help="the id of the record to delete"
    )
    delete_parser.set_defaults(func=cmd_delete)

    return parser


def main(argv):
    """Entry point. Parse arguments, dispatch to the chosen command, and
    turn any validation or data error into a clear message plus exit code 1.
    """
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        return args.func(args)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
