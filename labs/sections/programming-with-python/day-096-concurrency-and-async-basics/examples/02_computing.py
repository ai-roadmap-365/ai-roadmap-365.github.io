#!/usr/bin/env python3
"""Computing work: four prime counts, four ways, timed.

Run:  python3 examples/02_computing.py

Same code shape as 01_waiting.py. Same number of runs. The only thing that
changed is what the work *is* — and the answer flips completely.

This is the script that costs people weeks when they skip it. Threads made
the waiting work fourteen times faster in the previous script, so threads
get reached for again here, and here they do nothing at all. The reason is
the interpreter lock, and the fix is processes.
"""

from __future__ import annotations

import asyncio
import os
import sys
import sysconfig
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import labkit  # noqa: E402

TASKS = labkit.COMPUTING_TASKS
LIMIT = labkit.DEFAULT_PRIME_LIMIT
REPEATS = 3
LIMITS = [LIMIT] * TASKS


def run_sequential() -> list[int]:
    return [labkit.count_primes(limit) for limit in LIMITS]


def run_threaded() -> list[int]:
    """The same code as the fast version in 01_waiting.py. Watch it not help."""
    with ThreadPoolExecutor(max_workers=TASKS) as pool:
        return list(pool.map(labkit.count_primes, LIMITS))


def run_processes() -> list[int]:
    """One character different from the line above, and a different machine underneath.

    Each worker is a separate operating-system process with its own
    interpreter and its own lock, so four of them genuinely run at once on
    four cores. The price is paid at the edges: starting the processes, and
    pickling the arguments and results across them.
    """
    with ProcessPoolExecutor(max_workers=TASKS) as pool:
        return list(pool.map(labkit.count_primes, LIMITS))


async def _await_them() -> list[int]:
    """Deliberately wrong, and instructive.

    `async def` does not make anything concurrent. There is no `await` inside
    count_primes and there could not be: it never waits for anything. So the
    event loop runs each call to completion before it looks at the next one,
    and asyncio delivers exactly sequential timing with extra ceremony.
    """
    return [labkit.count_primes(limit) for limit in LIMITS]


def run_asyncio() -> list[int]:
    return asyncio.run(_await_them())


def main() -> int:
    free_threaded = sysconfig.get_config_var("Py_GIL_DISABLED")
    print("Day 096 — computing work: 4 prime counts, four ways")
    print(f"python {sys.version.split()[0]}   cpu_count {os.cpu_count()}   "
          f"Py_GIL_DISABLED {free_threaded!r}")
    print(f"each task counts the primes below {LIMIT:,} by trial division; "
          f"{TASKS} tasks; {REPEATS} runs each")
    if not free_threaded:
        print("This interpreter was built WITH the global interpreter lock "
              "(Py_GIL_DISABLED is 0), which is what the numbers below reflect.")
    else:
        print("This interpreter is a free-threaded build (Py_GIL_DISABLED is 1); "
              "the threaded row below is not what a lock-holding build produces.")
    print()

    sequential_samples, sequential_result = labkit.repeat(run_sequential, REPEATS)
    threaded_samples, threaded_result = labkit.repeat(run_threaded, REPEATS)
    process_samples, process_result = labkit.repeat(run_processes, REPEATS)
    asyncio_samples, asyncio_result = labkit.repeat(run_asyncio, REPEATS)

    print("timings")
    sequential = labkit.report("sequential (one at a time)", sequential_samples)
    threaded = labkit.report(f"threads (ThreadPoolExecutor {TASKS})", threaded_samples)
    processes = labkit.report(f"processes (ProcessPoolExecutor {TASKS})", process_samples)
    evented = labkit.report("asyncio (one thread, one loop)", asyncio_samples)
    print()

    print("correctness first")
    expected = [78498 if LIMIT == 1_000_000 else labkit.count_primes(LIMIT)] * TASKS
    for name, got in (
        ("sequential", sequential_result),
        ("threads", threaded_result),
        ("processes", process_result),
        ("asyncio", asyncio_result),
    ):
        print(f"  {name:<12} {got}  correct: {'yes' if got == expected else 'no'}")
    print(f"  there really are {expected[0]:,} primes below {LIMIT:,}")
    print()

    labkit.result_line("computing_sequential_s", sequential)
    labkit.result_line("computing_threaded_s", threaded)
    labkit.result_line("computing_processes_s", processes)
    labkit.result_line("computing_asyncio_s", evented)
    labkit.result_line("computing_threaded_speedup", sequential / threaded)
    labkit.result_line("computing_processes_speedup", sequential / processes)
    labkit.result_line("computing_asyncio_speedup", sequential / evented)
    labkit.shape_line(
        "threads_do_not_help_computing_work",
        sequential / threaded < 1.5,
        f"threads are {sequential / threaded:.2f}x sequential; the claim is < 1.5x",
    )
    labkit.shape_line(
        "processes_do_help_computing_work",
        sequential / processes >= 1.5,
        f"processes are {sequential / processes:.2f}x sequential; the claim is >= 1.5x",
    )
    labkit.shape_line(
        "asyncio_does_not_help_computing_work",
        sequential / evented < 1.5,
        f"asyncio is {sequential / evented:.2f}x sequential; the claim is < 1.5x",
    )
    print()
    print("The one-line rule, earned rather than asserted:")
    print("  waiting work  -> threads or an event loop; the waiting overlaps")
    print("  computing work-> processes; nothing else has more than one interpreter lock")
    print()
    print("Note what processes did NOT give you: a 4x speedup from 4 workers. Starting")
    print("them, pickling to them and pickling back are real costs, and they are paid")
    print("whether or not the work was big enough to deserve them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
