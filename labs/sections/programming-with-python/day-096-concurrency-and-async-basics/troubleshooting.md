# Troubleshooting — Day 096

Grouped by the message you actually see, or by the symptom when there is no
message. The last section is the one to read if your numbers disagree with
the captured ones, because on this day that is often correct rather than
broken.

## Errors with a message

### `Can't pickle <function <lambda> at 0x...>` / `AttributeError: Can't get attribute`

From `ProcessPoolExecutor`. Child processes do not inherit your function —
they import the module it lives in and look the name up. So the target must
be a module-level function with a real name. A lambda, a closure, a function
defined inside another function, and a method of an object that itself
cannot be pickled will all fail here.

This is why `examples/labkit.py` defines `count_primes` at module level, and
why exercise 5 works by changing one word rather than restructuring anything.

### `RuntimeError: asyncio.run() cannot be called from a running event loop`

`asyncio.run` is the boundary between synchronous code and the loop. It
creates a loop, runs one coroutine to completion, and closes the loop. Call
it once, from ordinary synchronous code, at the top.

Inside a coroutine you already have a loop, so you `await` instead. If you
need to run a coroutine from synchronous code that is itself running on a
loop's thread, you have an architecture problem rather than a syntax one.

### `RuntimeWarning: coroutine 'fetch_async' was never awaited`

You called a coroutine function and did nothing with the result. Calling
`fetch_async(url)` does not fetch anything: it builds a coroutine object.
The work happens when it is awaited, or when it is handed to
`asyncio.gather`, `asyncio.TaskGroup.create_task` or `asyncio.create_task`.

This warning is one of the friendlier things asyncio does. The silent version
of the same mistake is described under "Symptoms with no message" below.

### `TypeError: object list can't be used in 'await' expression`

You awaited something that is not awaitable. Common cause: `await` in front
of a list comprehension of coroutines rather than in front of
`asyncio.gather(*coroutines)`.

### `SyntaxError` on `async with asyncio.timeout(...)` or on `except*`

Your interpreter predates 3.11. `asyncio.timeout`, `asyncio.TaskGroup` and
`except*` all arrived in Python 3.11. Check with `python3 --version` and, if
you have a newer one installed elsewhere:

```bash
PYTHON=/path/to/python3 bash tests/run_tests.sh
```

### `OSError: [Errno 48] Address already in use`

Should not happen here: the fixture server binds to port 0, which asks the
operating system for a free ephemeral port. If you see it, you have modified
`fixture_server` to use a fixed port. Put the `0` back.

### `at least two usable CPUs` — the suite exits early

The process comparison cannot mean anything on a single-CPU machine, so the
suite says so instead of reporting a ratio that would be noise. Everything
else in the lab still runs and still teaches; run the individual example
scripts directly.

## Symptoms with no message

### A coroutine never runs, and nothing warns you

You used `asyncio.create_task(...)` and then never awaited anything before
the function returned. `create_task` *schedules*; it does not start. Nothing
on a loop starts until the currently running coroutine gives the thread back
at an `await`.

This exact bug is in `examples/03_blocking_coroutine.py` as a commented
demonstration — the `await asyncio.sleep(0.03)` in `measure_starvation` is
there for this reason, and the comment says so. It was also a real bug during
the writing of this lab: the first version of that function measured no
starvation at all because the heartbeat had not started yet.

### Your async code is correct and exactly as slow as the sequential version

Something in the call path is blocking. Symptoms: total time equals the sum
of the parts rather than the maximum, and CPU usage is near zero throughout.

Look inside every `async def` for a call that is not preceded by `await`. The
usual four are `time.sleep`, `requests.get` (or any synchronous HTTP client),
a synchronous database driver, and a file read from a slow or network
filesystem. Wrap the offender in `await asyncio.to_thread(...)`.

### The threaded version is no faster than the sequential one

If the work never waits, **this is the correct result**, and reproducing it
is exercise 4. Threads overlap waiting. They cannot overlap Python bytecode
execution, because only one thread holds the interpreter lock at a time. Use
processes.

If the work *does* wait and threads still do not help, check that the thing
being waited on can actually serve more than one caller at once. A fixture
server that handled one request at a time would serialise every client — this
is why `labkit._WaitServer` extends `ThreadingHTTPServer`, and there is a
comment there saying so.

### The process version is no faster, or is slower

Three usual causes, in order of likelihood:

1. **The tasks are too small.** Starting a process and pickling arguments to
   it costs real milliseconds, and on macOS and Windows the spawn start
   method re-imports your module in every child. If each task takes 2 ms,
   the overhead is the entire measurement. Extension exercise 1 finds the
   crossover point deliberately.
2. **The arguments or results are large.** Everything crossing a process
   boundary is pickled and copied. Sending a large array to a worker and
   getting a large array back can cost more than the computation.
3. **Too few cores.** Check `python3 -c "import os; print(os.cpu_count())"`.

### `8 of 8` will not appear even though every answer looks right

Exercises 2, 3 and 5 are judged on speed as well as correctness, because
being correct was never the hard part. The checker prints both the ratio it
measured and the ratio it needs:

```text
[open] 2. fetch_all_with_threads
       1.0x faster than sequential (0.658s); needs >= 2.5x
```

A ratio near 1.0 means your "concurrent" version is doing the work in
sequence. This is exactly the sabotage the test suite performs on the
reference answer to prove the checker is not vacuous.

### The unsafe counter does not lose any increments for you

**This is a real observation, not a broken lab, and it is worth understanding
rather than working around.**

On the authoring machine — CPython 3.14.0, macOS, arm64 — the unprotected
read-add-write counter lost **zero** increments in 20 dedicated trials at the
interpreter's default 5 ms thread switch interval. The race is genuinely
there; the window is simply narrower than one thread's time slice, so the
switch rarely lands inside it.

That is why `examples/04_race.py` reports the default-interval result first
and honestly, and only then drops the switch interval to 1 microsecond, at
which point the same unchanged code loses roughly 70% of its increments on
every single run. Nothing about the bug changed — only how often the
interpreter considers handing the thread to somebody else.

The lesson to take is not "races are rare". It is that **a concurrency bug's
visibility is a property of timing, not of correctness**, so you cannot test
your way to confidence about one. You reason about it, or you remove the
shared mutable state so there is nothing to reason about.

If you want to make it land at the default interval, that is extension
exercise 2.

### The suite passes but takes much longer than 40 seconds

Expected on a slower machine, and not a failure: the sequential baselines are
real waiting and real computing. The CPU-bound section is the slowest part —
four prime counts, four ways, three times each. Nothing in the suite has a
wall-clock deadline, precisely so that a slow machine cannot fail it.

### A `__pycache__` directory keeps appearing

Both harness scripts set `PYTHONDONTWRITEBYTECODE=1`, so this only happens if
you ran an example by hand without it. The suite clears any pre-existing one
at the start and asserts that none exists at the end, so it is testing its own
behaviour rather than your shell history. To clear it:

```bash
find . -type d -name __pycache__ -prune -exec rm -rf -- {} +
```

### The deadlock demonstration reports `deadlocked: no`

The two threads did not overlap, so the cycle never formed. `04_race.py` uses
a `threading.Barrier` to guarantee both threads hold one lock before either
asks for the second, which makes it reliable — if you have modified that
part, put the barrier back.

Note the barrier belongs only in the broken version. Adding one to the
*fixed* version makes it hang, because a thread holding the first lock would
wait at the barrier for a thread that cannot reach the barrier until it gets
that same first lock. That is a genuine deadlock introduced by the act of
trying to force an interleaving, and the comment in the file explains it.

## When your numbers disagree with the captured ones

Read `expected-output/FIELDS.md` first. It lists exactly which values must
match on every machine — the prime counts, the counter totals, the
scheduler's interleaving order, the number of surviving tasks — and which are
expected to differ, which is every single elapsed time.

If a *shape* disagrees — threads speeding up CPU-bound work, or processes not
speeding it up — check `Py_GIL_DISABLED` first:

```bash
python3 -c "import sysconfig; print(sysconfig.get_config_var('Py_GIL_DISABLED'))"
```

A `1` means you are on a free-threaded build (PEP 703), where threads
genuinely can execute Python bytecode in parallel and the "threads do not
help" result is expected **not** to hold. The suite detects this and skips
that one check with a printed note. Every other result in the lab stands.
