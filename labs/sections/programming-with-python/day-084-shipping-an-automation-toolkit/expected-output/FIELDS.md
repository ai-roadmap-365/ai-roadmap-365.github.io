# What must be true, on any platform

The captures in this directory were taken on the authoring machine. Several
values in them are *expected* to differ on yours, and several are not. This
file separates the two, so you can tell a real failure from a cosmetic
difference.

## Values that will differ on your machine, and should

| Value | Why |
| --- | --- |
| The port in `http://127.0.0.1:<port>` | The fixture server binds port 0 and the operating system picks a free port. A different number every run is the design working |
| The eight-character `run_id` | A fresh random label per run, so a month of logs can be filtered down to one 03:00 run |
| Every `ts` field and every timestamp in `status` | Wall-clock time when you ran it |
| Absolute paths | Temporary directories are created with `mktemp -d`, whose names are random by design |
| The exact wall-clock gaps between retry lines | Backoff is 0.5s then 1.0s on the authoring machine; a busy machine may show a few milliseconds more |
| `NN passed in 0.NNs` | pytest's timing |

## Values that must be identical, everywhere

| Value | Required |
| --- | --- |
| First run, three configured sources | `new entries: 7` (3 from notes, 2 from links, 2 from papers) and `exit: 0` |
| Second run of the same command | `new entries: 0` and `exit: 0` — this is idempotence, and any other number is a bug |
| `--dry-run` | The state file's bytes are unchanged, the summary still reports what *would* have happened, and `exit: 0` |
| A run over `notes,broken,papers` | `sources: 2 ok, 1 failed, 3 total`, a `FAILED: broken:` line, and **exit code 3** |
| A run over `broken` alone | `exit: 1` |
| A run while the lock file exists | `exit: 3`, no state written |
| `feedkit --version` | `feedkit 1.0.0` |
| The `flaky` source | Succeeds on `attempt 3` after two 503s, and the summary line reads `retried: flaky succeeded on attempt 3` |
| A 401 or 404 | Never retried: the message ends `(not retryable)` and only one attempt appears in the log |
| The four precedence layers | `5 default`, then `10 file`, then `20 environment`, then `40 flag` |
| A misspelled key in the config file | Exit non-zero with `unknown setting in configuration file` |
| The token | Appears **zero** times in every log, the state file, and `--explain-config` output |
| `bash tests/run_tests.sh` | `52 checks, 0 failure(s).` and exit 0 |

## Platform differences

**macOS and Linux** behave identically for everything in this lab. `os.replace`
is atomic on both, `O_CREAT | O_EXCL` is honoured by both, and both ship a
`python3` new enough for `tomllib` (3.11+).

**Windows.** Use WSL and follow the Linux path. Three things differ on native
Windows and are worth knowing rather than discovering:

- A virtual environment puts its executables in `.venv\Scripts\`, not
  `.venv/bin/`, so the paths in every command here need adjusting.
- `tests/run_tests.sh` and the schedule references are POSIX. The Windows
  equivalent of cron is Task Scheduler, and its configuration is not shown
  here because none of it was run on the authoring machine and this course does
  not print output it did not produce.
- `os.replace` **is** atomic on Windows, so the state file's guarantee holds.
  The lock, however, behaves differently around open file handles; the code as
  written works, but the diagnostic messages assume POSIX process ids.

**A machine with no network at all.** Everything except the one-time
`pip install` works. That is deliberate: the tests never leave 127.0.0.1.
