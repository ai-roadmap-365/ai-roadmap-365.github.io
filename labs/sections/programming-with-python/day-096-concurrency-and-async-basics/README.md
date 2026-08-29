# Day 096 lab — Waiting Versus Computing

## Lesson

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Concurrency and async Basics
- **Day number:** 96 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-096-concurrency-and-async-basics
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-096-concurrency-and-async-basics` when the site is running.
<!-- generated-links:end -->

## Purpose

Day 96 of 365. Somebody tells you to "make it concurrent". That instruction is not
actionable, and acting on it anyway is how people lose weeks.

This lab replaces the instruction with a question you can answer:

> **Is this work waiting, or is it computing?**

You then prove the answer to yourself by measuring it, three ways for
waiting work and four ways for computing work, on your own machine, right
now. Nothing here is taken on trust. By the end you will have watched:

- twenty requests take **2.1 seconds** in sequence and **0.12 seconds** on an
  event loop — the same work, the same results, a seventeen-fold difference;
- four CPU-bound tasks refuse to go faster with threads (**1.01x**) and then
  go **2.89x** faster with processes, from a one-word edit;
- five coroutines that say `gather` run strictly one at a time because one
  of them called `time.sleep`, with nothing raised and every answer correct;
- an event loop starved for **211 milliseconds** by a task that had nothing
  to do with it;
- a shared counter lose **290,878 of 400,000** increments, and then lose none;
- two locks deadlock, in eight lines, and stop deadlocking after one rule;
- and an event loop you wrote yourself, in about a dozen lines, after which
  `async`/`await` stops being magic because you have written the loop.

Those figures are from the authoring machine on one day. **The shape is what
travels, and the shape is what the tests assert** — never a millisecond.

## Learning objectives

By the end of this lab you will be able to:

- State the difference between concurrency (a structure: several things in
  progress) and parallelism (a hardware fact: several things executing at the
  same instant), and say which one your problem actually needs.
- Classify a piece of work as waiting or computing, and pick the model that
  suits it without guessing.
- Use `ThreadPoolExecutor` and `ProcessPoolExecutor` through the same
  `concurrent.futures` interface, and explain why swapping one for the other
  is a one-word edit with completely different consequences.
- Say what the global interpreter lock actually protects — interpreter state,
  not your data — and why I/O releasing it is the reason threads help with
  waiting.
- Report the GIL status of the interpreter in front of you rather than the one
  in a book, using `sysconfig.get_config_var("Py_GIL_DISABLED")`.
- Write coroutines, drive them with `asyncio.run`, and combine them with
  `asyncio.gather` and `asyncio.TaskGroup`, choosing between the two on the
  question of whether partial success is a real answer.
- Recognise a blocking call inside a coroutine, measure the damage it does to
  unrelated tasks on the same loop, and repair it with `asyncio.to_thread`.
- Apply a timeout with `asyncio.timeout`, and describe cancellation
  accurately: an exception delivered inside the task at its next await, so
  `finally` blocks run and nothing leaks.
- Reproduce a lost-update race deliberately, fix it with a `threading.Lock`,
  and explain why handing subtotals down a `queue.Queue` is usually better
  than any lock.
- Produce a deadlock from two locks taken in opposite orders and remove it
  with a consistent lock ordering.
- Build a cooperative scheduler from generators — a ready queue, a sleeping
  list and a loop — and map each part onto what asyncio does.
- Report a performance result honestly: several runs, the spread stated, the
  machine named, and a ratio rather than a stopwatch reading.

## Prerequisites

- **Day 43** — a working `python3` on your `PATH`.
- **Day 82** — the fixture-server pattern: a real HTTP server on `127.0.0.1`
  standing in for the internet, which is how this lab measures waiting
  without needing a network.
- **Day 84** — running a local server inside a test harness and shutting it
  down cleanly.
- **Day 63 onwards** — functions, generators and `yield`, which exercise 8
  builds an event loop out of.
- Nothing else. No third-party package is used, and the test suite fails if
  any file in this lab imports one.

## Supported operating systems

| System | Status |
| --- | --- |
| macOS (Apple Silicon or Intel) | Captured here — macOS 26.5.2, arm64, 14 logical CPUs |
| Linux (any current distribution) | Expected to behave identically. `ProcessPoolExecutor` defaults to the fork start method there rather than spawn, which usually makes the process column look slightly *better*, not worse |
| Windows | Use WSL and follow the Linux path. The harness scripts need bash and `mktemp -d`; native Windows was not tested and no output is claimed for it |

The suite refuses to run its process comparison on a single-CPU machine and
says so, rather than reporting a meaningless ratio.

## Hardware requirements

Two or more logical CPUs. That is the only real requirement, and it is
checked: with one CPU, "processes are faster than threads" is not a claim
that can be tested.

More cores make the process column look better and change nothing else. No
GPU, no network, no disk to speak of — the whole lab writes nothing outside
a temporary directory.

## Required software

| Tool | Minimum | Used here | Why |
| --- | --- | --- | --- |
| `python3` | 3.11 | 3.14.0 | `asyncio.TaskGroup`, `asyncio.timeout` and `except*` all arrived in 3.11 |
| `bash` | 3.2 | 3.2.57 | The two harness scripts |

Standard library only: `asyncio`, `threading`, `multiprocessing` (through
`concurrent.futures`), `queue`, `time`, `urllib`, `http.server`, `socket`,
`collections`, `statistics`, `sysconfig`.

Check your interpreter, including the fact this lab cares about most:

```bash
python3 --version
python3 -c "import sys, sysconfig; print(sys.version); print(sysconfig.get_config_var('Py_GIL_DISABLED'))"
python3 -c "import os; print(os.cpu_count(), 'logical CPUs')"
```

`Py_GIL_DISABLED` printing `0` means your interpreter has the global
interpreter lock, which is what every measurement in this lab assumes and
reports. If it prints `1` you have a free-threaded build (PEP 703), the
threads-do-not-help result should **not** hold for you, and the suite skips
that one check and says so instead of failing you for having better tooling.

## Free and open-source options

All of it is free, and no part of this lab is degraded without an account.

- **Python** and its standard library (PSF licence) provide every concurrency
  model used here. There is nothing to install.
- **`trio`** (Apache 2.0 / MIT) is the best-known alternative async library,
  built around structured concurrency — its nurseries are the idea that
  `asyncio.TaskGroup` later brought into the standard library. Not installed
  here; nothing in this lab reproduces its output.
- **`anyio`** (MIT) lets one codebase run on either asyncio or trio. Not
  installed here.
- **`gevent`** (MIT) takes the opposite approach: it monkey-patches the
  standard library so ordinary blocking code becomes cooperative without
  `async`/`await`. Not installed here.
- **Celery** (BSD) is where you go when the work must outlive the process and
  be spread over machines rather than cores. Not installed here.

The lesson's Alternatives section covers when each is the right call. This
lab runs only what ships with Python, so it works offline on a fresh machine.

## Installation

None. Change into this directory and start.

```bash
cd labs/sections/programming-with-python/day-096-concurrency-and-async-basics
python3 --version
```

If your interpreter lives somewhere unusual, both scripts take an override
rather than guessing:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## File structure

```text
day-096-concurrency-and-async-basics/
├── README.md                      this file
├── metadata.yml                   lab metadata and the recorded run
├── security.md                    what this lab does to your machine
├── troubleshooting.md             grouped by the message you actually see
├── requirements/
│   ├── README.md                  versions, the calibration, what is absent
│   └── requirements.txt           empty of packages, on purpose
├── starter/                       YOUR work happens here
│   ├── 00_brief.md                the situation, and the one question
│   ├── 01_exercises.py            eight exercises, each with its approach named
│   ├── 02_check.sh                "N of 8 exercises complete."
│   └── _progress.py               the checker behind it; behaviour and ratios only
├── examples/                      the reference. Read AFTER you have tried
│   ├── labkit.py                  fixture server, CPU task, timing helpers
│   ├── 01_waiting.py              20 requests: sequential, threads, asyncio
│   ├── 02_computing.py            4 prime counts: + processes, and the flip
│   ├── 03_blocking_coroutine.py   the rule broken, measured, and repaired
│   ├── 04_race.py                 a lost-update race, three fixes, a deadlock
│   ├── 05_scheduler.py            an event loop in forty lines of generators
│   ├── 06_timeouts.py             cancellation, timeouts, gather against TaskGroup
│   └── 07_solutions.py            the eight reference answers
├── tests/
│   └── run_tests.sh               58 checks of shapes and values
└── expected-output/               captured from a real run on 2026-08-16
    ├── FIELDS.md                  what must match and what may differ
    ├── waiting.txt                ├─ the six example scripts,
    ├── computing.txt              │  captured verbatim
    ├── blocking-coroutine.txt     │
    ├── race.txt                   │
    ├── scheduler.txt              │
    ├── timeouts.txt               ┘
    ├── starter-progress.txt       0 of 8 before, 8 of 8 after
    └── test-run.txt               the full harness run
```

## How to run

```bash
# 1. The whole thing. Start here — it should be green before you change
#    anything, and green again when you have finished. Takes about 40s.
bash tests/run_tests.sh
echo "exit code: $?"

# 2. Read the brief. It is three minutes and it is the point of the day.
#    starter/00_brief.md

# 3. Find out where you stand. It will say 0 of 8, and name each one.
bash starter/02_check.sh

# 4. Now do the work in starter/01_exercises.py, re-running step 3 as you go.
#    Look at the RATIOS the checker prints, especially for exercises 4 and 5.

# --- everything below is the reference. Look after you have tried. ---

# 5. Waiting work, three ways. Watch threads and asyncio both collapse it.
python3 examples/01_waiting.py

# 6. Computing work, four ways. Watch the answer flip completely.
python3 examples/02_computing.py

# 7. The rule you must not break, broken on purpose and then repaired twice.
python3 examples/03_blocking_coroutine.py

# 8. A counter that loses increments, three fixes, and a deadlock.
python3 examples/04_race.py

# 9. An event loop built from generators, so await stops being magic.
python3 examples/05_scheduler.py

# 10. Cancellation, timeouts, and gather against TaskGroup.
python3 examples/06_timeouts.py

# 11. The reference answers, checked the same way your own work is.
bash starter/02_check.sh examples/07_solutions.py
```

## What the commands do

**`bash tests/run_tests.sh`** runs all six example scripts, parses the
machine-readable `RESULT` lines they print, and applies its own thresholds to
them — 58 checks in all. It deliberately does **not** trust the scripts' own
`SHAPE` verdicts: a test that asks the code under test whether it passed is
not a test. It then runs the starter checker in both states, sabotages the
reference answer to exercise 2 so that it is secretly sequential, and
confirms the checker catches it on speed while every returned value is still
correct. Everything happens in a temporary directory removed on exit.

**`bash starter/02_check.sh`** imports your `starter/01_exercises.py`, calls
each of the eight functions with controlled inputs, and reports which are
complete. It checks behaviour (are the twenty bodies right, and in order?)
and ratios (is the threaded version at least 2.5x faster than the sequential
one on this machine, right now?). It never inspects how you wrote anything.
Pass it a path to check a different module, which is how the reference
answers are verified.

**`python3 examples/01_waiting.py`** starts the fixture server, warms it,
then runs twenty requests sequentially, through a 20-thread pool, and through
an event loop — three times each — and prints every sample, the median and
the spread.

**`python3 examples/02_computing.py`** does the same for four prime counts,
adding a process pool, and prints the interpreter's `Py_GIL_DISABLED` value
so the numbers are attached to the build that produced them.

**`python3 examples/03_blocking_coroutine.py`** gathers five coroutines that
call `time.sleep`, then the same five with `await asyncio.sleep`, then the
same five with `asyncio.to_thread` — and separately measures how late an
unrelated 10 ms heartbeat runs while the loop is blocked.

**`python3 examples/04_race.py`** runs one shared counter with eight threads
at the default switch interval, then at a microsecond, then with a lock, then
with per-thread subtotals posted to a `queue.Queue`, and finishes with a real
deadlock detected by timeout and the ordering rule that removes it.

**`python3 examples/05_scheduler.py`** runs a scheduler built from a `deque`,
a sleeping list and a `while` loop, over generators that `yield` to pause.

**`python3 examples/06_timeouts.py`** times out a request that will not
finish, shows the cancelled task's `finally` block running, and contrasts
`asyncio.gather(return_exceptions=True)` with `asyncio.TaskGroup`.

## Expected output

The harness ends with a real captured line:

```text
58 checks, 0 failure(s).
```

and exits 0. The starter reports `0 of 8 exercises complete.` with exit 1
before you begin and `8 of 8 exercises complete.` with exit 0 when you are
done.

The two measurements the whole day turns on, captured on the authoring
machine — **your seconds will differ and your ratios should not**:

```text
timings                                                                    (waiting work)
  sequential (one at a time)         runs:  2.101,  2.099,  2.117   median  2.101s   spread 0.017s
  threads (ThreadPoolExecutor 20)    runs:  0.172,  0.142,  0.172   median  0.172s   spread 0.031s
  asyncio (one thread, one loop)     runs:  0.117,  0.114,  0.176   median  0.117s   spread 0.062s

timings                                                                  (computing work)
  sequential (one at a time)         runs:  1.417,  1.418,  1.413   median  1.417s   spread 0.005s
  threads (ThreadPoolExecutor 4)     runs:  1.412,  1.405,  1.410   median  1.410s   spread 0.007s
  processes (ProcessPoolExecutor 4)  runs:  0.488,  0.504,  0.490   median  0.490s   spread 0.016s
  asyncio (one thread, one loop)     runs:  1.432,  1.440,  1.451   median  1.440s   spread 0.020s
```

Threads: **12.2x** on waiting work, **1.01x** on computing work. Same code
shape, opposite result. That is the lab.

The race, which is the other thing worth quoting:

```text
1. the naive counter at the interpreter's DEFAULT switch interval
   run 1: 400,000   lost 0
2. the same code with the switch interval at 1e-06 s
   run 1: 111,226   lost 288,774
3. the same counter, one lock
   run 1: 400,000   lost 0
```

Read `expected-output/FIELDS.md` before comparing anything: it lists exactly
which values must match on your machine (the prime counts, the counter
totals, the scheduler's interleaving order) and which are expected to differ
(every elapsed time, every speed-up ratio's precise value, and the number of
increments the unsafe counter loses).

## Validation steps

1. `bash tests/run_tests.sh` ends with `58 checks, 0 failure(s).` and exits 0.
2. Waiting work: threads and asyncio are each **at least 4x** faster than
   sequential, and all three return 20 well-formed bodies **in input order**.
3. Computing work: threads are **below 1.5x** sequential, processes are **at
   least 1.5x**, and processes beat threads by at least a further 1.4x.
4. Every approach in step 3 still answers **41538** — a fast wrong answer is
   not an answer.
5. Gathering five blocking coroutines takes the **serial** time (at least
   0.9 s for 5 x 0.2 s), and both repairs are at least **2.5x** faster.
6. The blocked loop starves an unrelated heartbeat by **at least 3x** the
   healthy gap, while all three versions return identical correct results.
7. The unprotected counter loses **more than 1000** increments; the locked
   and queued versions total exactly **400000**.
8. Two locks taken in opposite orders deadlock; taken in one order they do not.
9. The generator scheduler interleaves 3, 2 and 1 step tasks as
   `alpha beta gamma alpha beta alpha`, and a task that never yields runs all
   four of its steps before any other task starts.
10. A timeout fires at the caller's 0.15 s budget rather than the work's
    0.40 s, and the cancelled task's `finally` block appears in the log.
11. `gather` leaves 2 of 3 tasks finished; `TaskGroup` cancels 2 siblings.
12. The starter reports `0 of 8` with a non-zero exit, the reference reports
    `8 of 8` with exit 0, and a "threaded" answer that is secretly sequential
    is caught **on speed** while all its values are correct.
13. After the harness finishes, no `__pycache__` directory and no temporary
    file survive anywhere in this directory.

## Tests

```bash
bash tests/run_tests.sh
echo "exit code: $?"
```

58 checks, exit 0 when they all pass and non-zero otherwise.

**Why the tests are written the way they are** — this is the part worth
reading, because timing tests are usually terrible and these try not to be.

- **No check asserts a duration.** Every speed check is a ratio between two
  things measured in the same run on the same machine, with a margin wide
  enough to survive a laptop on battery or a loaded CI runner. The captured
  thread speed-up on waiting work was 12.2x; the assertion is "at least 4x".
- **The race is forced, and the forcing is stated.** A naive lost-update loop
  did **not** lose a single increment on this interpreter across 20 dedicated
  trials at the default 5 ms switch interval. Rather than pretend otherwise or write a
  test that fails one run in fifty, `examples/04_race.py` drops the switch
  interval to 1 microsecond, which makes the same race land on every run.
  Nothing about the buggy code changes — only how often the interpreter
  considers handing the thread to somebody else. The script prints both
  results, so you see the honest version first.
- **The suite parses `RESULT` lines rather than trusting `SHAPE` lines.** The
  scripts print their own verdicts for a human reader; the tests recompute
  them.
- **The suite proves it can fail.** It sabotages the reference answer to
  exercise 2 into a sequential loop that still returns every correct value,
  and asserts the checker rejects it.
- **The GIL check adapts to the build.** On a free-threaded interpreter
  (`Py_GIL_DISABLED` is `1`) the "threads do not help" check would be wrong,
  so it is skipped with a printed note rather than failed.

Overrides, if your interpreter is somewhere unusual:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

## Cleanup

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

`tests/run_tests.sh` and `starter/02_check.sh` both set
`PYTHONDONTWRITEBYTECODE=1` and build everything inside `mktemp -d`, removed
in a `trap`, so if you only ran those there is nothing to clean up — and the
suite asserts as much. The command above matters only if you ran an example
script by hand without that variable set.

Nothing else is created. No database, no log file, no socket left listening:
the fixture server is shut down and closed in a `finally` block, and it binds
to an ephemeral port so it cannot collide with anything you are running.

To reset your own work and start the exercises again:

```bash
git checkout -- starter/
```

## Troubleshooting

`troubleshooting.md` has the full list, grouped by the message you actually
see. The ones you are most likely to meet:

- **`Can't pickle <function ...>`** from `ProcessPoolExecutor` — you passed a
  lambda, a closure or a locally defined function. Child processes import
  your module to find the target, so it must be defined at module level.
- **`RuntimeError: asyncio.run() cannot be called from a running event loop`**
  — you called `asyncio.run` inside a coroutine. It is the boundary between
  synchronous code and the loop, used once, at the top.
- **A coroutine that never runs** — you called it and never awaited it, or you
  used `create_task` and never gave the loop a chance to start it. Python
  warns `coroutine ... was never awaited` for the first case and says nothing
  at all for the second.
- **The threaded version is no faster** — check what the work is. If it never
  waits, that is the correct result, and it is exercise 4.
- **The process version is no faster** — the tasks may be too small for the
  start-up and pickling cost, or your machine may have too few cores.
- **`8 of 8` will not appear even though the answers look right** — the two
  fetch exercises and the process exercise are judged on speed as well as
  correctness. The checker prints the ratio it measured and the one it needs.
- **The unsafe counter does not lose anything for you** — that is a real and
  reportable observation, not a broken lab. See the note in `troubleshooting.md`.

## Security notes

`security.md` has the full account. In short: nothing here reaches the
internet, runs `sudo`, needs a credential, or installs anything, and the test
suite checks each of those rather than promising them.

The two points specific to this day:

- **The only sockets are on the loopback address.** `examples/labkit.py`
  binds to `127.0.0.1` on an ephemeral port, so the fixture server is not
  reachable from another machine and cannot collide with a port you are
  already using. The suite asserts that no URL anywhere in this lab names any
  host but the loopback address.
- **Concurrency is itself a security surface, and this lab shows two of its
  edges.** A race condition on a shared counter is the same bug as a race
  condition on a permissions check or a balance — the lost update in
  `04_race.py` is a toy version of a time-of-check-to-time-of-use flaw. And a
  blocked event loop is a denial of service you inflict on yourself: one slow
  synchronous call in one handler stops every other request on that worker,
  which is exactly what `03_blocking_coroutine.py` measures.

`sys.setswitchinterval` is process-wide, so `04_race.py` and the starter
checker both restore the previous value in a `finally` block, and the test
suite verifies that they do.

## Extension exercises

1. **Find the crossover point.** `examples/02_computing.py` uses four tasks of
   roughly 350 ms each. Shrink the prime limit until `ProcessPoolExecutor` is
   *slower* than sequential code, and find the size at which it breaks even.
   Write down the number, then work out what it is really measuring — process
   start-up, argument pickling, or result pickling — by timing a pool that is
   created once and reused against one created per call.
2. **Make the race land at the default switch interval.** The naive counter in
   `04_race.py` lost nothing at 5 ms on the authoring machine. Get it to lose
   increments *without* touching `sys.setswitchinterval`: more threads, a
   longer read-modify-write, an object with a property, work between the read
   and the write. Report how many trials you needed, and what that tells you
   about relying on tests to catch this class of bug.
3. **Give your scheduler a socket.** `examples/05_scheduler.py` jumps its
   clock forward when everything is asleep. Replace that with a real
   `selectors.DefaultSelector`, let a task yield a socket it wants to read
   from, and block in `select()` until the operating system says one is
   ready. That single change turns a toy into the thing asyncio actually is.
4. **Measure `asyncio.to_thread`'s ceiling.** It runs on the loop's default
   executor, which has a bounded number of workers. Raise the number of
   concurrent `to_thread` calls until the time stops improving, find the
   bound, then look up how to change it — and write a paragraph on why the
   default is not simply "unlimited".
5. **Port exercise 3 to `asyncio.Semaphore`.** Twenty concurrent requests is
   fine against your own fixture server and rude against somebody else's API.
   Add a semaphore that allows five at a time, measure the new figure, and
   check it lands where arithmetic says it should. Then explain why a
   semaphore is the right tool here and a `ThreadPoolExecutor(max_workers=5)`
   would be a different thing that happens to look similar.

## Navigation

- **Previous day:** Day 95 — Dates, Times and Time Zones
  (`labs/sections/programming-with-python/day-095-dates-times-and-time-zones/`).
- **Next day:** Day 97 — Logging and Configuration
  (`labs/sections/programming-with-python/day-097-logging-and-configuration/`).
- **Week 14 project:** the week's project directory
  (`labs/sections/programming-with-python/projects/week-14/`), where the
  pipeline you build has both a waiting stage and a computing stage, and has
  to pick correctly for each.
