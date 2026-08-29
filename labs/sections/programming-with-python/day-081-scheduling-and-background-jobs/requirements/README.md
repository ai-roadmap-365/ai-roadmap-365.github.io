# Dependencies

One package, and it is only there to run the tests.

## pytest 9.1.1

- **What it is:** the test framework you have used since Day 71.
- **Why it is here:** the reference suite in `examples/` and your exercises in
  `starter/` are pytest tests. The bash runner (`tests/run_tests.sh`) drives
  pytest and then adds the end-to-end checks that need real processes and real
  exit codes.
- **Licence and cost:** MIT. Free and open source, no account, no key.
- **Install:** `python3 -m venv .venv` then
  `.venv/bin/pip install -r requirements/requirements.txt`.

## Everything else is the standard library — deliberately

Scheduling is one of the areas where Python's own batteries genuinely are
enough, and this lab makes that argument by not installing anything to do the
work:

| Module | What it does here |
| --- | --- |
| `sched` | the event scheduler, driven by an injected clock so nothing waits |
| `signal` | `SIGALRM` and `setitimer` for the in-process timeout |
| `fcntl` | `flock` for the "only one copy at a time" lock (POSIX only) |
| `subprocess` | supervising a child process and killing its process group |
| `datetime`, `zoneinfo` | aware timestamps and the real IANA time zone rules |
| `json`, `csv` | the report, and the structured log |
| `argparse` | the command-line interface, as on Day 80 |
| `tempfile`, `os.replace` | the atomic write that makes the job idempotent |
| `statistics` | `fmean` for the per-station averages |

## Libraries the lesson discusses but does NOT install

`schedule`, `APScheduler`, `croniter` and `Celery` are all real, free and open
source, and the lesson's Alternatives section describes each one accurately —
including what it would add and what it would cost you. None of them is
installed here, and no code in this lab imports any of them. Where the lesson
shows their syntax, it says plainly that the snippet was written from the
project's documented interface rather than captured from a run on this
machine.

## Network

Installing pytest needs the network once. **The lab itself never does** — no
test, script or check in this directory opens a socket, and
`tests/run_tests.sh` asserts that no networking module is even imported.

## Platform note

`fcntl` is POSIX. macOS and Linux have it; Windows does not, and the Windows
equivalent is `msvcrt.locking` or a named mutex. Run this lab under WSL on
Windows.
