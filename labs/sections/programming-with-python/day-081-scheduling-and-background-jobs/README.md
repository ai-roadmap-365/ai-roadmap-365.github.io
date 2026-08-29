# Day 081 lab — A Job That Survives Being Ignored

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Scheduling and Background Jobs
- **Day number:** 81 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-081-scheduling-and-background-jobs
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-081-scheduling-and-background-jobs` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 81 of 365, and the companion to the lesson "Scheduling and Background
Jobs".

**Read this first. This lab installs nothing into any real scheduler.**

Not your crontab. Not launchd. Not systemd. Nothing is added to your machine
that outlives the commands you type, and no background process is left running
when you finish. The lab *generates* schedule files, *shows* you the install
command, and *runs the job by hand* — because a lesson that quietly schedules
something on your computer would be a lesson you could not undo. Section 8 of
the test suite asserts all of that directly: it reads your real crontab, your
`~/Library/LaunchAgents` and your `~/.config/systemd/user` and fails if this
lab's job appears in any of them, and it checks that no process from the lab
survived.

With that established: scheduling something is easy. A crontab line is five
numbers and a command. **Operating** a scheduled job is hard, and that is what
you build today.

You are given a small daily report job — the kind of thing Days 78, 79 and 80
produced and that you would obviously want to run every night — and you give
it the five properties that decide whether it can be trusted while nobody is
watching:

1. **Idempotence.** Run it twice, get one result. Not two, and not a doubled
   one. Every retry, every catch-up run, and every operator typing the command
   again means "run it twice".
2. **A lock.** A job that takes longer than its interval will one day be
   started while the previous copy is still going. The second copy must refuse
   to start, with a distinct exit code, having done nothing.
3. **A timeout.** A job that hangs holds the lock for ever, which silently
   stops every later run. A hang is worse than a crash, because a crash is
   reported.
4. **A log you can debug from.** You will not be watching. One structured
   line per run — run id, status, duration, exit code — is the entire record
   of what happened.
5. **A watchdog.** Alerting on failure catches the easy case. The case that
   bites is the job that stopped running altogether, which produces no error
   because it produces nothing at all. The fix is a dead man's switch: alert
   on the **absence of a success**.

Every one of those is testable in milliseconds, and the reason is Day 74. The
clock is a boundary, so it arrives as a parameter. `--now` freezes it, which
is how "what does this report the morning after the job dies?" and "what does
a 02:30 job do on the day the clocks change?" become assertions instead of
things you wait two days to find out.

## Learning objectives

- Explain why a `time.sleep` loop drifts, measure the drift exactly, and fix
  it by sleeping to a deadline instead of for a duration.
- Drive `sched.scheduler` with an injected time source so a six-hour schedule
  runs in microseconds, and say why an in-process scheduler dies with the
  process.
- Read and write a five-field cron expression, including the day-of-month and
  day-of-week fields, which cron ORs rather than ANDs when both are set.
- Describe what environment a cron job actually gets, and write the four lines
  that compensate for it.
- Read a launchd plist and a systemd `.service`/`.timer` pair field by field,
  and name the two things systemd timers give you that cron does not.
- Make a job idempotent with an output-name key and an atomic write, and prove
  running it twice leaves one result.
- Stop overlapping runs with `fcntl.flock`, and explain why "if the lock file
  exists, exit" is not the same thing.
- Bound a job with `SIGALRM`, know that mechanism's three limits, and use a
  supervised child process with `os.killpg` when they matter.
- Choose exit codes that mean something, and log enough context to debug a
  failure you did not watch.
- Alert on silence with a heartbeat file, and choose a staleness budget.
- Explain why UTC is the answer to daylight saving, with the 23-hour and
  25-hour days to prove it.

## Prerequisites

- Day 74: the clock as an injected boundary. Today is that lesson's largest
  application — nothing here would be testable without it.
- Day 80: `argparse`, subcommands, and exit codes as a public interface.
- Days 64 to 66: reading and writing files, JSON and CSV, and exception
  strategy.
- Day 69: dataclasses and type hints, used throughout.
- Days 71 to 73: pytest, fixtures, parametrization, and reading a failure.
- Day 60: the standard library tour — `sched`, `signal` and `subprocess` all
  appeared there.
- Day 43: creating a virtual environment.

## Supported operating systems

- **macOS** — fully supported (captured on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, pytest 9.1.1, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.10+ and bash).
  The systemd sections are most relevant here.
- **Windows** — use WSL and follow the Linux path. `fcntl` is POSIX-only, so
  the lock will not import on native Windows; the Windows equivalents are
  `msvcrt.locking` and named mutexes, and this lab does not pretend to cover
  them. Task Scheduler is the Windows counterpart of cron and is described in
  the lesson.

## Hardware requirements

Any computer that runs Python 3. The suite finishes in a few seconds, writes
a few kilobytes into temporary directories, and needs no network, no GPU and
no special memory.

## Required software

- `python3` (3.10 or newer; captured on 3.14.0).
- `pytest` 9.1.1 — the only dependency, installed below.
- `bash` for the test runner (preinstalled on macOS and Linux).
- `sched`, `signal`, `fcntl`, `subprocess`, `datetime`, `zoneinfo`, `json`,
  `csv`, `argparse` — all standard library, already present, nothing to
  install.

## Free and open-source options

Everything here is free and open source: Python and its standard library, bash,
and pytest (MIT — see [`requirements/README.md`](requirements/README.md)). cron,
launchd and systemd all ship with the operating system at no cost. No account,
no API key, no purchase, and no network access at any point after the one-time
pytest install.

The lesson also describes `schedule`, `APScheduler`, `croniter` and Celery.
All are free and open source, **none is installed here**, and no code in this
lab imports any of them.

## Installation

```bash
cd labs/sections/programming-with-python/day-081-scheduling-and-background-jobs
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

That last command should print `pytest 9.1.1`. `.venv/` is ignored by version
control — never commit it. If you already have pytest elsewhere, skip the
virtual environment and run the suite as
`PYTEST=/path/to/pytest bash tests/run_tests.sh`.

## File structure

```text
day-081-scheduling-and-background-jobs/
├── README.md                     ← you are here
├── metadata.yml                  ← machine-readable lab metadata
├── examples/
│   ├── clock.py                  ← the clock as a parameter: frozen, ticking, fake
│   ├── inprocess.py              ← sleep loops, drift, and sched with a fake clock
│   ├── cronexpr.py               ← a five-field cron parser, including the OR rule
│   ├── timezones.py              ← what 02:30 means on the two broken mornings
│   ├── joblock.py                ← flock: one copy at a time
│   ├── reportjob.py              ← the work, written idempotently and atomically
│   ├── runner.py                 ← lock + timeout + log + exit code + heartbeat
│   ├── supervise.py              ← the stronger timeout: kill the child's group
│   ├── watchdog.py               ← the dead man's switch
│   ├── gen_schedules.py          ← writes cron/launchd/systemd files; installs nothing
│   ├── job.py                    ← the command a scheduler would run (argparse)
│   ├── hold_lock.py              ← holds the lock so the suite can prove the refusal
│   ├── demo.py                   ← the whole day in one run, under a second
│   ├── data/readings.csv         ← the input; invented, tiny, no personal data
│   ├── schedules/                ← the four generated files, committed for reading
│   └── test_*.py                 ← 61 tests: cron, time zones, runner, watchdog, safety
├── starter/
│   ├── myjob.py                  ← YOUR working file (exercises 1-4)
│   ├── test_myjob.py             ← the tests for those exercises
│   ├── NOTES.md                  ← YOUR written answers (exercises 5-6)
│   └── conftest.py               ← puts starter/ and examples/ on the path
├── tests/
│   └── run_tests.sh              ← 56 checks; exits 0 only if all pass
├── expected-output/
│   ├── sample-run.txt            ← real captured run of demo.py
│   ├── cli-runs.txt              ← real captured runs of job.py, supervise, generator
│   ├── pytest-runs.txt           ← real captured pytest runs
│   ├── test-run.txt              ← real captured run of the test suite
│   └── FIELDS.md                 ← required behaviour, and what varies between runs
├── requirements/
│   ├── requirements.txt          ← pytest==9.1.1
│   └── README.md                 ← what each dependency is for, and what is stdlib
├── troubleshooting.md
└── security.md
```

## How to run

From this directory. `pt` below is your pytest: `.venv/bin/pytest` after the
install above.

```bash
# 1. The whole day in one run. Eight parts, under a second, nothing waits.
python3 examples/demo.py

# 2. Run the job. Then run it again, and watch it decline to do the work twice.
python3 examples/job.py --now 2026-07-20T02:30:00+00:00 run --output-dir /tmp/day081
python3 examples/job.py --now 2026-07-20T02:35:00+00:00 run --output-dir /tmp/day081
ls /tmp/day081

# 3. The failure paths, each with its own exit code. Check $? after each.
python3 examples/job.py --now 2026-07-21T02:30:00+00:00 run --output-dir /tmp/day081 \
    --date 2026-07-18 --simulate-failure                      # exit 1
python3 examples/job.py --now 2026-07-22T02:30:00+00:00 run --output-dir /tmp/day081 \
    --date 2026-07-17 --simulate-hang 30 --timeout 1          # exit 124, in ~1s

# 4. Overlap. Hold the lock in one terminal, run the job in another.
python3 examples/hold_lock.py /tmp/day081/daily-report.lock 20   # terminal A
python3 examples/job.py --now 2026-07-23T02:30:00+00:00 run \
    --output-dir /tmp/day081 --date 2026-07-20                   # terminal B: exit 75

# 5. The watchdog. Quiet now; alerting once the job has been silent too long.
python3 examples/job.py --now 2026-07-20T09:00:00+00:00 watch \
    --heartbeat-file /tmp/day081/daily-report.heartbeat.json --max-age-minutes 1560
python3 examples/job.py --now 2026-08-01T09:00:00+00:00 watch \
    --heartbeat-file /tmp/day081/daily-report.heartbeat.json --max-age-minutes 1560

# 6. Generate the schedule files. Read all four. Install none of them.
python3 examples/gen_schedules.py --out /tmp/day081/schedules --hour 2 --minute 30
cat /tmp/day081/schedules/com.example.dailyreport.cron

# 7. The reference suite: cron parsing, daylight saving, locking, the watchdog.
.venv/bin/pytest examples -q

# 8. Your task: exercises 1-4 in starter/myjob.py, 5-6 in starter/NOTES.md.
.venv/bin/pytest starter -q

# 9. Check your work.
bash tests/run_tests.sh

# 10. Clean up the scratch directory when you are done.
rm -rf /tmp/day081
```

## What the commands do

- `python3 examples/demo.py` — eight sections and no waiting anywhere.
  Section 1 measures the drift of a sleep loop (65-second gaps from a
  60-second interval; 495 seconds late by run 100) against a deadline-
  corrected one (0). Section 2 runs a six-hour `sched` schedule through a fake
  clock in no time at all. Sections 3 to 6 demonstrate idempotence, the lock
  refusal, a real 30-second hang killed by a 0.2-second budget, and the
  watchdog going from `OK` to `STALE`. Section 7 asks the operating system's
  own time zone database what happens on 2026-03-08 and 2026-11-01. Section 8
  prints one schedule in three dialects and states that nothing was installed.
- `python3 examples/job.py ... run` — the command a scheduler would run.
  `--now` freezes the clock; without it the real one is used. Every run prints
  one JSON line to standard output, which is where cron picks output up from,
  and `--log-file` appends the same line to a file.
- `python3 examples/job.py ... watch` — reads the heartbeat file the job
  writes on success and exits 1 if it is too old. Deliberately a separate
  command: a watchdog inside the job it watches cannot report that the job
  never started.
- `python3 examples/hold_lock.py <path> <seconds>` — takes the lock, prints
  `READY`, waits, releases, exits. It exists so you can watch the refusal
  happen rather than read about it.
- `python3 examples/supervise.py --timeout 1 -- sleep 30` — the stronger
  timeout, for when `SIGALRM` is not enough: the child runs in its own process
  group and the whole group is signalled, TERM then KILL.
- `python3 examples/gen_schedules.py --out DIR` — writes four files and
  prints the three install commands **without running them**. The paths in the
  committed copies (`/opt/reports`, `/usr/bin/python3`) are placeholders on
  purpose; pass `--project-dir` and `--python` for a machine you actually
  intend to use.
- `.venv/bin/pytest examples -q` — 61 tests covering the cron parser
  (including the OR rule), daylight saving from the real time zone database,
  the runner's five behaviours, the watchdog's five verdicts, drift
  arithmetic, and the two safety assertions.
- `bash tests/run_tests.sh` — 56 checks, including the end-to-end ones that
  need real processes and real exit codes, and the safety section.

## Expected output

Real captured sessions are in [`expected-output/`](expected-output/). The
heart of it:

```text
$ python3 examples/job.py --now 2026-07-20T02:30:00+00:00 run --output-dir /tmp/reports
{"action": "written", "duration_seconds": 0.0, "exit_code": 0, ... "status": "ok"}
exit: 0

$ python3 examples/job.py --now 2026-07-20T02:35:00+00:00 run --output-dir /tmp/reports   # again
{"action": "skipped", "duration_seconds": 0.0, "exit_code": 0, ... "status": "skipped"}
exit: 0
```

```text
$ python3 examples/job.py ... run --output-dir /tmp/reports --date 2026-07-17 --simulate-hang 30 --timeout 1
daily-report: timeout -> exit 124 (the work exceeded its timeout and was interrupted)
{"duration_seconds": 0.0, "error": "JobTimeout", "exit_code": 124, ... "timeout_seconds": 1.0}
exit: 124
```

```text
$ python3 examples/job.py --now 2026-08-01T09:00:00+00:00 watch --heartbeat-file ... --max-age-minutes 1560
STALE: last success was 12.3d ago (budget 26.0h) — the job has stopped running
exit: 1
```

```text
      2026-03-08 02:30 America/New_York -> skipped
        2026-03-08 02:30 never appears on the wall clock in America/New_York;
        the clocks jump over it. Python resolves it to 03:30 EDT, an hour later
        than intended.
      hours between daily 12:00 runs, local: [24.0, 23.0, 24.0, 24.0]
      hours between daily 12:00 runs, UTC  : [24.0, 24.0, 24.0, 24.0]
```

Only timings, temporary paths and process ids vary between runs.
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) lists exactly what is
required and what may differ, and shows the report's arithmetic so you can
check the numbers by hand.

## Validation steps

1. `python3 examples/demo.py` exits 0. Section 1 shows 65-second gaps and 495
   seconds of drift for the naive loop, and 60 and 0 for the corrected one.
2. Section 5 of the demo reports `exit code: 124` and "real time spent" of
   about 0.2 seconds, for work that asked to sleep for 30.
3. Running `job.py run` twice for the same date leaves exactly one
   `report-*.json`, and its `generated_at` is still the first run's timestamp.
4. With `hold_lock.py` holding the lock, `job.py run` exits 75, logs
   `"status": "already-running"`, and writes no report. Check with
   `echo $?` and `ls`.
5. `job.py run --simulate-hang 30 --timeout 1` exits 124 in about a second,
   and the lock is free immediately afterwards — run the job again and watch
   it succeed.
6. `job.py watch` exits 0 against a fresh heartbeat and 1 against one older
   than the budget, saying "the job has stopped running".
7. `pytest examples -q` reports `61 passed` in well under a second. Nothing in
   that suite waits for a schedule, because every clock in it is injected.
8. The generated `.cron` file's five fields parse back to 02:30 daily:
   `pytest examples -q -k cron_line`.
9. `crontab -l` still shows what it showed before you started (very likely
   `no crontab for <you>`), and `ls ~/Library/LaunchAgents` contains nothing
   named `com.example.dailyreport`.
10. `pgrep -f 'examples/job.py'` and `pgrep -f hold_lock.py` print nothing
    once you have finished.
11. Every exercise in `starter/myjob.py` is complete, `starter/NOTES.md` is
    answered in sentences, and `.venv/bin/pytest starter -q` passes.
12. `bash tests/run_tests.sh` reports `0 failure(s).` and exits 0.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `56 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure, so it can run in continuous integration. A full
captured run is in [`expected-output/test-run.txt`](expected-output/test-run.txt).

Section 8 is the one to read. It is the safety section, and it asserts the
promise this lab makes:

- no file in `examples/` or `starter/` executes `crontab`, `launchctl` or
  `systemctl`;
- your real crontab contains no entry from this lab;
- `~/Library/LaunchAgents` and `~/.config/systemd/user` contain no unit named
  `com.example.dailyreport`;
- no `hold_lock.py` and no `job.py` process survived the suite;
- no report file was left in the lab directory.

Sections 4 and 5 start real processes on purpose — one to hold a lock, one to
hang — and both are killed and waited for. The runner's `trap ... EXIT` cleans
up even if a check fails partway through.

## Cleanup

The suite writes only into a directory made with `mktemp -d`, and removes it
in the exit trap. Nothing is added to your crontab, your LaunchAgents, or your
systemd units, so there is nothing to uninstall.

```bash
rm -rf /tmp/day081        # the scratch directory from "How to run", if you made it
rm -rf .venv              # the virtual environment, when you are done
git checkout -- starter/  # optional: reset your work
```

If you followed step 6 of "How to run" and then decided to install a schedule
for real, that is outside this lab — but for completeness, you would remove it
with `crontab -e` (delete the lines), `launchctl unload <plist>` then delete
the file, or `systemctl --user disable --now <name>.timer` then delete the
unit files.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for the full list. The five you
are most likely to meet: `ModuleNotFoundError` because you started Python in
the lab root instead of running a script by path; an unexpected exit 75
because something is still holding the lock (`pgrep -f examples/job.py`); an
unexpected exit 124 because `--timeout` defaults to 60 seconds; `--now` being
refused because you left the timezone offset off; and an empty report because
the job defaults to yesterday's date and the sample data covers only
2026-07-17 to 2026-07-20.

## Security notes

See [security.md](security.md). Short version: this lab installs nothing into
any real scheduler and leaves no process running, and the test suite proves
both. Beyond that, the real security content of the day is that a scheduled
job runs unattended with your privileges for years — so run it as a dedicated
user with least privilege, keep secrets out of crontab lines and command lines
(both are readable by other users), treat anything that can write a schedule
file as able to run code as you on a timer, and log identifiers rather than
payloads.

## Extension exercises

1. **Make the job rerunnable without deleting anything.** The idempotence key
   is currently the output filename. Add a `--force` flag, and then decide
   what "force" should mean for a job that has already sent a notification —
   the answer is not obvious, and writing it down is the exercise.
2. **Add catch-up.** Given a `--since` date, generate every missing report
   between then and yesterday. Then answer the harder question in one
   paragraph: for which jobs is catch-up correct, and for which is a missed
   run better skipped entirely?
3. **Add retries with backoff.** Wrap the work so a failure is retried three
   times with waits of 1, 2 and 4 seconds. Test the schedule without waiting
   by injecting a recording sleep, exactly as Day 74 did. Then explain why
   retrying a non-idempotent job is worse than not retrying it.
4. **Alert somewhere real.** Make `watch` exit 1 *and* append to an
   `alerts.jsonl` file. Then write down what would have to be true for that
   file to be read by a human within an hour — this is the whole difficulty of
   alerting, and it is not a code problem.
5. **Extend the cron parser.** Add support for `@daily`, `@hourly` and
   `@reboot`, and for three-letter day names (`MON`, `FRI`). Write the test
   first. Then add `L` for "last day of month" and notice how much harder it
   is than the others.
6. **Compare with `croniter` on paper.** Read the project's documentation and
   list three things it does that your parser does not. Then decide, in
   writing, whether you would add the dependency to a real project — and note
   that this lab deliberately did not.
7. **Break the lock on purpose.** Replace `flock` with
   `if lock_file.exists(): sys.exit(75)` and then write a test that starts two
   runs close enough together to slip through the gap. It is harder to trigger
   than you expect, which is exactly why this bug reaches production.

## Navigation

- **Previous day:** Day 80 — Building CLIs with argparse
  (`labs/sections/programming-with-python/day-080-building-clis-with-argparse/`).
- **Next day:** Day 82 — A First Web API with FastAPI
  (`labs/sections/programming-with-python/day-082-a-first-web-api-with-fastapi/`).
- **Week 12 project:** the Personal Automation Toolkit
  (`labs/sections/programming-with-python/projects/week-12/`), which expects a
  scheduled entry point with the properties built here: idempotent, locked,
  bounded, logged, and watched.
