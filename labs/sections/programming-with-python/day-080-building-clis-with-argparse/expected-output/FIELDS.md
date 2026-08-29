# Expected output — Day 080 lab

These are real captured runs from the authoring machine (macOS 26.5.1, Apple
Silicon, Python 3.14.0, pytest 9.1.1, bash 3.2.57, 2026-07-19). Every date the
tool records comes from an explicit `--on`, and nothing here reads the
network or a random number, so the same commands produce the same bytes on
any machine with Python 3.

## Files

- `sample-run.txt` — a full session with the reference tool: adding notes by
  argument and through a pipe, listing as a table and as JSON, searching,
  exporting CSV, a `--dry-run` with the store's SHA-256 hash printed before
  and after, the real removal, the two output streams redirected to separate
  files, and five different failures with their exit codes.
- `help-output.txt` — every help screen the tool produces: the root `--help`,
  all five subcommand `--help` screens, and `--version`. Read this one as a
  document, not as output: it is the tool's entire user manual, generated
  from the same declarations that do the parsing.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  exercises unfinished: 76 checks, 0 failures, exit 0. One line in it varies
  between runs — the check that reports `42 passed in 0.07s` quotes pytest's
  own timing, which is a measurement and will differ by a few hundredths of a
  second on your machine. Every other line is byte-stable.

## The contract your finished tool must satisfy

### Exit codes

| Command | Exit code | Why |
| --- | --- | --- |
| `notes --help`, `notes add --help`, `notes --version` | 0 | asking for help is not an error |
| a command that did its job | 0 | the only success code |
| `notes search kangaroo` with no match | 1 | grep's convention: nothing found, nothing wrong |
| `notes remove 99` when 99 does not exist | 1 | a refusal the tool understood |
| a store that is not valid JSON | 1 | a refusal, not a traceback |
| `notes` with no subcommand | 2 | usage error |
| `notes frobnicate` | 2 | usage error |
| `notes add x --on 2026-13-01` | 2 | the custom `type=` rejected the value |
| `notes list --format yaml` | 2 | outside `choices=` |
| `notes list -v -q` | 2 | mutually exclusive options |
| `notes add x --tagg typo` | 2 | an unknown option is refused, never ignored |

### Which stream each thing goes to

| Output | Stream | Reason |
| --- | --- | --- |
| the note ids from `remove --dry-run` | standard output | it is a RESULT; a person can pipe it |
| `list`, `search`, `export` output | standard output | the result again |
| `added note 3`, `removed note 2` | standard output | a short confirmation the user asked for |
| every `-v` explanation | standard error | a diagnostic; it must not pollute a pipe |
| the `dry run: ... was not touched` summary | standard error | a diagnostic |
| every error message | standard error | so `2>/dev/null` still leaves the result usable |
| argparse's own usage errors | standard error | argparse does this for you, and it is right |

The single check that proves this was implemented rather than approximated:
`notes add x --on 2026-13-01 >out.txt 2>err.txt` must leave `out.txt` **empty**
and `err.txt` **non-empty**. A program that printed its errors with a bare
`print()` passes a `2>&1` check and fails this one.

### The dry-run promise

| Step | Required |
| --- | --- |
| `shasum -a 256 notes.json` before | some hash H |
| `notes remove 2 --dry-run` | exits 0, prints `would remove note 2` on stdout |
| `shasum -a 256 notes.json` after | **exactly H** |
| `notes remove 99 --dry-run` | still exits 1 — a dry run validates for real |
| `notes remove 2` (no `--dry-run`) | exits 0, and the hash **changes** |

That last row is the control. Without it, "the file did not change" would also
be satisfied by a tool that never writes anything.

### Configuration precedence

| Command | Store used |
| --- | --- |
| `notes add x --store a.json` with `NOTES_STORE=b.json` set | `a.json` — the flag wins |
| `notes add x` with `NOTES_STORE=b.json` set | `b.json` — the environment |
| `notes add x` with nothing set | `./notes.json` — the built-in default |

### Parser behaviour, in-process

| Call | Result |
| --- | --- |
| `parse_args(["add", "hello"])` | `args.command == "add"`, `args.text == "hello"` |
| `parse_args(["remove", "3", "--dry-run"])` | `args.dry_run is True`, `args.ids == [3]` |
| `parse_args(["remove", "2", "5", "9"])` | `args.ids == [2, 5, 9]` — `nargs="+"` |
| `parse_args(["add", "x", "-t", "a", "--tag", "b"])` | `args.tag == ["a", "b"]` — `action="append"` |
| `parse_args(["add", "x", "--on", "2026-03-01"])` | `args.on` is a `datetime.date`, already converted |
| `parse_args(["add", "--", "--not-a-flag"])` | `args.text == "--not-a-flag"` |
| `parse_args(["list"]).store` | `None` — not `"notes.json"`; see `store_path()` |
| `parse_args(["list"]).func` | `is cmd_list` — the `set_defaults` dispatch |
| any usage error | raises `SystemExit` with `code == 2` |
| `parse_args(["--help"])` | raises `SystemExit` with `code == 0` |
| `iso_date("2026-13-01")` | raises `argparse.ArgumentTypeError` naming the value |
| `positive_int("0")` | raises `argparse.ArgumentTypeError` saying "at least 1" |

## Platform notes

- macOS and Linux produce identical bytes. The only thing that differs
  between the two in `sample-run.txt` is the temporary directory the capture
  ran in, and that never appears in the output.
- `shasum -a 256` is the macOS spelling. On most Linux distributions the
  command is `sha256sum`; the hash is the same either way. The test suite
  does not depend on either — it hashes the file with Python's `hashlib`, so
  it works everywhere.
- **Colour.** From Python 3.13 argparse colourizes its help and usage output
  when it detects a terminal. Every capture in this directory was made with
  output redirected to a file, so no colour codes appear in them. Run the same
  commands interactively on a recent Python and the *text* is identical while
  the terminal shows it in colour. Nothing in the test suite depends on
  colour, because everything it inspects is captured to a file.
- On Windows, run everything inside WSL. Two things genuinely differ on a
  native Windows console: `python3` may be spelled `python`, and the em dash
  in the suite's banner needs a UTF-8 terminal. Exit codes, stream
  separation and the JSON bytes are unaffected.
- The suite writes only inside a directory made with `mktemp -d` and removes
  it in a `trap`, so even a failed run leaves nothing behind.
