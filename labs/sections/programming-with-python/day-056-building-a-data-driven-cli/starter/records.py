#!/usr/bin/env python3
"""records.py — YOUR working file.

Build this data-driven CLI one exercise at a time. Each numbered exercise
below names exactly what to write. The finished reference is in
examples/records.py — try each exercise yourself before peeking.

When all five exercises are done, this file behaves like the reference:

    python3 starter/records.py --store data.json add --name "Ada" --email ada@example.com
    python3 starter/records.py --store data.json list
    python3 starter/records.py --store data.json find --field name --query ada
    python3 starter/records.py --store data.json delete --id 1

Then run:  bash tests/run_tests.sh
"""
import argparse
import json
import sys


def load_records(path):
    """Return the list of records stored at path (missing file => empty)."""
    # Exercise 1: LOAD JSON.
    # 1. Open path for reading and use json.load to read the data.
    # 2. If the file does not exist (FileNotFoundError), return [] — the
    #    first run is not an error.
    # 3. If json.load raises json.JSONDecodeError, raise ValueError with a
    #    clear message naming the file.
    # 4. If the data is not a list, raise ValueError.
    # 5. Otherwise return the data.
    raise NotImplementedError("Exercise 1: implement load_records")


def save_records(path, records):
    """Write records to path as pretty-printed JSON. (Provided.)"""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def next_id(records):
    """Return the next id: one more than the largest existing id, or 1."""
    # Exercise 2: COMPUTE THE NEXT ID.
    # Return 1 + the maximum "id" among records, or 1 when records is empty.
    # Hint: max((r["id"] for r in records), default=0) + 1
    raise NotImplementedError("Exercise 2: implement next_id")


def validate_new(name, email):
    """Raise ValueError if a new record's name or email is bad. (Provided.)"""
    if not name.strip():
        raise ValueError("name must not be empty")
    if "@" not in email:
        raise ValueError(f"'{email}' is not a valid email (needs '@')")


def format_record(record):
    """Return the one-line, human-readable form of a record. (Provided.)"""
    return f"#{record['id']}: {record['name']} <{record['email']}>"


def cmd_add(args):
    """add: load, append a validated record, save, and report it."""
    # Exercise 3: THE COMMAND LOOP (load -> mutate -> save -> report).
    # 1. records = load_records(args.store)
    # 2. validate_new(args.name, args.email)
    # 3. build record = {"id": next_id(records), "name": args.name.strip(),
    #    "email": args.email.strip()}
    # 4. append it to records, then save_records(args.store, records)
    # 5. print(f"added {format_record(record)}") and return 0
    raise NotImplementedError("Exercise 3: implement cmd_add")


def cmd_list(args):
    """list: print every record, or a notice when empty. (Provided.)"""
    records = load_records(args.store)
    if not records:
        print("no records")
        return 0
    for record in records:
        print(format_record(record))
    return 0


def cmd_find(args):
    """find: print matching records; exit 0 if any, 1 if none."""
    # Exercise 4: SEARCH WITH EXIT CODES.
    # 1. records = load_records(args.store)
    # 2. needle = args.query.lower()
    # 3. matches = every record where needle is in the chosen field,
    #    compared case-insensitively:
    #        str(record.get(args.field, "")).lower()
    # 4. If there are no matches: print a message to sys.stderr and return 1.
    # 5. Otherwise print each match with format_record and return 0.
    raise NotImplementedError("Exercise 4: implement cmd_find")


def cmd_delete(args):
    """delete: remove the record with the given id, or report it. (Provided.)"""
    records = load_records(args.store)
    kept = [record for record in records if record["id"] != args.id]
    if len(kept) == len(records):
        print(f"error: no record with id {args.id}", file=sys.stderr)
        return 1
    save_records(args.store, kept)
    print(f"deleted #{args.id}")
    return 0


def build_parser():
    """Build the argparse parser: a global --store plus four subcommands. (Provided.)"""
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
    """Entry point: parse arguments, dispatch, and turn errors into exit 1. (Provided.)"""
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        return args.func(args)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


# Exercise 5: ADD THE MAIN GUARD.
# Below this comment, add the guard so the program runs only when this file
# is executed directly (not when it is imported), passing main's return
# value to sys.exit:
#
#     if __name__ == "__main__":
#         sys.exit(main(sys.argv))
