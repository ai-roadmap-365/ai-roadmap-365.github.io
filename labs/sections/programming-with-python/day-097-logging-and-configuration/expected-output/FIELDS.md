# What must match, and what may differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16: macOS 26.5.2 (Apple Silicon, arm64), Python 3.14.0,
bash 3.2.57. Nothing was edited by hand afterwards.

Two files are captured with one deliberate substitution, made by the scripts
themselves and not by an editor: `logging-architecture.txt` and
`structured-logging.txt` print rendered tracebacks, and a rendered traceback
contains the absolute path of the file it came from. Both scripts replace this
lab's directory with the literal text `<lab>` **before printing**. The
assertions in `tests/run_tests.sh` run against the unmodified text.

## Must match exactly, on any machine

| Value | Where | Must be |
| --- | --- | --- |
| Harness total | `test-run.txt` | `86 checks, 0 failure(s).`, exit 0 |
| Starter before | `starter-progress.txt` | `0 of 12 exercises complete.`, exit 1 |
| Reference answers | `starter-progress.txt` | `12 of 12 exercises complete.`, exit 0 |
| The two-level trap | `logging-architecture.txt` §B | 3 calls made, exactly 1 line emitted, and it is the warning |
| Propagation | `logging-architecture.txt` §C | 1 call produces 2 lines; each fix reduces it to 1 |
| Lazy against eager | `logging-architecture.txt` §E | `0 renders` and `1000 renders` |
| Level numbers | `logging-architecture.txt` §F | DEBUG 10, INFO 20, WARNING 30, ERROR 40, CRITICAL 50 |
| Records kept | `structured-logging.txt` §1 | 125 across two batches; `{'INFO': 4, 'WARNING': 1, 'ERROR': 1}` |
| Filter on the handler | `structured-logging.txt` §2 | the secret appears in the message, the args, the nested dict and the list — and is redacted in all four |
| The traceback hole | `structured-logging.txt` §2 | `the secret survives inside the traceback field: True` |
| The formatter fix | `structured-logging.txt` §3 | `the secret appears anywhere in that output: False` |
| The filter-placement hole | `structured-logging.txt` §2b | direct line redacted, **child's line leaks** |
| Four layers | `config-resolver.txt` §1 | `32` default, `64` file, `128` environment, `256` flag |
| Provenance | `config-resolver.txt` §2 | 7 settings, 5 distinct sources, `api_key` shown as `***redacted***` |
| The bool trap | `config-resolver.txt` §3 | `bool("false") -> True` |
| Missing against empty | `config-resolver.txt` §4 | three distinct sources, the middle one `env:APP_MODEL_NAME (set but empty)` |
| Startup validation | `config-resolver.txt` §5 | 3 problems, each naming the setting and its source |
| Rotation | `dictconfig-rotation.txt` §2 | `app.log` plus `app.log.1`, `.2`, `.3` — four generations, never five |
| Timed rotation | `dictconfig-rotation.txt` §2 | `files after one rollover: 2` |
| Level change | `dictconfig-rotation.txt` §3 | 3 lines at DEBUG, 2 at INFO, 1 at WARNING |
| The manifest | `run-manifest.txt` | 6 JSON events, one `run_id`, `"api_key": "***redacted***"` |
| Determinism | `run-manifest.txt` | seed 7 gives final loss `0.506509`, every time, on every machine |

## Expected to differ on your machine

- **Every `ts` field, and the `%H:%M:%S` stamps in `dictconfig-rotation.txt`.**
  They are real timestamps from the moment of capture. The tests assert the
  *shape* of `ts` — 24 characters, ISO 8601 UTC to milliseconds, ending `Z` —
  and that the values sort into the order the events happened. They never
  assert a particular instant.
- **The line numbers inside the captured tracebacks** in
  `logging-architecture.txt` and `structured-logging.txt`. They are the real
  line numbers of the file they came from and move if the file is edited. The
  tests assert that a traceback is present, that it names the exception type
  and that it names the failing call — never a line number.
- **`daily.log.2026-08-16`** in `dictconfig-rotation.txt`. The suffix
  `TimedRotatingFileHandler` writes is the date the rolled file covers, so it
  is the date you run it. The test asserts the file *count* after one
  rollover, not the name.
- **The Python version banner** in `test-run.txt` and
  `starter-progress.txt`. It prints whatever `python3` you have. Anything from
  3.11 is fine; `tomllib` arrived in 3.11 and the suite checks for it first.
- **The wording of `NotImplementedError` messages** quoted in
  `starter-progress.txt` will change the moment you start editing the starter
  files, which is the point of them.

## Deliberately stable, and why

`06_run_manifest.py` takes its run id as a parameter with a fixed default and
seeds `random.Random` from configuration rather than from the clock or the
system entropy pool. The same seed therefore produces the same three loss
figures on any machine, which is what lets the test suite assert
`0.506509` at all.

That is not a testing convenience bolted on afterwards. It is the day's own
argument: a run whose inputs are not recorded cannot be repeated, and a run
that cannot be repeated is an anecdote. The seed is configuration, the
configuration is in the log, and the log is therefore enough to reproduce the
run — which the suite proves by running the program a second time from the
manifest's own values and comparing the final loss.

## Platform notes

- **Linux** — identical output, given Python 3.11 or newer.
- **Windows** — use WSL and follow the Linux path. `tests/run_tests.sh` and
  `starter/03_check.sh` are bash scripts and use `mktemp -d`; neither was run
  on native Windows here, so no capture is claimed for it. The Python files
  themselves have nothing platform-specific in them.
