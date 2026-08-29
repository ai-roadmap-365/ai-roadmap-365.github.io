# What must match, and what is allowed to differ

Every file in this directory was captured from a real run on the authoring
machine on 2026-08-16:

- macOS 26.5.2, Apple Silicon (arm64), 14 logical CPUs
- Python 3.14.0, standard library only
- `Py_GIL_DISABLED` is `0` — this is a normal build **with** the global
  interpreter lock, not a free-threaded one
- default thread switch interval `0.005` s
- bash 3.2.57

This is the most timing-heavy lab in the section, so it needs the clearest
statement of what a "correct" run looks like on somebody else's machine.

## The rule

**No number of seconds in any of these captures is a claim about your
machine.** They are a record of one machine on one day. What must reproduce
is the *shape*: which approach is faster than which, and by roughly how
much. `tests/run_tests.sh` asserts only shapes, with wide margins, which is
why it passes on hardware quite unlike the machine above.

## Must match exactly

| Value | Where | Why it cannot vary |
| --- | --- | --- |
| `41538` primes below 500,000 | `computing.txt` | Arithmetic. A different answer is a bug |
| `33860` primes below 400,000 | `starter-progress.txt` | Same |
| `400,000` for the locked and queued counters | `race.txt` | 8 x 50,000, exactly. Losing even one is the failure |
| `alpha beta gamma alpha beta alpha` | `scheduler.txt` | Round-robin over 3, 2 and 1 steps has one correct order |
| `greedy greedy greedy greedy polite polite polite` | `scheduler.txt` | A task that never yields cannot be interleaved |
| `20 bodies, all well formed: yes` three times | `waiting.txt` | All three approaches must return all twenty |
| `2 of 3 finished` with `gather` | `timeouts.txt` | `return_exceptions=True` has defined behaviour |
| `2 sibling(s) were cancelled` with `TaskGroup` | `timeouts.txt` | Same |
| `0 of 8` then `8 of 8` | `starter-progress.txt` | The checker's two end states |
| `58 checks, 0 failure(s).` | `test-run.txt` | The suite's own result line |

## Must hold, but the numbers will differ

| Shape | Captured here | Margin the tests use |
| --- | --- | --- |
| Threads beat sequential on **waiting** work | 12.2x | at least 4x |
| asyncio beats sequential on **waiting** work | 17.9x | at least 4x |
| Threads do **not** beat sequential on **computing** work | 1.01x | must be below 1.5x |
| Processes **do** beat sequential on computing work | 2.89x | at least 1.5x |
| asyncio does not beat sequential on computing work | 0.98x | must be below 1.5x |
| `await asyncio.sleep` beats a blocking coroutine | 5.1x | at least 2.5x |
| `asyncio.to_thread` beats a blocking coroutine | 4.9x | at least 2.5x |
| A blocked loop starves an unrelated task | 211 ms against 11 ms | at least 3x the healthy gap |
| A timeout fires at the budget, not at the work | 0.1511 s for a 0.15 s budget | below 0.35 s and above 0.10 s |

Note the asyncio row on computing work: it came out at **0.98x**, meaning
marginally *slower* than plain sequential code. That is not an error and it
has not been rounded away. An event loop that never gets an `await` is
sequential execution plus the cost of running a loop.

## Expected to differ, and why

- **Every elapsed time and every `spread` figure.** A slower CPU raises the
  computing numbers; the waiting numbers are pinned near `0.100 s` per
  request by the fixture server's sleep rather than by your hardware.
- **The process speed-up.** Captured at 2.89x with 4 workers on 14 cores. On
  a 2-core machine expect closer to 1.5-2x, which still passes. On a single
  core the comparison is meaningless, and `tests/run_tests.sh` fails early
  with a clear message rather than pretending otherwise.
- **The thread speed-up on waiting work.** Bounded by the pool size (20) and
  by how quickly your machine can start 20 threads and open 20 sockets.
- **`race_lost_at_tight_interval`.** Captured at 290,878 of 400,000 lost. The
  count varies by tens of thousands between runs; only "greater than zero,
  and by a wide margin" is asserted.

## The one that may legitimately differ in KIND

`race_lost_at_default_interval` is **0** in this capture, across three runs
at the interpreter's normal 5 ms switch interval — and it was 0 across 20
further dedicated trials of the identical configuration during authoring. On a busier machine, a different CPython
version, or a machine with fewer cores, you may well see it lose increments.

Both outcomes are correct observations, and neither is asserted by the test
suite. The unsafe counter is broken either way; the default switch interval
merely determines how often the breakage is visible. `examples/04_race.py`
prints whichever you get and explains it, and the lesson's "Examples in
practice" section discusses why.

## Windows

Not tested, and no output is claimed for it. Use WSL and follow the Linux
path. Two things would differ on native Windows even so: the shell scripts
need bash, and `ProcessPoolExecutor` uses the spawn start method there — as
it already does on macOS, which is why the process start-up cost visible in
`computing.txt` is representative rather than optimistic.
