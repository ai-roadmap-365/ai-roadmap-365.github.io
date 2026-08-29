# Troubleshooting — Day 081

## `ModuleNotFoundError: No module named 'runner'` (or `clock`, `joblock`, …)

The modules live beside each other in `examples/` with no package layout, so
they are importable only when that directory is on the path. `conftest.py`
does this for pytest, and Python does it automatically when you run a script
by path (`python3 examples/demo.py`). It does **not** happen if you start a
bare `python3` in the lab root and type `import runner`. Either run the
scripts as shown, or start your interpreter with
`PYTHONPATH=examples python3`.

## `pytest` is not found

Create the virtual environment and install the one dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Or point the runner at a pytest you already have:
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## `ModuleNotFoundError: No module named 'fcntl'`

You are on Windows. `fcntl` is POSIX-only. Run the lab under WSL. The Windows
equivalents are `msvcrt.locking` and named mutexes, and they behave
differently enough that this lab does not pretend to cover them.

## The job exits 75 and I did not start a second copy

Exit 75 means the lock was held. Two likely causes:

1. A previous run is genuinely still going — check with
   `pgrep -f examples/job.py`.
2. You are pointing two runs at the same `--lock-file` while one of them is
   deliberately holding it (this is what `examples/hold_lock.py` is for).

Note what exit 75 does **not** mean: it is not "the lock file exists". The
lock is `flock` on an open file descriptor, and the kernel drops it when the
holding process exits, however it exits. A leftover `daily-report.lock` file
on disk blocks nothing.

## The job exits 124 and I did not ask for a timeout

`job.py run` has a default `--timeout` of 60 seconds. Pass `--timeout 0` to
disable it. In real life, do not: a job with no time budget can hang for ever
holding the lock, which silently stops every later run.

## The timeout does not fire

Three known reasons, all honest limits of `SIGALRM`:

1. **You are not on the main thread.** `signal.signal` can only be called
   from the main thread of the main interpreter.
2. **The work is blocked inside a C library** that does not return to the
   interpreter. Python cannot raise into it.
3. **The work is a child process.** The alarm interrupts your process, not
   its children. Use `examples/supervise.py`, which runs the child in its own
   process group and kills the group.

## `--now` is rejected

`--now` needs an offset: `2026-07-20T02:30:00+00:00`, not
`2026-07-20T02:30:00`. A naive timestamp means "whatever this machine thinks
local time is", which is precisely the bug the lesson is about, so the program
refuses it rather than guessing.

## The report is empty

`generate_daily_report` reports on the day **before** `--now` by default,
because that is what a nightly job does. `examples/data/readings.csv` holds
data for 2026-07-17 to 2026-07-20 only. Either pass `--date`, or use a
`--now` inside that window.

## The second run says `skipped` and I wanted it to rerun

That is idempotence working. To force a rerun, delete the output file for
that date; the job treats the file's existence as "already done". If you want
a rerun to be possible without deleting anything, that is a different design
(a version or run-id in the filename) and is one of the extension exercises.

## `run_tests.sh` reports a failure in section 4 or 5

Those two sections start real processes. If a previous interrupted run left
something behind, `pgrep -f hold_lock.py` will show it; kill it and rerun.
The runner's own `trap ... EXIT` cleans up after itself, so this should only
happen if you killed the runner with SIGKILL.

## `crontab: no crontab for <user>` while running the tests

That is the expected, healthy answer, and section 8 treats it as a pass — it
means you have no crontab, so this lab certainly did not add anything to it.

## The generated files are full of `/opt/reports` and `/usr/bin/python3`

They are placeholders, on purpose, so that the committed examples contain no
path from any real machine. Pass `--project-dir` and `--python` to generate a
version for a machine you actually intend to schedule on — and read the file
before you install it.

## `pytest starter` says `1 passed, 8 skipped`

That is the shipped state. Each exercise is skipped until you delete its
`@pytest.mark.skip` line in `starter/test_myjob.py`.

## The lesson's `sched` example seems to finish instantly

It does, and that is the point. `sched.scheduler` takes its time source and
delay function as arguments, so a fake clock makes a six-hour schedule run in
microseconds. Nothing was waited for.
