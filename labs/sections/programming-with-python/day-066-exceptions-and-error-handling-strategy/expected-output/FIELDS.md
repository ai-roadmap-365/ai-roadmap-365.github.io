# Expected output — Day 066 lab

These are real captured runs from the authoring machine (macOS on Apple
Silicon, Python 3.14.0, bash 3.2.57, 2026-07-19). Every program here is
deterministic — no randomness, no network, no clock reading — so given the
same input it produces the same output and the same exit code on every
platform Python 3 runs on.

## Files

- `tracebacks.txt` — the three genuine tracebacks from
  `examples/raw_triage.py`: `FileNotFoundError`, `ValueError`, `KeyError`.
- `sample-run.txt` — a full session: the swallowing anti-pattern, the
  rebuilt `examples/triage.py` on clean and dirty input, a missing file,
  the resulting log, and the retry demo with its chained traceback.
- `log-sample.txt` — the log file `logging.exception` writes when a record
  is rejected, including the chained traceback.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished: `29 checks, 0 failure(s).`, exit 0.

## About the absolute paths

**Your tracebacks will not match these character for character, and they are
not supposed to.** A traceback prints the absolute path of every source file
in the stack, so the paths in your output are wherever you cloned this
repository. In the captured files the lab directory has been replaced with
the placeholder `<lab>` so the output stays readable; nothing else was
edited. What must match is the **exception type**, the **message**, the
**order of the frames**, and the **exit code**.

Two more differences you may legitimately see:

- The line numbers in tracebacks point into `examples/raw_triage.py` and
  `examples/triage.py`. If you edit those files, the numbers move.
- Python 3.11 and newer print `~~~^^^` caret lines under the exact failing
  sub-expression. On Python 3.8-3.10 those caret lines are absent and the
  traceback is otherwise identical. The tests never depend on them.

## Capture note: `python3 -u`

The captured sessions were run with `python3 -u` (unbuffered). In an
interactive terminal, standard output is line-buffered, so a program's
stdout and stderr interleave in the order the lines were written. When you
redirect output to a file, stdout becomes block-buffered and the two streams
can come out reordered. `-u` makes a redirected capture match what you see in
a terminal. Running the plain commands from the README in your own terminal
gives the same ordering as these files.

## Required behaviour on every platform

The handlers in `triage.py` must satisfy exactly:

| Call | Result |
| --- | --- |
| `parse_record('{"id": "P-1", "severity": 3}', 1)` | `{"id": "P-1", "severity": 3}` |
| `parse_record('{"id": "P-1"}', 7)` | raises `RecordError` mentioning `line 7` and `severity`; `__cause__` is a `KeyError` |
| `parse_record('{"id": "P-1", "severity": "high"}', 2)` | raises `RecordError`; `__cause__` is a `ValueError` (not a `JSONDecodeError`) |
| `parse_record('this is not json', 4)` | raises `RecordError` saying `not valid JSON`; `__cause__` is a `json.JSONDecodeError` |
| `parse_record('{"id": "P-1", "severity": 9}', 3)` | raises `RecordError` saying `outside 1-5`; `__cause__` is `None` |
| `band(1), band(3), band(5)` | `"immediate"`, `"urgent"`, `"routine"` |
| `summarize([...])` | a dict counting the three bands |
| `retry` on a callable that fails twice | succeeds on attempt 3; sleeps `0.05` then `0.10` seconds |
| `retry` on a callable that always fails | raises `DispatchError` whose `__cause__` is the last `ConnectionError` |
| `retry` on a callable raising `ValueError` | the `ValueError` propagates immediately, after one call |

The shell must satisfy exactly:

| Command | Output | Exit code |
| --- | --- | --- |
| `python3 examples/triage.py examples/samples/intake.jsonl` | `admitted 5 record(s), rejected 0`, `immediate  2` | 0 |
| `python3 examples/triage.py examples/samples/bad-severity.jsonl` | `rejected: line 2: severity is not a whole number` (stderr) | 0 |
| `python3 examples/triage.py examples/samples/missing-field.jsonl` | `rejected: line 2: missing field 'severity'` (stderr) | 0 |
| `python3 examples/triage.py examples/samples/no-such-file.jsonl` | `error: no such intake file: ...` (stderr) | 1 |
| `python3 examples/triage.py` | `usage: python3 triage.py <records.jsonl> [logfile]` (stderr) | 2 |
| `python3 examples/swallowing.py examples/samples/no-such-file.jsonl` | `total severity: 0`, `done` — the failure hidden | 0 |

And the log file written by `logging.exception` must contain, for a rejected
record: the line `ERROR: rejected record on line 2`, a
`Traceback (most recent call last):` block, the chaining sentence
`The above exception was the direct cause of the following exception`, and
the original `ValueError: invalid literal for int()`.

## Platform notes

- macOS and Linux behave identically here; the only difference is the shell
  prompt shown before each command in the captures.
- `mktemp -t NAME` is used by the test runner. macOS and GNU coreutils spell
  its template rules slightly differently, so the runner passes a template
  form (`triage-test.XXXXXX`) that both accept.
- The exact wording of `FileNotFoundError`'s message
  (`[Errno 2] No such file or directory: ...`) comes from the operating
  system through Python's `OSError`, so it can differ on other platforms.
  The tests check the program's own message (`error: no such intake file`)
  and the exit code, never the OS wording.
- Windows: run everything inside WSL. Native Windows Python raises the same
  exceptions, but paths in tracebacks use backslashes and `bash` is not
  available for the test runner.
