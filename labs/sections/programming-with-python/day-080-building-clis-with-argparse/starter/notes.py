#!/usr/bin/env python3
"""notes — YOUR working file for the Day 080 lab.

Eight numbered exercises build this into a tool you would actually install.
Everything that is NOT about the command-line interface — the JSON store, the
table and CSV renderers, the error type — is already written for you, because
today is about the interface, not about the storage.

Work top to bottom. After each exercise run:

    bash tests/run_tests.sh

The suite runs a structural pass while exercises remain, and switches to the
full behavioural battery — the same one the reference passes — the moment the
last NotImplementedError is gone.

The exercises, at a glance:

  1. iso_date        a custom type= that converts and validates a date
  2. positive_int    a second custom type=, for --limit and note ids
  3. common_options  an argument group and a mutually exclusive group
  4. build_parser    the root parser: prog, description, epilog, --version
  5. build_parser    the `add` subparser and its set_defaults dispatch
  6. build_parser    the list / search / export / remove subparsers
  7. cmd_add         reading the note from standard input when text is '-'
  8. cmd_remove      --dry-run: say what would happen, write nothing

Compare with examples/notes.py only AFTER you have tried. Reading the answer
first turns a two-hour lesson into a five-minute copy.
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


# ===========================================================================
# PROVIDED — you do not need to change anything between here and EXERCISE 1
# ===========================================================================


class NotesError(Exception):
    """A refusal stated in the language of the tool, not of the machinery."""


@dataclass
class Streams:
    """Standard input, output and error, passed in rather than imported."""

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


def load_store(path: Path) -> dict[str, Any]:
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
    text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise NotesError(f"cannot write {path}: {exc.strerror}") from None


def next_id(notes: list[dict[str, Any]]) -> int:
    return max((int(note["id"]) for note in notes), default=0) + 1


def store_path(args: argparse.Namespace) -> Path:
    """Precedence: --store flag, then $NOTES_STORE, then ./notes.json."""
    if args.store is not None:
        return Path(args.store)
    from_env = os.environ.get(STORE_ENV_VAR)
    if from_env:
        return Path(from_env)
    return Path(DEFAULT_STORE)


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


# ===========================================================================
# EXERCISE 1 — a custom type= that converts AND validates
# ===========================================================================
#
# argparse's `type=` is not only a converter; it is your validation hook. A
# function passed as `type=` receives the raw string, returns the converted
# value, and raises argparse.ArgumentTypeError when the string is unusable.
# argparse turns that exception into a usage message on STANDARD ERROR and
# exits 2. Raise a plain ValueError instead and the user gets a traceback.
#
# Write iso_date so that:
#   iso_date("2026-03-01")  ->  datetime.date(2026, 3, 1)
#   iso_date("2026-13-01")  ->  raises argparse.ArgumentTypeError
#   iso_date("tomorrow")    ->  raises argparse.ArgumentTypeError
#
# Hint: datetime.strptime(text, "%Y-%m-%d").date() raises ValueError on bad
# input. Catch it and re-raise as ArgumentTypeError with a message naming both
# the offending value and the form you wanted. `from None` suppresses the
# chained traceback, which the user does not need to see.
#
# Check it:
#   python3 -c "import notes; print(notes.iso_date('2026-03-01'))"


def iso_date(text: str) -> date:
    raise NotImplementedError("EXERCISE 1: convert YYYY-MM-DD or raise ArgumentTypeError")


# ===========================================================================
# EXERCISE 2 — a second custom type, for counts and ids
# ===========================================================================
#
# positive_int("3")   ->  3
# positive_int("0")   ->  raises argparse.ArgumentTypeError
# positive_int("-2")  ->  raises argparse.ArgumentTypeError
# positive_int("abc") ->  raises argparse.ArgumentTypeError
#
# Two different failures, two different messages: "is not a whole number" and
# "is not at least 1". A user who mistypes should not have to guess which.


def positive_int(text: str) -> int:
    raise NotImplementedError("EXERCISE 2: parse a whole number of at least 1")


# ===========================================================================
# PROVIDED — the handlers, except the two bodies you write in 7 and 8
# ===========================================================================


def cmd_add(args: argparse.Namespace, streams: Streams) -> int:
    if args.text == "-":
        # ===================================================================
        # EXERCISE 7 — read the note from standard input
        # ===================================================================
        #
        # `-` meaning "standard input" is a convention older than Python, and
        # following it is what lets your tool live inside a pipeline:
        #
        #     echo 'from a pipe' | python3 notes.py add - --tag inbox
        #
        # Two things must happen here.
        #
        # (a) TERMINAL DETECTION. If standard input is a terminal, nothing is
        #     piped in and reading would hang with no explanation. Call
        #     streams.stdin_is_a_terminal() and, when it is True, call
        #         args.parser.error("...")
        #     which prints usage on standard error and exits 2. Say what the
        #     user should have done, not just that they were wrong.
        #
        # (b) READ AND CHECK. Otherwise read streams.stdin.read(), strip it,
        #     and raise NotesError if it is empty — an empty pipe is a
        #     refusal, not a note.
        #
        # Assign the result to `text`.
        raise NotImplementedError("EXERCISE 7: read the note from standard input")
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
    # grep's convention: nothing found is exit 1, not an error message.
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
        # =====================================================================
        # EXERCISE 8 — --dry-run on the one destructive command
        # =====================================================================
        #
        # A dry run is a promise: the tool tells you exactly what it would do
        # and changes nothing. Two rules make that promise keepable.
        #
        #   1. Do the READS and the CHECKS for real. Notice that the
        #      "no note with id ..." check above already ran — a dry run that
        #      skipped validation would happily promise an impossible deletion.
        #   2. Never reach the write. Return before save_store is called.
        #
        # Write, for each id in `doomed`, one line on STANDARD OUTPUT:
        #     would remove note 2
        # then one summary line on STANDARD ERROR:
        #     dry run: 1 note(s) would be removed; <path> was not touched
        # then return 0.
        #
        # The split is deliberate: the ids are the RESULT (a person could pipe
        # them into another command), the summary is a DIAGNOSTIC. Call
        # streams.stdout.flush() before writing to stderr so the two arrive in
        # the order you wrote them even when standard output is a pipe.
        #
        # The test suite checks the store is byte-for-byte identical
        # afterwards. That is the only check that can prove a dry run is real.
        raise NotImplementedError("EXERCISE 8: report what would happen, write nothing")

    data["notes"] = [n for n in data["notes"] if int(n["id"]) not in set(doomed)]
    save_store(path, data)
    if not args.quiet:
        for note_id in doomed:
            streams.stdout.write(f"removed note {note_id}\n")
    return 0


# ===========================================================================
# EXERCISE 3 — shared options: an argument group and a mutually exclusive pair
# ===========================================================================
#
# Every subcommand needs --store, --verbose and --quiet. Rather than repeating
# them five times, define them once on a PARENT parser and pass parents=[...]
# to each subparser. Note add_help=False: without it, every subcommand would
# try to define -h twice and argparse would raise at import time.
#
# Build, inside this function:
#
#   (a) an ARGUMENT GROUP called "storage options", created with
#       parent.add_argument_group(title, description). Groups do not change
#       parsing at all — they only change how --help is laid out, which is
#       reason enough, because your help output is the documentation most
#       users will ever read. Give it --store with metavar="PATH",
#       default=None, and a help string naming the precedence.
#
#       default=None is not laziness. It is how you tell "the user did not
#       say" apart from "the user said the default" — which is exactly what
#       store_path() above needs in order to consult $NOTES_STORE.
#
#   (b) a MUTUALLY EXCLUSIVE GROUP holding -v/--verbose and -q/--quiet, both
#       action="store_true". Created with
#       some_group.add_mutually_exclusive_group(). Passing both then fails
#       with exit code 2 and a message naming both options — argparse does
#       that for you, and a hand-rolled `if verbose and quiet` would not
#       produce a usage message.
#
# Return the parent parser.


def common_options() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    raise NotImplementedError("EXERCISE 3: add the storage group and the verbose/quiet pair")


# ===========================================================================
# EXERCISES 4, 5 and 6 — the parser itself
# ===========================================================================


def build_parser() -> argparse.ArgumentParser:
    parent = common_options()

    # =======================================================================
    # EXERCISE 4 — the root parser
    # =======================================================================
    #
    # Create argparse.ArgumentParser with, at minimum:
    #   prog="notes"            so usage lines say `notes`, not `notes.py`
    #   description=...         one sentence, shown at the top of --help
    #   epilog=...              worked examples, shown at the bottom
    #   formatter_class=argparse.RawDescriptionHelpFormatter
    #                           so your epilog's line breaks survive
    #
    # Then add --version with action="version" and
    # version=f"%(prog)s {__version__}". `%(prog)s` is argparse's own
    # substitution, not an f-string field — it expands to the prog name.
    #
    # Users expect -h, --help and --version to exist. Two of the three you get
    # for free; the third is one line. Not having them is the first thing that
    # makes a tool feel homemade.
    raise NotImplementedError("EXERCISE 4: build the root parser and add --version")

    # =======================================================================
    # EXERCISE 5 — subcommands and the dispatch pattern
    # =======================================================================
    #
    # subcommands = parser.add_subparsers(
    #     title="subcommands", dest="command", metavar="<command>", required=True,
    # )
    #
    # required=True is what makes bare `notes` exit 2 with a usage message
    # instead of crashing with AttributeError when nothing set args.func.
    #
    # Then, for `add`:
    #
    #   add = subcommands.add_parser("add", parents=[parent],
    #                                help="add one note",
    #                                description="...")
    #   add.add_argument("text", help="the note text, or '-' to read stdin")
    #   add.add_argument("-t", "--tag", action="append", type=tag_name,
    #                    metavar="TAG", help="...")
    #   add.add_argument("--on", type=iso_date, metavar="YYYY-MM-DD", help="...")
    #   add.add_argument("--dry-run", action="store_true", help="...")
    #   add.set_defaults(func=cmd_add, parser=add)
    #
    # That last line is the whole dispatch pattern, and it is the single most
    # useful technique in this lesson. set_defaults stores arbitrary values on
    # the resulting namespace, so after parsing, `args.func` IS the right
    # handler. main() calls it without a single if-statement about which
    # subcommand ran. Storing `parser=add` as well gives the handler access to
    # its own parser so it can call parser.error() — which is how EXERCISE 7
    # reports a usage problem it could only detect at run time.
    #
    # Note also: `--dry-run` on the command line becomes `args.dry_run`.
    # argparse replaces dashes with underscores, because a dash is not legal
    # in a Python identifier.

    # =======================================================================
    # EXERCISE 6 — the remaining four subcommands
    # =======================================================================
    #
    #   list    --format {table,json} (default "table"), -t/--tag (append,
    #           type=tag_name), --since (type=iso_date),
    #           -n/--limit (type=positive_int)     -> cmd_list
    #   search  positional `pattern`; -i/--ignore-case (store_true);
    #           --format {table,json}              -> cmd_search
    #   export  --format {json,csv} (default "json")  -> cmd_export
    #   remove  positional `ids` with nargs="+" and type=positive_int;
    #           --dry-run (store_true)             -> cmd_remove
    #
    # Every one takes parents=[parent] and ends with set_defaults(func=...,
    # parser=...).
    #
    # `choices=` is worth pausing on: it validates, it prints the legal values
    # in the usage line, and a wrong value exits 2 with a message listing what
    # was allowed. Three jobs, one keyword.
    #
    # nargs="+" means one or more, collected into a list — so
    # `notes remove 2 5 9` deletes three notes with no extra parsing.
    #
    # Finally: return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse an EXPLICIT argument list.

    Defaulting to None (which argparse turns into sys.argv[1:]) keeps the real
    program convenient, while every test passes its own list and never has to
    monkey-patch a global. This is Day 74's injection argument, applied to the
    command line.
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
        return 0
    except KeyboardInterrupt:
        streams.stderr.write("notes: interrupted\n")
        return 130


if __name__ == "__main__":
    sys.exit(main())
