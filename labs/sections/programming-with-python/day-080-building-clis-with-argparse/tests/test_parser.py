"""In-process tests: the parser and the handlers, with no subprocess at all.

Read this file alongside `run_tests.sh`. The two prove different things:

  * run_tests.sh launches the real program and checks exit codes and the two
    output streams — the contract a SHELL sees;
  * this file calls parse_args(argv) and main(argv, streams) directly — the
    contract PYTHON sees.

You need both. A subprocess test is the only honest way to check an exit code
or stream separation. An in-process test is a hundred times faster, gives a
real traceback when it fails, and can assert on the parsed Namespace, which a
subprocess can never see.

That both are possible at all comes down to two design decisions in notes.py:
`parse_args` takes an explicit argument list instead of reading sys.argv, and
`main` takes a Streams object instead of importing sys.stdout. Day 74 called
that injecting the boundary; this is the same idea, one layer out.
"""

from __future__ import annotations

import argparse
import io
import json

import pytest


# ---------------------------------------------------------------------------
# parse_args: the parser as a pure function from a list of strings
# ---------------------------------------------------------------------------


def test_parse_args_takes_an_explicit_list(notes_module):
    args = notes_module.parse_args(["add", "hello"])
    assert args.command == "add"
    assert args.text == "hello"


def test_the_subcommand_binds_its_handler(notes_module):
    """set_defaults(func=...) is the dispatch: no if-statement anywhere."""
    for name, handler in [
        ("add", "cmd_add"),
        ("list", "cmd_list"),
        ("search", "cmd_search"),
        ("export", "cmd_export"),
        ("remove", "cmd_remove"),
    ]:
        argv = {"add": ["add", "x"], "search": ["search", "x"], "remove": ["remove", "1"]}.get(
            name, [name]
        )
        args = notes_module.parse_args(argv)
        assert args.func is getattr(notes_module, handler)


def test_dashes_become_underscores(notes_module):
    args = notes_module.parse_args(["remove", "3", "--dry-run"])
    assert args.dry_run is True
    assert args.ids == [3]


def test_nargs_plus_collects_a_list(notes_module):
    args = notes_module.parse_args(["remove", "2", "5", "9"])
    assert args.ids == [2, 5, 9]


def test_action_append_collects_repeats(notes_module):
    args = notes_module.parse_args(["add", "x", "-t", "one", "--tag", "two"])
    assert args.tag == ["one", "two"]


def test_defaults_apply_when_the_option_is_absent(notes_module):
    args = notes_module.parse_args(["list"])
    assert args.format == "table"
    assert args.store is None  # None, not "notes.json": see store_path()
    assert args.verbose is False and args.quiet is False


def test_type_conversion_happens_during_parsing(notes_module):
    from datetime import date

    args = notes_module.parse_args(["add", "x", "--on", "2026-03-01"])
    assert args.on == date(2026, 3, 1)
    assert isinstance(args.on, date)


def test_a_double_dash_ends_option_parsing(notes_module):
    args = notes_module.parse_args(["add", "--", "--not-a-flag"])
    assert args.text == "--not-a-flag"


@pytest.mark.parametrize(
    "argv",
    [
        [],  # no subcommand at all
        ["frobnicate"],  # unknown subcommand
        ["add"],  # missing required positional
        ["add", "x", "--on", "2026-13-01"],  # custom type rejects the value
        ["add", "x", "--tag", "two words"],  # custom type rejects the value
        ["list", "--format", "yaml"],  # not in choices
        ["list", "-n", "0"],  # positive_int rejects it
        ["list", "-v", "-q"],  # mutually exclusive
        ["remove"],  # nargs="+" needs at least one
        ["add", "x", "--tagg", "typo"],  # unknown option is refused, not ignored
    ],
)
def test_usage_errors_raise_systemexit_with_code_2(notes_module, argv):
    """argparse's contract: a usage error is SystemExit(2), never a traceback."""
    with pytest.raises(SystemExit) as caught:
        notes_module.parse_args(argv)
    assert caught.value.code == 2


def test_help_and_version_exit_zero(notes_module):
    for argv in (["--help"], ["--version"], ["add", "--help"]):
        with pytest.raises(SystemExit) as caught:
            notes_module.parse_args(argv)
        assert caught.value.code == 0


# ---------------------------------------------------------------------------
# The custom types, tested on their own — they are just functions
# ---------------------------------------------------------------------------


def test_iso_date_converts(notes_module):
    from datetime import date

    assert notes_module.iso_date("2026-03-01") == date(2026, 3, 1)


@pytest.mark.parametrize("bad", ["2026-13-01", "tomorrow", "01-03-2026", "", "2026-02-30"])
def test_iso_date_raises_argument_type_error(notes_module, bad):
    with pytest.raises(argparse.ArgumentTypeError):
        notes_module.iso_date(bad)


@pytest.mark.parametrize("bad", ["0", "-2", "abc", "1.5"])
def test_positive_int_raises_argument_type_error(notes_module, bad):
    with pytest.raises(argparse.ArgumentTypeError):
        notes_module.positive_int(bad)


def test_the_error_message_names_the_offending_value(notes_module):
    with pytest.raises(argparse.ArgumentTypeError) as caught:
        notes_module.iso_date("2026-13-01")
    assert "2026-13-01" in str(caught.value)


# ---------------------------------------------------------------------------
# main() driven with injected streams — no process, no real terminal
# ---------------------------------------------------------------------------


def run(notes_module, argv, stdin_text=""):
    """Call main() with string streams and return (code, stdout, stderr)."""
    streams = notes_module.Streams(
        stdin=io.StringIO(stdin_text), stdout=io.StringIO(), stderr=io.StringIO()
    )
    code = notes_module.main(argv, streams)
    return code, streams.stdout.getvalue(), streams.stderr.getvalue()


def test_add_then_list_round_trips(notes_module, store):
    code, out, err = run(notes_module, ["add", "buy milk", "--on", "2026-03-01", "--store", str(store)])
    assert (code, out, err) == (0, "added note 1\n", "")

    code, out, err = run(notes_module, ["list", "--format", "json", "--store", str(store)])
    assert code == 0
    assert json.loads(out) == [{"date": "2026-03-01", "id": 1, "tags": [], "text": "buy milk"}]


def test_stdin_is_read_when_the_text_is_a_dash(notes_module, store):
    code, out, _ = run(
        notes_module,
        ["add", "-", "--on", "2026-03-02", "--store", str(store)],
        stdin_text="piped in\n",
    )
    assert code == 0 and out == "added note 1\n"
    assert json.loads(store.read_text())["notes"][0]["text"] == "piped in"


def test_results_go_to_stdout_and_diagnostics_to_stderr(notes_module, store):
    run(notes_module, ["add", "one", "--on", "2026-03-01", "--store", str(store)])
    code, out, err = run(notes_module, ["list", "--format", "json", "-v", "--store", str(store)])
    assert code == 0
    assert json.loads(out)  # the RESULT parses as JSON, undisturbed...
    assert "1 note(s) from" in err  # ...because the chatter went elsewhere


def test_quiet_silences_success_but_not_the_work(notes_module, store):
    code, out, err = run(
        notes_module, ["add", "silent", "--on", "2026-03-01", "-q", "--store", str(store)]
    )
    assert (code, out, err) == (0, "", "")
    assert json.loads(store.read_text())["notes"][0]["text"] == "silent"


def test_a_refusal_exits_1_and_says_so_on_stderr(notes_module, store):
    store.write_text('{"version": 1, "notes": []}\n')
    code, out, err = run(notes_module, ["remove", "99", "--store", str(store)])
    assert code == 1
    assert out == ""
    assert "no note with id 99" in err


def test_search_exits_1_when_nothing_matched(notes_module, store):
    run(notes_module, ["add", "hello", "--on", "2026-03-01", "--store", str(store)])
    assert run(notes_module, ["search", "hello", "--store", str(store)])[0] == 0
    assert run(notes_module, ["search", "kangaroo", "--store", str(store)])[0] == 1


def test_ignore_case_changes_the_match(notes_module, store):
    run(notes_module, ["add", "Hello", "--on", "2026-03-01", "--store", str(store)])
    assert run(notes_module, ["search", "hello", "--store", str(store)])[0] == 1
    assert run(notes_module, ["search", "hello", "-i", "--store", str(store)])[0] == 0


def test_dry_run_leaves_the_store_byte_identical(notes_module, store):
    run(notes_module, ["add", "keep me", "--on", "2026-03-01", "--store", str(store)])
    before = store.read_bytes()

    code, out, err = run(notes_module, ["remove", "1", "--dry-run", "--store", str(store)])

    assert code == 0
    assert out == "would remove note 1\n"  # the RESULT: pipeable ids
    assert "was not touched" in err  # the DIAGNOSTIC
    assert store.read_bytes() == before  # the promise, actually checked


def test_a_real_remove_does_change_the_store(notes_module, store):
    """The control for the test above: without --dry-run, the bytes move."""
    run(notes_module, ["add", "keep me", "--on", "2026-03-01", "--store", str(store)])
    before = store.read_bytes()
    assert run(notes_module, ["remove", "1", "--store", str(store)])[0] == 0
    assert store.read_bytes() != before


def test_store_precedence_flag_beats_environment(notes_module, tmp_path, monkeypatch):
    from_flag = tmp_path / "flag.json"
    from_env = tmp_path / "env.json"
    monkeypatch.setenv("NOTES_STORE", str(from_env))

    run(notes_module, ["add", "a", "--on", "2026-03-01", "--store", str(from_flag)])
    assert from_flag.exists() and not from_env.exists()

    run(notes_module, ["add", "b", "--on", "2026-03-01"])
    assert from_env.exists()


def test_export_csv_has_a_header_and_one_row_per_note(notes_module, store):
    run(notes_module, ["add", "one", "-t", "x", "--on", "2026-03-01", "--store", str(store)])
    run(notes_module, ["add", "two", "--on", "2026-03-02", "--store", str(store)])
    code, out, _ = run(notes_module, ["export", "--format", "csv", "--store", str(store)])
    assert code == 0
    assert out.splitlines() == [
        "id,date,tags,text",
        "1,2026-03-01,x,one",
        "2,2026-03-02,,two",
    ]


def test_a_corrupt_store_is_a_refusal_not_a_traceback(notes_module, store):
    store.write_text("{ this is not json")
    code, out, err = run(notes_module, ["list", "--store", str(store)])
    assert code == 1 and out == "" and "not valid JSON" in err
