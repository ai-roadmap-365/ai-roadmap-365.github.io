#!/usr/bin/env python3
"""Waiting work: twenty requests, three ways, timed.

Run:  python3 examples/01_waiting.py

Every request goes to a fixture server on 127.0.0.1 that sleeps exactly
0.100 seconds before answering. No network is involved and no rate limit
can distort the result: the work is *waiting*, and the amount of waiting
is a number this script chose.

The question the script answers is the only question that matters when you
are picking a concurrency model: **is this work waiting, or is it
computing?** This half is waiting. Watch what threads do to it.
"""

from __future__ import annotations

import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import labkit  # noqa: E402

REQUESTS = labkit.WAITING_REQUESTS
WORKERS = 20
REPEATS = 3


def run_sequential(base: str) -> list[str]:
    """One at a time. The simplest thing, and the slowest by a mile."""
    return [labkit.fetch(url) for url in labkit.urls(base, REQUESTS)]


def run_threaded(base: str) -> list[str]:
    """Twenty threads, each blocked in a socket read.

    A blocked socket read releases the interpreter lock, so nineteen other
    threads are free to run while any one of them waits. That single fact is
    why threads help here and will not help the next script along.

    `executor.map` returns results in the order the inputs were given, not
    the order they finished, which is usually what you wanted anyway.
    """
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(labkit.fetch, labkit.urls(base, REQUESTS)))


async def _gather(base: str) -> list[str]:
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(labkit.fetch_async(url)) for url in labkit.urls(base, REQUESTS)]
    return [task.result() for task in tasks]


def run_asyncio(base: str) -> list[str]:
    """One thread, one event loop, twenty coroutines suspended at `await`.

    `asyncio.run` creates the loop, runs the coroutine to completion and
    closes the loop. A TaskGroup (Python 3.11 and later) is the modern way
    to say "these run together, and if one raises, cancel the rest".
    """
    return asyncio.run(_gather(base))


def main() -> int:
    print("Day 096 — waiting work: 20 requests, three ways")
    print(f"fixture server sleeps {labkit.DEFAULT_DELAY:.3f}s per request; "
          f"{REQUESTS} requests; thread pool of {WORKERS}; {REPEATS} runs each")
    print()

    with labkit.fixture_server() as base:
        # A first request that is not measured, so that the cost of importing
        # ssl-free urllib machinery and warming the server does not land on
        # the sequential column and flatter the other two.
        labkit.fetch(base + "/warmup")

        sequential_samples, sequential_bodies = labkit.repeat(
            lambda: run_sequential(base), REPEATS
        )
        threaded_samples, threaded_bodies = labkit.repeat(lambda: run_threaded(base), REPEATS)
        asyncio_samples, asyncio_bodies = labkit.repeat(lambda: run_asyncio(base), REPEATS)

    print("timings")
    sequential = labkit.report("sequential (one at a time)", sequential_samples)
    threaded = labkit.report(f"threads (ThreadPoolExecutor {WORKERS})", threaded_samples)
    evented = labkit.report("asyncio (one thread, one loop)", asyncio_samples)
    print()

    floor = REQUESTS * labkit.DEFAULT_DELAY
    print("what the numbers mean")
    print(f"  {REQUESTS} requests x {labkit.DEFAULT_DELAY:.3f}s of waiting = {floor:.3f}s of "
          "waiting in total.")
    print("  Sequential pays all of it end to end. The other two overlap it, so the floor")
    print(f"  becomes roughly one request: {labkit.DEFAULT_DELAY:.3f}s plus overhead.")
    print()

    print("correctness first — a fast wrong answer is not an answer")
    for name, bodies in (
        ("sequential", sequential_bodies),
        ("threads", threaded_bodies),
        ("asyncio", asyncio_bodies),
    ):
        assert isinstance(bodies, list)
        ok = len(bodies) == REQUESTS and all("waited 0.100s" in b for b in bodies)
        print(f"  {name:<12} {len(bodies)} bodies, all well formed: {'yes' if ok else 'no'}")
    print(f"  and the order is preserved: first body is for {sequential_bodies[0].split()[-1]}")
    print()

    labkit.result_line("waiting_sequential_s", sequential)
    labkit.result_line("waiting_threaded_s", threaded)
    labkit.result_line("waiting_asyncio_s", evented)
    labkit.result_line("waiting_threaded_speedup", sequential / threaded)
    labkit.result_line("waiting_asyncio_speedup", sequential / evented)
    labkit.shape_line(
        "threads_help_waiting_work",
        sequential / threaded >= 4.0,
        f"threads are {sequential / threaded:.1f}x faster than sequential; the claim is >= 4x",
    )
    labkit.shape_line(
        "asyncio_helps_waiting_work",
        sequential / evented >= 4.0,
        f"asyncio is {sequential / evented:.1f}x faster than sequential; the claim is >= 4x",
    )
    print()
    print("These seconds are one machine on one day. The SHAPE is what travels:")
    print("waiting work overlaps, so both threads and an event loop collapse it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
