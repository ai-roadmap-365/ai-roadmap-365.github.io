# Week 12 project — Personal Automation Toolkit

This week was about **Python for automation and the web**: HTTP with
`requests`, scraping responsibly, building command-line interfaces with
argparse, scheduling and background jobs, a first web API with FastAPI, and
packaging and distributing Python code. This project is where those six days
stop being six separate techniques and become one tool you could hand to
someone else and then forget about — which is the real test, because a tool you
have to remember to babysit is not an automation.

## What you are building

An installable command-line tool — call it `deskkit`, or whatever you like —
that carries **three unrelated automations behind one interface**:

1. **A poller** that fetches something over HTTP on a schedule and records what
   changed since last time.
2. **A file organizer** that sorts a messy directory into a structure you
   describe, and can be asked to explain what it would do without doing it.
3. **A report generator** that turns what the first two produced into one
   readable summary a human actually reads.

They are deliberately unrelated. A toolkit whose three commands all do the same
kind of work proves nothing about your interface design; three genuinely
different jobs force the shared parts — configuration, logging, exit codes,
state, the dry run — to be actually shared rather than copy-pasted.

The deliverable is not the feature list. It is that the tool survives being
run unattended: twice in a row, on a machine that is not yours, at a moment
when the network is broken and the directory is half-full of files it has never
seen.

## Requirements

Show this week's skills:

- **HTTP done operationally, not optimistically** (Day 78): every request sets
  a timeout, goes through a `Session`, and identifies itself. Retry only what
  is worth retrying — 429 and 5xx — with backoff, and never retry a
  non-idempotent request blindly. Distinguish in code between "no response
  arrived" and "a response arrived carrying a failure status", because they
  need different handling and different messages.
- **A source you are entitled to read** (Day 79): if the poller reads a
  website rather than an API, check for an API, a data dump or a feed first,
  honour `robots.txt` in code rather than in a comment, rate-limit yourself,
  and record provenance next to the data — where it came from, when, and under
  what terms. If you use an API, say in `NOTES.md` why that was available and
  scraping was not needed.
- **A command line that is the documentation** (Day 80): subcommands
  dispatched through `set_defaults(func=...)` with no branch on the command
  name anywhere; conversion and validation at the parser boundary through
  `type=` callables; results on standard output and diagnostics on standard
  error; the exit-code convention 0 success, 1 refusal, 2 usage error. `--help`
  should be good enough that the README is a courtesy rather than a necessity.
- **A `--dry-run` that is a guarantee** (Days 80 and 81): validated for real,
  written never. Prove it — the organizer's dry run must leave the directory
  byte-identical, and the poller's must leave the state file byte-identical.
- **Unattended-safe scheduling** (Day 81): the tool is idempotent — running it
  twice processes each unit of work once — writes state atomically through a
  same-directory temporary file and `os.replace`, takes a non-blocking lock so
  two copies cannot overlap, and emits one structured log line per run carrying
  a run id, a status, a duration and a count. Ship the schedule as a file (a
  crontab line, a launchd plist or a systemd timer) and write down what the job
  does *not* inherit from your shell.
- **A local API over the same core** (Day 82): expose the report as a small
  FastAPI endpoint that reads the same functions the CLI calls — not a
  reimplementation. Validate the query parameters with pydantic, declare a
  response model, and return the right status code when the report does not
  exist yet. Test it with `TestClient`, which opens no socket.
- **Installable, not runnable-from-here** (Day 83): a `src/` layout, a complete
  `pyproject.toml`, a console entry point, a single-sourced version readable
  through `importlib.metadata`, and both artifacts built with `python -m build`.
  Install the wheel into a throwaway virtual environment and run the tool by
  its command name, from a directory that is not the project.

## Steps

1. Write down the three jobs in one sentence each, and beside each one the
   failure it will have at 3 a.m. — the network is down, the directory is
   locked, the disk is full. Keep the list; you will check it at the end.
2. Build the skeleton first: `src/deskkit/`, `pyproject.toml`, one subcommand
   that does nothing but print its resolved configuration, and an editable
   install. Get `deskkit --help` reading well before any feature exists.
3. Decide the configuration precedence — defaults, file, environment, flags —
   and implement it once, in one place, with a way to print where each value
   came from. Everything else depends on this being boring.
4. Write the poller against a local fixture server before you point it at
   anything real, so your tests never need the internet.
5. Make the poller idempotent before you make it correct. Run it twice against
   the same fixture and assert one result. It is far harder to retrofit.
6. Build the organizer with `--dry-run` first and the real move second, so the
   dry run is never an afterthought bolted on to working code.
7. Add the lock and the structured log line, then deliberately start two copies
   at once and confirm exactly one does the work and the other exits cleanly.
8. Put the report behind both the CLI and the API by writing the report
   function first and giving it no knowledge of either.
9. Build the wheel, install it somewhere clean, and run the whole thing from a
   different directory. Fix everything that only worked because you were
   standing in the project root.
10. Break it on purpose: unplug the network mid-poll, make one source return
    500, hand the organizer a file it cannot move, and confirm each failure is
    reported, survivable, and visible in the exit code.

## Expected output

- `deskkit --help` → the three subcommands listed with one-line descriptions,
  exit code 0.
- `deskkit poll --dry-run` → the work it would do, printed; the state file's
  modification time and contents unchanged afterwards; exit code 0.
- `deskkit poll` run twice against an unchanged source → the second run reports
  zero new items and exits 0, and the state file shows one entry per item, not
  two.
- `deskkit poll` with one of several sources failing → the other sources
  complete, the failure is named on standard error, and the exit code signals
  partial success rather than success.
- `deskkit organize ~/Downloads --dry-run` → a table of planned moves; nothing
  moved; a `diff` of the directory listing before and after showing no change.
- `deskkit organize` on a directory containing a name collision → the collision
  is resolved by a documented rule, reported, and never silently overwrites.
- Two copies of `deskkit poll` started within the same second → one runs, one
  exits immediately with a message naming the lock; exactly one set of results
  is produced.
- `deskkit report --since 2026-08-01` → the summary on standard output; the log
  line on standard error, parseable as JSON, carrying a run id and a duration.
- `pytest` → all tests pass with no network access at any point.
- `python -m build` → an sdist and a wheel; `unzip -l dist/*.whl` shows
  `entry_points.txt`; installing the wheel into a fresh virtual environment and
  running the console command from `/tmp` works.

## Validation

- [ ] Every outbound request sets a timeout, and there is a test that proves a
      slow response is given up on rather than waited for forever.
- [ ] Retries cover 429 and 5xx only, and a test proves a 404 is not retried.
- [ ] `--dry-run` leaves both the target directory and the state file
      byte-identical, checked mechanically rather than by eye.
- [ ] Running any command twice produces the same result as running it once,
      and the test asserts the count rather than the absence of an error.
- [ ] State is written through a temporary file in the same directory and
      `os.replace`; interrupting a write leaves the previous state intact.
- [ ] Two concurrent runs cannot both do the work, and the loser's exit is a
      clean, explained 0 or 1 rather than a traceback.
- [ ] Each run emits exactly one structured log line to standard error, and
      results never contaminate standard output with diagnostics.
- [ ] Exit codes distinguish success, refusal, usage error, and partial
      success, and the README documents what each one means.
- [ ] Configuration resolves defaults, then file, then environment, then flags,
      and the tool can print the provenance of every setting.
- [ ] No secret appears in any log line, and a test greps the captured log for
      the secret's value to prove it.
- [ ] The API and the CLI call the same functions; there is no duplicated
      report logic, and a test asserts both produce the same numbers.
- [ ] The wheel installs into a clean environment and the console script runs
      from an unrelated working directory.
- [ ] A schedule file is committed, and `NOTES.md` records what the scheduled
      environment does not inherit and how the job compensates.
- [ ] If anything is scraped, `robots.txt` is checked in code, the rate limit is
      real, and provenance is stored with the data.

## Troubleshooting

- Second run reprocesses everything? Your idempotence key is derived from
  something that changes between runs — a timestamp, a position in a list, or
  the order the source returned. Derive it from the unit of work itself.
- Dry run leaves the directory changed? Something validated by *doing*. Look
  for a `mkdir` or an "ensure the target exists" call that runs before the
  branch on dry-run rather than after it.
- Works in the project directory, fails once installed? You are reading a file
  by a relative path. Package data belongs inside the distribution, and
  everything else belongs in configuration with an absolute default.
- Console script not found after installing the wheel? The entry point is under
  the wrong table in `pyproject.toml`, or you installed the sdist. Unzip the
  wheel and read `entry_points.txt` — if the name is not there, the metadata is
  wrong, not the installation.
- Scheduled run does nothing while the same command works in your terminal?
  It inherited neither your PATH nor your virtual environment. Use the absolute
  path to the installed console script and reproduce the environment with
  `env -i` to confirm.
- Both copies ran despite the lock? You checked whether the lock file exists
  instead of taking a lock. Between the check and the create there is a gap,
  and a crash leaves a file nobody will ever remove. Use a real non-blocking
  lock on an open file descriptor.
- Log line unparseable when a message contains a quote? You are building JSON
  by string concatenation. Serialise the record properly; a log you cannot
  parse is a log you will not read.
- Every test needs the internet? The boundary is not injected. Have the fetch
  function take a session, then hand it a fake in tests — the argument from
  Day 74, now paying for itself.
- Partial success reported as success? The exit code was set from the last
  operation rather than accumulated across all of them. Track failures as you
  go and decide the code once, at the end.
