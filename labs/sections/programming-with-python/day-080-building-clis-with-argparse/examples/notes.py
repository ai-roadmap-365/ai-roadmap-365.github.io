#!/usr/bin/env python3
"""notes — a small note-taking tool, built the way a real command should be.

This is the reference implementation for the Day 080 lab. Everything in it is
standard library: argparse, json, csv, os, sys, pathlib, datetime.

The shape to notice, because it is the shape of every serious Python CLI:

  build_parser()          builds the parser and NOTHING else — no I/O, no work
  parse_args(argv)        takes an EXPLICIT list, so tests never touch sys.argv
  cmd_add / cmd_list /    one handler per subcommand, bound by set_defaults
  cmd_search / ...        so dispatch is `args.func(args, streams)`
  main(argv, streams)     wires them together and returns an exit code

Streams are injected rather than reached for, so the same code can be driven
by a test with io.StringIO in place of the terminal. That is Day 74's boundary
lesson applied to standard input and standard output.

Exit codes:
  0  the command did what it said
  1  a runtime refusal (no such note, unreadable store)
  2  a usage error (argparse's own convention, and we keep it)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Sequence, TextIO

__version__ = "1.0.0"

DEFAULT_STORE = "notes.json"
STORE_ENV_VAR = "NOTES_STORE"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class NotesError(Exception):
    """A refusal stated in the language of the tool, not of the machinery."""


# ---------------------------------------------------------------------------
# Streams — the three surfaces every command-line program stands on
# ---------------------------------------------------------------------------


@dataclass
class Streams:
    """Standard input, output and error, passed in rather than imported.

    A handler that writes to `streams.stdout` can be tested by handing it an
    io.StringIO. A handler that calls `print()` can only be tested by capturing
    the process. The difference is one parameter.
    """

    stdin: TextIO
    stdout: TextIO
    stderr: TextIO

    @classmethod
    def real(cls) -> "Streams":
        return cls(stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    def stdin_is_a_terminal(self) -> bool:
        """True when nothing is piped in — so the tool would hang waiting."""
        try:
            return self.stdin.isatty()
        except (AttributeError, ValueError):
            return False


# ---------------------------------------------------------------------------
# Custom argument types — conversion and validation in one place
# ---------------------------------------------------------------------------


def iso_date(text: str) -> date:
    """Convert YYYY-MM-DD to a date, or explain precisely why it cannot.

    Raising ArgumentTypeError is what makes argparse print a usage message on
    standard error and exit 2. Raising ValueError would give the user a
    traceback, which is a bug report addressed to the wrong person.
    """
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{text!r} is not a date in YYYY-MM-DD form (for example 2026-03-01)"
        ) from None


def positive_int(text: str) -> int:
    """Convert to an int that is at least 1."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number") from None
    if value < 1:
        raise argparse.ArgumentTypeError(f"{value} is not at least 1")
    return value


def tag_name(text: str) -> str:
    """A tag is lower case, non-empty, and has no spaces or commas."""
    cleaned = text.strip().lower()
    if not cleaned:
        raise argparse.ArgumentTypeError("a tag cannot be empty")
    if any(ch in cleaned for ch in " ,\t"):
        raise argparse.ArgumentTypeError(
            f"{text!r} is not a tag: tags contain no spaces or commas"
        )
    return cleaned


# ---------------------------------------------------------------------------
# The store — a small JSON file, kept behind two functions
# ---------------------------------------------------------------------------


def load_store(path: Path) -> dict[str, Any]:
    """Read the store, or return an empty one if the file is not there yet."""
    if not path.exists():
        return {"version": 1, "notes": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise NotesError(f"{path} is not valid JSON ({exc.msg}, line {exc.lineno})") from None
    except OSError as exc:
        raise NotesError(f"cannot read {path}: {exc.strerror}") from None
    if not isinstance(data, dict) or not isinstance(data.get("notes"), list):
        raise NotesError(f"{path} does not look like a notes store")
    return data


def save_store(path: Path, data: dict[str, Any]) -> None:
    """Write the store back, formatted so a human can read the diff."""
    text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise NotesError(f"cannot write {path}: {exc.strerror}") from None


def next_id(notes: list[dict[str, Any]]) -> int:
    return max((int(note["id"]) for note in notes), default=0) + 1


def store_path(args: argparse.Namespace) -> Path:
    """Resolve the store path using the precedence users expect.

    flag beats environment beats built-in default. The flag's own default is
    None precisely so that "the user did not say" is distinguishable from
    "the user said the default".
    """
    if args.store is not None:
        return Path(args.store)
    from_env = os.environ.get(STORE_ENV_VAR)
    if from_env:
        return Path(from_env)
    return Path(DEFAULT_STORE)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_table(notes: list[dict[str, Any]], stream: TextIO) -> None:
    if not notes:
        return
    id_width = max(2, max(len(str(note["id"])) for note in notes))
    tag_width = max(4, max(len(",".join(note["tags"])) for note in notes))
    header = f"{'ID'.rjust(id_width)}  {'DATE':10}  {'TAGS'.ljust(tag_width)}  TEXT"
    stream.write(header + "\n")
    stream.write("-" * len(header) + "\n")
    for note in notes:
        tags = ",".join(note["tags"])
        stream.write(
            f"{str(note['id']).rjust(id_width)}  {note['date']:10}  "
            f"{tags.ljust(tag_width)}  {note['text']}\n"
        )


def render_json(notes: list[dict[str, Any]], stream: TextIO) -> None:
    json.dump(notes, stream, indent=2, ensure_ascii=False, sort_keys=True)
    stream.write("\n")


def render_csv(notes: list[dict[str, Any]], stream: TextIO) -> None:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["id", "date", "tags", "text"])
    for note in notes:
        writer.writerow([note["id"], note["date"], ";".join(note["tags"]), note["text"]])


# ---------------------------------------------------------------------------
# Subcommand handlers — each returns an exit code, each takes its streams
# ---------------------------------------------------------------------------


def cmd_add(args: argparse.Namespace, streams: Streams) -> int:
    if args.text == "-":
        if streams.stdin_is_a_terminal():
            args.parser.error(
                "reading from standard input was requested with '-', "
                "but standard input is a terminal; pipe something in"
            )
        text = streams.stdin.read().strip()
        if not text:
            raise NotesError("standard input was empty, so there is nothing to add")
    else:
        text = args.text.strip()
        if not text:
            raise NotesError("a note cannot be empty")

    when = args.on if args.on is not None else date.today()
    path = store_path(args)
    data = load_store(path)
    note = {
        "id": next_id(data["notes"]),
        "date": when.isoformat(),
        "tags": sorted(set(args.tag or [])),
        "text": text,
    }
    data["notes"].append(note)

    if args.dry_run:
        if not args.quiet:
            streams.stdout.flush()
            streams.stderr.write(
                f"dry run: would add note {note['id']} to {path} (nothing was written)\n"
            )
        return 0

    save_store(path, data)
    if not args.quiet:
        streams.stdout.write(f"added note {note['id']}\n")
    if args.verbose:
        streams.stdout.flush()
        streams.stderr.write(f"store: {path}\n")
    return 0


def select_notes(args: argparse.Namespace, notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen = notes
    if args.tag:
        wanted = set(args.tag)
        chosen = [n for n in chosen if wanted.issubset(set(n["tags"]))]
    if getattr(args, "since", None) is not None:
        chosen = [n for n in chosen if n["date"] >= args.since.isoformat()]
    if getattr(args, "limit", None) is not None:
        chosen = chosen[-args.limit :]
    return chosen


def cmd_list(args: argparse.Namespace, streams: Streams) -> int:
    path = store_path(args)
    notes = select_notes(args, load_store(path)["notes"])
    if args.format == "json":
        render_json(notes, streams.stdout)
    else:
        render_table(notes, streams.stdout)
    if args.verbose:
        streams.stdout.flush()
        streams.stderr.write(f"{len(notes)} note(s) from {path}\n")
    return 0


def cmd_search(args: argparse.Namespace, streams: Streams) -> int:
    path = store_path(args)
    notes = load_store(path)["notes"]
    needle = args.pattern.lower() if args.ignore_case else args.pattern
    matches = [
        note
        for note in notes
        if needle in (note["text"].lower() if args.ignore_case else note["text"])
    ]
    if args.format == "json":
        render_json(matches, streams.stdout)
    else:
        render_table(matches, streams.stdout)
    if args.verbose:
        streams.stdout.flush()
        streams.stderr.write(f"{len(matches)} of {len(notes)} note(s) matched\n")
    return 0 if matches else 1


def cmd_export(args: argparse.Namespace, streams: Streams) -> int:
    path = store_path(args)
    notes = load_store(path)["notes"]
    if args.format == "csv":
        render_csv(notes, streams.stdout)
    else:
        render_json(notes, streams.stdout)
    if args.verbose:
        streams.stdout.flush()
        streams.stderr.write(f"exported {len(notes)} note(s) as {args.format}\n")
    return 0


def cmd_remove(args: argparse.Namespace, streams: Streams) -> int:
    path = store_path(args)
    data = load_store(path)
    present = {int(note["id"]) for note in data["notes"]}
    missing = [str(i) for i in args.ids if i not in present]
    if missing:
        raise NotesError(f"no note with id {', '.join(missing)} in {path}")

    doomed = sorted(set(args.ids))
    if args.dry_run:
        for note_id in doomed:
            streams.stdout.write(f"would remove note {note_id}\n")
        streams.stdout.flush()
        streams.stderr.write(
            f"dry run: {len(doomed)} note(s) would be removed; {path} was not touched\n"
        )
        return 0

    data["notes"] = [n for n in data["notes"] if int(n["id"]) not in set(doomed)]
    save_store(path, data)
    if not args.quiet:
        for note_id in doomed:
            streams.stdout.write(f"removed note {note_id}\n")
    return 0


# ---------------------------------------------------------------------------
# The parser — a declaration of the tool's whole interface, in one place
# ---------------------------------------------------------------------------


def common_options() -> argparse.ArgumentParser:
    """Options shared by every subcommand.

    `add_help=False` matters: this parser is only ever used as a parent, and
    without it every subcommand would try to define -h twice and crash.
    """
    parent = argparse.ArgumentParser(add_help=False)

    storage = parent.add_argument_group(
        "storage options",
        f"where the notes live. Precedence: --store, then ${STORE_ENV_VAR}, "
        f"then ./{DEFAULT_STORE}",
    )
    storage.add_argument(
        "--store",
        metavar="PATH",
        default=None,
        help=f"path to the JSON store (default: ${STORE_ENV_VAR} or ./{DEFAULT_STORE})",
    )

    noise = parent.add_argument_group("output options")
    loudness = noise.add_mutually_exclusive_group()
    loudness.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="explain what is happening, on standard error",
    )
    loudness.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="print nothing on success",
    )
    return parent


def build_parser() -> argparse.ArgumentParser:
    """Build the parser. This function does no work and touches no file."""
    parent = common_options()

    parser = argparse.ArgumentParser(
        prog="notes",
        description="Keep short notes in a JSON file you can read with your own eyes.",
        epilog=(
            "Examples:\n"
            "  notes add 'ring the dentist' --tag health --on 2026-03-01\n"
            "  echo 'from a pipe' | notes add - --tag inbox\n"
            "  notes list --format json | python3 -m json.tool\n"
            "  notes remove 3 --dry-run\n"
            "\n"
            "Exit codes: 0 success, 1 refusal, 2 usage error."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )

    subcommands = parser.add_subparsers(
        title="subcommands",
        dest="command",
        metavar="<command>",
        required=True,
    )

    # --- add ---------------------------------------------------------------
    add = subcommands.add_parser(
        "add",
        parents=[parent],
        help="add one note",
        description="Add one note. Use '-' as the text to read it from standard input.",
    )
    add.add_argument("text", help="the note text, or '-' to read standard input")
    add.add_argument(
        "-t",
        "--tag",
        action="append",
        type=tag_name,
        metavar="TAG",
        help="attach a tag; repeat the option for more than one",
    )
    add.add_argument(
        "--on",
        type=iso_date,
        metavar="YYYY-MM-DD",
        help="the date to file the note under (default: today)",
    )
    add.add_argument(
        "--dry-run",
        action="store_true",
        help="say what would happen without writing anything",
    )
    add.set_defaults(func=cmd_add, parser=add)

    # --- list --------------------------------------------------------------
    listing = subcommands.add_parser(
        "list",
        parents=[parent],
        help="list notes",
        description="List notes, newest last.",
    )
    listing.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="output format (default: table)",
    )
    listing.add_argument(
        "-t", "--tag", action="append", type=tag_name, metavar="TAG", help="only notes with this tag"
    )
    listing.add_argument("--since", type=iso_date, metavar="YYYY-MM-DD", help="only notes on or after this date")
    listing.add_argument("-n", "--limit", type=positive_int, metavar="N", help="show at most N notes")
    listing.set_defaults(func=cmd_list, parser=listing)

    # --- search ------------------------------------------------------------
    search = subcommands.add_parser(
        "search",
        parents=[parent],
        help="find notes containing text",
        description="Find notes whose text contains PATTERN. Exits 1 when nothing matched.",
    )
    search.add_argument("pattern", help="the text to look for")
    search.add_argument("-i", "--ignore-case", action="store_true", help="match regardless of case")
    search.add_argument(
        "--format", choices=["table", "json"], default="table", help="output format (default: table)"
    )
    search.set_defaults(func=cmd_search, parser=search)

    # --- export ------------------------------------------------------------
    export = subcommands.add_parser(
        "export",
        parents=[parent],
        help="write every note to standard output",
        description="Write every note to standard output so it can be piped or redirected.",
    )
    export.add_argument(
        "--format", choices=["json", "csv"], default="json", help="output format (default: json)"
    )
    export.set_defaults(func=cmd_export, parser=export)

    # --- remove ------------------------------------------------------------
    remove = subcommands.add_parser(
        "remove",
        parents=[parent],
        help="delete notes by id",
        description="Delete one or more notes. Destructive, so it has --dry-run.",
    )
    remove.add_argument("ids", nargs="+", type=positive_int, metavar="ID", help="note id to remove")
    remove.add_argument(
        "--dry-run",
        action="store_true",
        help="list what would be removed and leave the store untouched",
    )
    remove.set_defaults(func=cmd_remove, parser=remove)

    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse an EXPLICIT argument list.

    Defaulting to None (which argparse turns into sys.argv[1:]) keeps the real
    program convenient, while every test passes its own list and never has to
    monkey-patch a global.
    """
    return build_parser().parse_args(argv)


def main(argv: Sequence[str] | None = None, streams: Streams | None = None) -> int:
    streams = streams or Streams.real()
    args = parse_args(argv)
    handler: Callable[[argparse.Namespace, Streams], int] = args.func
    try:
        return handler(args, streams)
    except NotesError as exc:
        streams.stderr.write(f"notes: {exc}\n")
        return 1
    except BrokenPipeError:
        # `notes export | head -2` closes the pipe early. That is not an error.
        return 0
    except KeyboardInterrupt:
        streams.stderr.write("notes: interrupted\n")
        return 130


if __name__ == "__main__":
    sys.exit(main())
