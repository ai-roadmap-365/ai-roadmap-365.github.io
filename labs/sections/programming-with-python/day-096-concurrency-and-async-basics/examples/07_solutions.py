"""Reference answers to the eight exercises in starter/01_exercises.py.

Read this AFTER you have tried. Every function has the same name and
signature as the starter's, so the checker can be pointed at either:

    bash starter/02_check.sh examples/07_solutions.py

Each answer is the shortest one that is actually correct, with a note on
the mistake that version exists to avoid.
"""

from __future__ import annotations

import asyncio
import sys
import threading
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import labkit  # noqa: E402


def fetch_all_sequentially(urls: list[str]) -> list[str]:
    """The baseline. Correct, obvious, and pays every wait end to end."""
    return [labkit.fetch(url) for url in urls]


def fetch_all_with_threads(urls: list[str], workers: int) -> list[str]:
    """Threads help because a blocked socket read releases the interpreter lock.

    `pool.map` returns results in INPUT order. `as_completed` would return
    them in finish order, which is what you want for a progress bar and not
    what you want when the caller expects a list lined up with its input.
    """
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(labkit.fetch, urls))


def fetch_all_with_asyncio(urls: list[str]) -> list[str]:
    """One thread, one loop, N coroutines suspended at await.

    `asyncio.gather` preserves argument order in its result list. Note this
    is an ordinary def: `asyncio.run` is the boundary between synchronous
    code and the loop, and calling it from inside a running loop is an error.
    """

    async def gather_all() -> list[str]:
        return list(await asyncio.gather(*(labkit.fetch_async(url) for url in urls)))

    return asyncio.run(gather_all())


def count_primes_with_threads(limits: list[int], workers: int) -> list[int]:
    """Identical to the fast version above, and it will not be faster.

    Nothing here waits, so nothing releases the interpreter lock for long
    enough to matter. The answers are right; the wall clock is unmoved.
    """
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(labkit.count_primes, limits))


def count_primes_with_processes(limits: list[int], workers: int) -> list[int]:
    """One word changed, and now there are four interpreter locks.

    `labkit.count_primes` is a module-level function, which is why the child
    processes can find it. A lambda, a closure, or a locally defined function
    raises a pickling error here — the most common first failure with
    ProcessPoolExecutor, and one worth meeting deliberately.
    """
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(labkit.count_primes, limits))


def wait_without_blocking_the_loop(naps: list[float]) -> list[float]:
    """The repair for a synchronous library you cannot rewrite.

    `asyncio.to_thread(fn, *args)` returns a coroutine that runs fn in a
    worker thread. The blocking still happens; it just happens somewhere
    that is allowed to block, so the loop keeps its thread.
    """

    async def nap(seconds: float) -> float:
        await asyncio.to_thread(time.sleep, seconds)
        return seconds

    async def all_naps() -> list[float]:
        return list(await asyncio.gather(*(nap(seconds) for seconds in naps)))

    return asyncio.run(all_naps())


def counter_that_loses_nothing(threads: int, per_thread: int) -> int:
    """The better answer: do not share the mutable state at all.

    Each worker counts into a local variable that no other thread can see,
    and posts one subtotal at the end. There is exactly one shared mutation
    per thread instead of `per_thread` of them, and it is under a lock.

    The direct answer — one shared counter with `with lock:` around every
    read-add-write — is also correct and also passes. It is roughly an order
    of magnitude slower here, because it takes and releases a lock several
    hundred thousand times to protect an addition.
    """
    lock = threading.Lock()
    total = 0

    def worker() -> None:
        nonlocal total
        subtotal = 0
        for _ in range(per_thread):
            subtotal += 1
        with lock:
            total += subtotal

    workers = [threading.Thread(target=worker) for _ in range(threads)]
    for thread in workers:
        thread.start()
    for thread in workers:
        thread.join()
    return total


def round_robin(tasks: list[tuple[str, object]]) -> list[str]:
    """An event loop, minus everything that is not the loop.

    A ready queue, take the front one, advance it exactly one step, put it
    at the back unless it has finished. That is scheduling. Everything
    asyncio adds is about deciding WHEN a task becomes ready again.
    """
    ready = deque(tasks)
    order: list[str] = []
    while ready:
        name, task = ready.popleft()
        try:
            next(task)  # type: ignore[arg-type]
        except StopIteration:
            continue  # finished: do not put it back
        order.append(name)
        ready.append((name, task))
    return order
