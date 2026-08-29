# Day 084 lab — Ship the Toolkit

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Shipping an Automation Toolkit
- **Day number:** 84 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-084-shipping-an-automation-toolkit
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-084-shipping-an-automation-toolkit` when the site is running.
<!-- generated-links:end -->

## Purpose

Week 12 handed you six pieces. Day 78 gave you HTTP with `requests` — sessions,
timeouts, status codes, retries. Day 79 gave you the ethics and the technique of
collecting from the web responsibly. Day 80 gave you argparse, subcommands and
`--dry-run`. Day 81 gave you schedules, idempotence, locking and catch-up. Day
82 gave you a service with validated inputs. Day 83 gave you packaging and
console entry points.

None of them is an automation.

An automation is not a script that ran once and worked. It is something that
runs unattended, on someone else's machine, at three in the morning, while you
are asleep — and the difference is almost entirely in the parts that are not the
happy path. In this lab you assemble the week into one installable tool called
`feedkit`, and then you prove the operational properties that separate a tool
you can leave running from one you cannot.

The proof is the point. It is easy to write a fetch command that works. The
suite here asks the harder questions:

- Run it twice — does it process each item **once**?
- Break one source — do the others still succeed, is the failure **reported**,
  and does the exit code say **partial** rather than pretending everything
  worked?
- Run `--dry-run` — is the state file **byte-identical** afterwards?
- Give one setting four different values in four different places — does
  precedence resolve **flag over environment over file over default**, all four?
- Hand it a secret — does that string appear **nowhere** in the log?
- Interrupt a state write — does the **previous** state survive intact?
- Install it — does the **console script** run?

All fifty-one checks run offline. A fixture server on `127.0.0.1` stands in for
the internet, and nothing is installed into your crontab, launchd or systemd.

## Learning objectives

- Assemble a week's separate techniques into one installable, configurable,
  observable package with a pure core and the boundaries at the edges.
- Resolve configuration through four layers in a written-down order, and print
  the provenance of every setting so "why is it doing that?" takes five seconds.
- Read a secret from the environment, never from a file or a flag, and prove
  mechanically that it never reaches a log.
- Emit structured logs that identify which run and which item, and explain why
  stdout is usually the right destination.
- Design failure: retry what is worth retrying, skip and report what is not,
  stop for what makes continuing meaningless, and give partial success its own
  exit code.
- Make a job idempotent with a state file, and write that file atomically so an
  interruption cannot destroy it.
- Treat `--dry-run` as a first-class feature of anything that mutates the world.
- Build the observability a personal tool actually needs: a run summary, a
  last-success timestamp, and a watchdog that alerts on silence.
- Package the whole thing with console entry points and read a real crontab,
  launchd plist and systemd timer without installing any of them.

## Prerequisites

- The Day 84 lesson (read it first).
- Days 78–83 of this course: `requests`, responsible collection, argparse,
  scheduling, a service, and packaging. This lab uses all six and re-teaches
  none of them.
- Week 11 (Days 71–77): pytest, fixtures, boundaries and mocking, and the habit
  of a single command that returns one exit code.
- Days 64–66: files, JSON, and exception strategy — the atomic write and the
  state file build directly on them.
- Day 43: `python3 -m venv` and installing into a virtual environment.
- A terminal, a text editor, and one network connection for the install.

## Supported operating systems

- **macOS** — fully supported (captures taken on macOS 26.5.1, Apple Silicon,
  Python 3.14.0, bash 3.2.57).
- **Linux** — fully supported (any distribution with Python 3.11+ and bash).
- **Windows** — use WSL and follow the Linux path. On native Windows a virtual
  environment puts its executables in `.venv\Scripts\` rather than `.venv/bin/`,
  and `tests/run_tests.sh` is a bash script. `expected-output/FIELDS.md` records
  the differences honestly rather than guessing at captures.

Python **3.11 or newer** is required, because the configuration loader uses
`tomllib` from the standard library.

## Hardware requirements

Any computer that runs Python 3.11 or newer. The package is around 700 lines,
the property suite is 28 tests, and the whole harness finishes in a few seconds
on the authoring machine. No GPU, no special memory, no disk of consequence.
Network access is needed once, for the install.

## Required software

- `python3` (3.11 or newer; captures taken on 3.14.0).
- `bash` for the test harness (preinstalled on macOS and Linux).
- Three pinned packages — `requests`, `pytest`, `setuptools` — listed with their
  exact versions and their reasons in
  [`requirements/README.md`](requirements/README.md).

## Free and open-source options

Every tool in this lab is free and open source, and everything runs on your own
machine at no cost. `requests` is Apache-2.0; `pytest` and `setuptools` are MIT,
each per its own project metadata. The scheduler you would use in real life —
cron, launchd or systemd — is already on your machine and costs nothing.

The lesson's Alternatives section covers the wider field honestly, including
the option this lab deliberately does not take: for many jobs, a plain script
plus a cron line is the correct answer, and reaching for anything heavier is a
common and expensive mistake.

## Installation

```bash
cd labs/sections/programming-with-python/day-084-shipping-an-automation-toolkit
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
.venv/bin/pytest --version
```

The install needs the network once. **Everything after it runs offline** — the
tests never leave `127.0.0.1`.

If you would rather not create a virtual environment here, point the harness at
tools you already have:

```bash
PYTEST=/path/to/pytest PIP=/path/to/pip PYTHON=/path/to/python bash tests/run_tests.sh
```

## File structure

```text
day-084-shipping-an-automation-toolkit/
├── README.md                       ← you are here
├── metadata.yml
├── examples/                       ← the finished toolkit
│   ├── pyproject.toml              ← packaging + two console entry points
│   ├── feedkit.toml                ← a real configuration file, annotated
│   ├── src/feedkit/
│   │   ├── core.py                 ← PURE: no network, no clock, no disk
│   │   ├── config.py               ← the four-layer precedence, plus provenance
│   │   ├── logging_setup.py        ← JSON lines, run id, secret redaction
│   │   ├── state.py                ← atomic write + the run lock
│   │   ├── adapters.py             ← the edges: HTTP, the clock, sleeping
│   │   ├── runner.py               ← the order of one unattended run
│   │   └── cli.py                  ← argparse subcommands + both entry points
│   └── schedule/                   ← REFERENCE ONLY — nothing here is installed
│       ├── README.md
│       ├── feedkit.cron
│       ├── com.example.feedkit.plist
│       ├── feedkit.service
│       └── feedkit.timer
├── starter/                        ← YOUR work: 7 numbered exercises
│   ├── pyproject.toml
│   ├── feedkit.toml
│   └── src/feedkit/                ← the same package, with 7 gaps
├── tests/
│   ├── run_tests.sh                ← 52 checks; the outer harness
│   ├── test_toolkit.py             ← 28 property tests
│   ├── conftest.py
│   ├── fixture_server.py           ← 127.0.0.1, ephemeral port, no internet
│   └── fixtures/feed/              ← the JSON the server serves
│       ├── notes.json  links.json  papers.json  malformed.json
├── expected-output/
│   ├── test-run.txt                ← the full harness run
│   ├── fetch-runs.txt              ← first run, second run, dry run, partial
│   ├── config-precedence.txt       ← all four layers
│   ├── secret-handling.txt         ← the leak check
│   ├── status-and-report.txt
│   └── FIELDS.md                   ← what must match, what may differ
├── requirements/
│   ├── requirements.txt
│   └── README.md
├── troubleshooting.md
└── security.md
```

## How to run

From this directory, after the install.

```bash
# 1. The whole thing. Start here.
bash tests/run_tests.sh
echo "exit code: $?"
```

To drive the toolkit by hand you need the fixture server, and the base address
must be handed to the toolkit through the environment — it has no default, on
purpose.

```bash
# 2. Start the fixture server in one terminal. It prints its port and stays up.
.venv/bin/python tests/fixture_server.py --token demo-token-value

# 3. In a SECOND terminal, in this directory, set up the environment.
#    Replace PORT with the number the server printed.
cd examples
export FEEDKIT_BASE_URL="http://127.0.0.1:PORT"
export FEEDKIT_TOKEN="demo-token-value"
export PYTHONPATH="$PWD/src"
alias fk="../.venv/bin/python -m feedkit.cli"

# 4. The first run. Seven new entries from three sources.
fk fetch; echo "exit: $?"

# 5. The same command again. Zero new entries — this is idempotence.
fk fetch; echo "exit: $?"

# 6. A dry run. It says what it would do and writes nothing.
shasum feedkit-state.json
fk --sources notes,links,papers,flaky fetch --dry-run
shasum feedkit-state.json          # identical

# 7. Partial success. One source is broken; the others still work.
fk --sources notes,broken,papers fetch; echo "exit: $?"   # 2, not 0

# 8. Where every setting came from.
fk status --explain-config

# 9. The watchdog: it can fail, which is the whole point.
fk status; echo "exit: $?"
fk status --max-age-minutes 0; echo "exit: $?"

# 10. What has been collected.
fk report --limit 5

# 11. Read the schedule files. NONE of them is installed by this lab.
cat schedule/feedkit.cron
cat schedule/feedkit.service

# 12. Install it for real, and use the console script.
cd ..
.venv/bin/pip install -e examples --no-build-isolation --no-deps
cd examples && ../.venv/bin/feedkit --version && ../.venv/bin/feedkit fetch

# 13. Your task: fill in the seven exercises in starter/src/feedkit/.
cd ../starter
PYTHONPATH="$PWD/src" ../.venv/bin/python -m feedkit.cli --help
# ... complete exercises 1-7 ...
```

Stop the fixture server with Ctrl-C when you are finished. Nothing else in this
lab starts a background process.

## What the commands do

- `bash tests/run_tests.sh` — the whole harness. It starts the fixture server on
  an ephemeral port, waits for readiness in a loop rather than sleeping, runs
  the 28 pytest property tests, then drives the CLI as a real subprocess for
  every operational property, then installs the package and runs the console
  script, and finally kills the server in a `trap`. 52 checks, one exit code.
  The install step deliberately differs from the one you run by hand above: the
  harness builds a wheel and installs it into a throwaway environment under a
  temporary directory, so running the tests never adds a package to whatever
  Python you happen to have active. Checking for the command on your `PATH`
  afterwards would only find it because the test had polluted your environment.
- `.venv/bin/python tests/fixture_server.py` — the stand-in for the internet.
  Binds `127.0.0.1` on port 0 (the kernel picks a free port) and prints the port
  on its first line. Serves the fixtures, requires the bearer token, answers 500
  for `broken`, and answers 503 twice then 200 for `flaky` so retry-with-backoff
  can be watched recovering.
- `fk fetch` — one unattended run: acquire the lock, load the state, fetch each
  source with bounded retries, skip and report the ones that fail, fold the
  successes into the state, write it atomically, print the summary, exit with a
  code that tells the truth (0 all good, 2 partial, 1 nothing worked, 3 a run
  was already in progress).
- `fk fetch --dry-run` — everything except the write. Note what it still does:
  it fetches, it reports, and it tells you exactly what *would* have changed.
  A dry run that skips the work tells you nothing.
- `fk status --explain-config` — a table of every setting, its value, and which
  of the four layers it came from. The token appears as `set (never printed)`.
- `fk status --max-age-minutes N` — the watchdog. Exits non-zero when the last
  **successful** run is older than the allowance, including when there has never
  been one. This is what a second, much simpler scheduled job reads to notice
  the run that never happened.
- `fk report --limit N` — renders what has been collected, newest first.
- `pip install -e examples --no-build-isolation --no-deps` — a real editable
  install (Day 83). The two flags keep it offline: the backend and the runtime
  dependency are already in the virtual environment. Afterwards `feedkit` and
  `feedkit-scheduled` are commands on your PATH, which is what makes a schedule
  entry short enough to read.
- `cat schedule/feedkit.cron` — a real crontab entry, annotated. It is
  **not installed**, and neither are the plist or the systemd units; each file
  says so at the top and carries its own install and removal commands for the
  day you choose to use one deliberately.

## Expected output

The harness ends like this (a real captured run — see
[`expected-output/test-run.txt`](expected-output/test-run.txt) for all 75 lines):

```text
9. The starter is runnable, and the shipped files behave
  ok: the starter's --help works before you write a line
  ok: the starter carries its numbered exercises (21 markers)
  ok: the starter package imports cleanly
  ok: no Python file can spawn a process, so nothing can touch a scheduler
  ok: examples/schedule/feedkit.cron ships as a reference and says so

10. Nothing in this lab reaches the internet
  ok: no executable file names any host but 127.0.0.1
  ok: nothing hard-codes port 8000 — the port everyone already has in use

52 checks, 0 failure(s).
```

A partial-success run, in full
([`expected-output/fetch-runs.txt`](expected-output/fetch-runs.txt)):

```text
$ feedkit --sources notes,broken,papers fetch
{"ts": "2026-07-19T19:09:13", "level": "info", "run_id": "5a1ffd4e", "event": "run started", "status": "started", "path": "feedkit-state.json"}
{"ts": "2026-07-19T19:09:13", "level": "info", "run_id": "5a1ffd4e", "event": "source started", "source": "notes"}
{"ts": "2026-07-19T19:09:13", "level": "info", "run_id": "5a1ffd4e", "event": "source finished", "source": "notes", "attempt": 1, "status": "ok", "count": 0}
{"ts": "2026-07-19T19:09:13", "level": "info", "run_id": "5a1ffd4e", "event": "source started", "source": "broken"}
{"ts": "2026-07-19T19:09:13", "level": "warning", "run_id": "5a1ffd4e", "event": "fetch attempt failed", "source": "broken", "attempt": 1, "status": 500}
{"ts": "2026-07-19T19:09:13", "level": "warning", "run_id": "5a1ffd4e", "event": "fetch attempt failed", "source": "broken", "attempt": 2, "status": 500}
{"ts": "2026-07-19T19:09:14", "level": "warning", "run_id": "5a1ffd4e", "event": "fetch attempt failed", "source": "broken", "attempt": 3, "status": 500}
{"ts": "2026-07-19T19:09:14", "level": "error", "run_id": "5a1ffd4e", "event": "source failed", "source": "broken", "status": "failed"}
{"ts": "2026-07-19T19:09:14", "level": "info", "run_id": "5a1ffd4e", "event": "source started", "source": "papers"}
{"ts": "2026-07-19T19:09:14", "level": "info", "run_id": "5a1ffd4e", "event": "source finished", "source": "papers", "attempt": 1, "status": "ok", "count": 0}
{"ts": "2026-07-19T19:09:14", "level": "info", "run_id": "5a1ffd4e", "event": "state written", "status": "partial", "path": "feedkit-state.json"}
{"ts": "2026-07-19T19:09:14", "level": "info", "run_id": "5a1ffd4e", "event": "run finished", "status": "partial", "count": 0}
run 5a1ffd4e: partial
  sources: 2 ok, 1 failed, 3 total
  new entries: 0
  FAILED: broken: HTTP 500 after 3 attempts
exit: 2
```

Read the timestamps on the three warning lines: `:13`, `:13`, `:14`. That gap is
the backoff doubling from half a second to a full one, visible in a real
capture rather than described.

And the four precedence layers
([`expected-output/config-precedence.txt`](expected-output/config-precedence.txt)):

```text
=== layer 1: nothing configured — the default wins ===
  max_items            5                            default
=== layer 2: the configuration file beats the default ===
  max_items            10                           file
=== layer 3: the environment beats the file ===
  max_items            20                           environment
=== layer 4: a flag beats the environment ===
  max_items            40                           flag
```

[`expected-output/secret-handling.txt`](expected-output/secret-handling.txt)
holds the leak check, and
[`expected-output/FIELDS.md`](expected-output/FIELDS.md) states which values must
be identical on your machine and which are expected to differ.

## Validation steps

1. `bash tests/run_tests.sh` ends with `52 checks, 0 failure(s).` and exits 0.
2. A first `fetch` over the three configured sources reports `new entries: 7`
   and exits 0; running it again reports `new entries: 0` and exits 0.
3. `shasum feedkit-state.json` before and after a `--dry-run` gives the same
   hash, and the dry run still reports what it would have collected.
4. `--sources notes,broken,papers fetch` prints `sources: 2 ok, 1 failed`, a
   `FAILED: broken:` line, and **exits 3**.
5. `--sources broken fetch` exits 1. Creating `feedkit-state.json.lock` and
   running `fetch` exits 75 and writes nothing.
6. `status --explain-config` shows `5 default`, then `10 file` with a config
   file present, then `20 environment` with `FEEDKIT_MAX_ITEMS=20`, then
   `40 flag` with `--max-items 40`.
7. `grep -c "$FEEDKIT_TOKEN"` over any captured log prints `0`, and unsetting
   `FEEDKIT_TOKEN` makes every request fail with `HTTP 401 (not retryable)` —
   which proves the token was genuinely being sent.
8. The `flaky` source succeeds on `attempt 3`, and the summary says
   `retried: flaky succeeded on attempt 3`.
9. `status --max-age-minutes 0` prints `STALE` and exits 3; in a fresh
   directory, `status` prints `last success: never` and exits 3.
10. After `pip install -e examples --no-build-isolation --no-deps`,
    `feedkit --version` prints `feedkit 1.0.0` and `feedkit fetch` exits 0.
11. `pgrep -fl fixture_server.py` finds nothing after the harness finishes.

## Tests

```bash
bash tests/run_tests.sh
```

Expected final line: `52 checks, 0 failure(s).` The command exits 0 on success
and non-zero on any failure.

Read two blocks of the harness before you run it. Section 2 copies the package
into a temporary directory, breaks exactly one line — the one that filters out
already-seen ids — and demands that the property suite goes **red**. A suite
that stays green when idempotence is broken is a suite that is checking nothing,
and this is the check that proves it is not. Section 4 is the leak check: it
greps the captured log, the state file and the `--explain-config` output for the
exact token string and requires zero matches, then removes the token and
confirms every request is refused — because redaction that works by never
sending the credential would prove nothing at all.

A full captured run is in
[`expected-output/test-run.txt`](expected-output/test-run.txt).

## Cleanup

```bash
rm -f examples/feedkit-state.json examples/feedkit-state.json.lock
rm -rf examples/src/feedkit.egg-info
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

To remove the console scripts the harness installed:
`.venv/bin/pip uninstall -y feedkit`. To remove the tools as well:
`rm -rf .venv`. To reset your work: `git checkout -- starter/`.

The harness makes its own temporary directories with `mktemp -d` and removes
them in a `trap`, so a completed run leaves nothing behind and no process
running. **Nothing was ever added to your crontab, launchd or systemd, so there
is nothing to uninstall there.**

## Troubleshooting

See [troubleshooting.md](troubleshooting.md). The ones you are most likely to
meet: `no base URL configured`, which is the toolkit refusing to guess a
deployment fact; `new entries: 0` when you expected more, which is idempotence
working; `exit code 3`, which is partial success being honest rather than a
failure; `exit code 75`, which is a lock file left by a killed run; and a
scheduled job that works by hand but does nothing on a schedule, which is
`PATH`, the working directory, or the environment, in that order of likelihood.

## Security notes

See [security.md](security.md). Short version: the token is read from the
environment and from nowhere else, because a flag lands in your shell history
and in `ps` output while a config file lands in version control. The lab proves
the no-leak property mechanically rather than asserting it, and the fixture
server genuinely requires the token so the proof means something. Nothing is
installed into a real scheduler, nothing reaches the internet during the tests,
nothing needs `sudo`, and the file that leaks a credential most often — a log —
is the one the redaction filter guards. The "if a token leaks" section states
the order of operations, and revoking comes first.

## Extension exercises

1. **Add a fourth subcommand: `prune`.** Drop entries older than N days from the
   state file, atomically. Then answer the harder question in a comment: if you
   prune a `seen_id`, the next run will treat that entry as new. What is the
   correct relationship between the entry list and the seen list, and what does
   that tell you about which one is really the state?
2. **Give the watchdog somewhere to shout.** `status --max-age-minutes` exits
   non-zero; wire that into something that reaches you. The cron reference shows
   the shape. Then write down why the watchdog must not live inside
   `feedkit-scheduled` itself.
3. **Make the retry policy per-source.** Some sources deserve five attempts and
   some deserve one. Add it to the configuration, keep the precedence intact,
   and add a test. Then decide whether it earned its complexity.
4. **Break the leak check on purpose.** Log the token deliberately from
   `adapters.py`, remove it from the `secrets` list passed to `configure`, and
   watch section 4 of the harness go red. This is the single most valuable
   minute in the lab: it shows the check is real.
5. **Replace the state file with SQLite.** Week 13 is about databases. Write
   down, before you start, what you would gain (concurrent readers, queries,
   no whole-file rewrite) and what you would lose (a state file you can read
   with `cat`, and an atomic write you can explain in one paragraph).
6. **Write the runbook.** One page: what this job does, when it runs, what each
   exit code means, what to check first when it fails, how to run it by hand,
   and how to turn it off. Then hand it to somebody and ask them to recover from
   a failure using only that page. Whatever they had to ask you is what the
   runbook is missing.
7. **Delete it.** Take one automation you actually run, work out how much time it
   has saved you against how much time you have spent maintaining it, and if the
   arithmetic is negative, delete it. Knowing when to stop is the skill this
   whole week is building toward.

## Navigation

- **Previous day:** Day 83 — packaging and distribution
  (`labs/sections/programming-with-python/day-083-packaging-and-distributing-python-code/`).
- **Next day:** Day 85 — the first day of Week 13, SQL and Relational Databases
  (`labs/sections/programming-with-python/`).
- **Week 12 project:** the Personal Automation Toolkit
  (`labs/sections/programming-with-python/projects/week-12/`). It builds
  directly on this lab: the same shape, your own sources, and a runbook.
