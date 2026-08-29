# Expected output — Day 063 lab

These are real captured runs from the authoring machine (macOS, Apple
Silicon, Python 3.14.0, bash 3.2, 2026-07-13). The program is
deterministic: given the same input it produces the same output and the
same exit code on every platform Python 3 runs on.

## Files

- `sample-run.txt` — the reference tool driven through a full session:
  summarize numbers from stdin, summarize numbers from a file, a rejected
  non-numeric token, rejected empty input, and one direct call into the
  pure core (`summary_core.summarize(...)`) to show the core works with no
  I/O at all.
- `test-run.txt` — a full run of `bash tests/run_tests.sh` with the starter
  still unfinished (15 checks, 0 failures). Absolute paths are shown as
  `<repo>`; on your machine they are your real repository path.

## Required behaviour on every platform

The pure core (`summary_core.py`) must satisfy exactly:

| Call | Result |
| --- | --- |
| `parse_numbers("1, 2\n3\t4")` | `[1.0, 2.0, 3.0, 4.0]` |
| `parse_numbers("   ")` | `[]` |
| `parse_numbers("1 two 3")` | raises `ValueError` mentioning `'two'` |
| `summarize([2, 4, 6, 8])` | `{"count": 4, "total": 20, "mean": 5.0, "minimum": 2, "maximum": 8, "above_mean": 2}` |
| `summarize([])` | raises `ValueError` (cannot summarize an empty list) |
| `format_summary(summarize([10, 20, 30]))` | six aligned lines; includes `count      3`, `mean       20.00`, `above mean 1` |

The shell (`summary.py`) must satisfy exactly, for a fresh input:

| Command | Output (stream) | Exit code |
| --- | --- | --- |
| `echo "10 20 30" \| python3 summary.py` | the six-line summary, `mean       20.00` (stdout) | 0 |
| `python3 summary.py numbers.txt` (valid file) | the six-line summary (stdout) | 0 |
| `echo "1 two 3" \| python3 summary.py` | `error: 'two' is not a number` (stderr) | 1 |
| `printf "" \| python3 summary.py` | `error: cannot summarize an empty list of numbers` (stderr) | 1 |
| `python3 summary.py missing.txt` | `error: [Errno 2] No such file or directory: ...` (stderr) | 1 |

## Platform notes

- The only visible difference between platforms is the shell prompt (`$`)
  shown before each command; the program's own output is identical.
- The exact text of the missing-file error (`[Errno 2] No such file or
  directory: ...`) is produced by the operating system through Python's
  `OSError`, so the wording can differ slightly between platforms and
  Python versions. The tests therefore check only for the `error:` prefix
  and exit code 1 on that case, not the full OS message.
- Floating-point formatting uses `:.2f`, which rounds to two decimals
  identically across platforms; integer statistics (count, above mean)
  print with no decimals.
