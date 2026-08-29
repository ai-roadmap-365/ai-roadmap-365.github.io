# Expected output — Day 056 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The tool is deterministic:
given the same store and the same commands, it produces the same output and
the same exit codes on every platform Python 3 runs on.

## Files

- `sample-run.txt` — the reference CLI driven through a full session on a
  scratch `demo.json`: list an empty store, add two records, list, find
  (matching and not), delete (present and absent), a rejected bad email,
  the JSON left on disk, and a `python3 -c` import check.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (19 checks, 0 failures). Absolute paths are shown as
  `<repo>`; on your machine they are your real repository path.

## Required behaviour on every platform

A correct CLI must, for a fresh store, produce exactly:

| Command (with `--store demo.json`) | Output (stream) | Exit code |
| --- | --- | --- |
| `list` (empty store) | `no records` (stdout) | 0 |
| `add --name "Ada Lovelace" --email ada@example.com` | `added #1: Ada Lovelace <ada@example.com>` (stdout) | 0 |
| `add --name "Alan Turing" --email alan@example.com` | `added #2: Alan Turing <alan@example.com>` (stdout) | 0 |
| `list` | `#1: ...` then `#2: ...` (stdout) | 0 |
| `find --field name --query ada` | `#1: Ada Lovelace <ada@example.com>` (stdout) | 0 |
| `find --field name --query zoe` | `no records match name='zoe'` (stderr) | 1 |
| `delete --id 1` | `deleted #1` (stdout) | 0 |
| `delete --id 99` | `error: no record with id 99` (stderr) | 1 |
| `add --name "Bad" --email noatsign` | `error: 'noatsign' is not a valid email (needs '@')` (stderr) | 1 |
| `add --name "  " --email x@example.com` | `error: name must not be empty` (stderr) | 1 |

Argparse itself handles usage errors before your code runs: a missing
required option (for example `add --name X` with no `--email`) prints a
usage line to stderr and exits with code **2** — argparse's own convention,
distinct from the code 1 this program uses for its own validation and data
errors.

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- The JSON store is written with a two-space indent and a trailing newline,
  so it is human-readable and diffs cleanly under version control.
- `mktemp` is used by the test runner to make a throwaway store. On Linux
  `mktemp -t records-test.XXXXXX` behaves the same as on macOS; if your
  `mktemp` differs, the test still works because the store path is quoted
  and removed on exit.
