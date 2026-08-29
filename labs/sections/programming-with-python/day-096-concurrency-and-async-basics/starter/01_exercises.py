"""Day 096 starter — eight exercises. This is where YOUR work happens.

Read `starter/00_brief.md` first. Then run:

    bash starter/02_check.sh

It will say `0 of 8 exercises complete.` and tell you which. Work down the
list, re-running the checker as you go. The checker never looks at how you
wrote a function — only at whether it behaves correctly and, where the
point of the exercise is speed, whether it is actually faster.

Everything you need is in the standard library and in `examples/labkit.py`,
which is imported for you below. The pieces of labkit you will want:

    labkit.fetch(url)              blocking fetch, returns the body as str
    labkit.fetch_async(url)        coroutine fetch, must be awaited
    labkit.count_primes(limit)     CPU-bound, returns an int
    labkit.urls(base, count)       build the list of request URLs

Do not change any function's name or signature: the checker calls them.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

import labkit  # noqa: E402,F401  (imported for you; every exercise below uses it)


# ---------------------------------------------------------------------------
# Exercise 1 — the baseline. Fetch every URL, one after another.
#
# Use labkit.fetch on each URL in turn and return the bodies in the same
# order as the URLs. A list comprehension is enough. This is deliberately
# the slow one: you need it to measure the others against.
# ---------------------------------------------------------------------------
def fetch_all_sequentially(urls: list[str]) -> list[str]:
    raise NotImplementedError("Exercise 1: return [labkit.fetch(u) for u in urls]")


# ---------------------------------------------------------------------------
# Exercise 2 — the same work with threads, and it must actually be faster.
#
# Use concurrent.futures.ThreadPoolExecutor with max_workers=workers, and
# its .map method, which returns results in INPUT order rather than
# completion order. Wrap the executor in a `with` block so the pool shuts
# down cleanly.
#
# The checker requires this to be at least 2.5x faster than exercise 1 on
# the same URLs — a real speed-up, not just a different spelling.
# ---------------------------------------------------------------------------
def fetch_all_with_threads(urls: list[str], workers: int) -> list[str]:
    raise NotImplementedError("Exercise 2: use ThreadPoolExecutor(max_workers=workers).map")


# ---------------------------------------------------------------------------
# Exercise 3 — the same work on one thread with an event loop.
#
# This is an ordinary def, not an async def. Inside it, define a coroutine
# (or use asyncio.gather directly) that awaits labkit.fetch_async for every
# URL, and drive it with asyncio.run. Return the bodies in URL order —
# asyncio.gather preserves the order of its arguments.
#
# The checker requires this to be at least 2.5x faster than exercise 1.
# ---------------------------------------------------------------------------
def fetch_all_with_asyncio(urls: list[str]) -> list[str]:
    raise NotImplementedError("Exercise 3: asyncio.run over asyncio.gather(*fetch_async(u))")


# ---------------------------------------------------------------------------
# Exercise 4 — CPU-bound work with threads. It will NOT be faster.
#
# Same shape as exercise 2, but map labkit.count_primes over `limits`.
# Return the counts in input order.
#
# The checker only requires the ANSWERS to be right here. It then measures
# the speed-up and prints it, so you can see for yourself that threads did
# nothing for work that never waits.
# ---------------------------------------------------------------------------
def count_primes_with_threads(limits: list[int], workers: int) -> list[int]:
    raise NotImplementedError("Exercise 4: ThreadPoolExecutor over labkit.count_primes")


# ---------------------------------------------------------------------------
# Exercise 5 — the same CPU work with processes, and this one must be faster.
#
# Change ThreadPoolExecutor to ProcessPoolExecutor. That is the whole edit.
# It works because labkit.count_primes is a module-level function, so the
# child processes can import it; a lambda or a closure would fail to pickle.
#
# The checker requires this to be at least 1.4x faster than the sequential
# version of the same work.
# ---------------------------------------------------------------------------
def count_primes_with_processes(limits: list[int], workers: int) -> list[int]:
    raise NotImplementedError("Exercise 5: ProcessPoolExecutor over labkit.count_primes")


# ---------------------------------------------------------------------------
# Exercise 6 — repair a blocking call inside a coroutine.
#
# You are given a list of nap lengths in seconds and must wait all of them
# CONCURRENTLY, using only the blocking time.sleep — imagine it is a
# synchronous database driver you do not own.
#
# Writing `async def nap(n): time.sleep(n)` and gathering them does not
# work: it takes sum(naps), because time.sleep never gives the loop back.
# Use `await asyncio.to_thread(time.sleep, n)` instead, gather those, and
# return the nap lengths in input order.
#
# The checker requires the whole thing to finish in well under sum(naps).
# ---------------------------------------------------------------------------
def wait_without_blocking_the_loop(naps: list[float]) -> list[float]:
    raise NotImplementedError("Exercise 6: gather asyncio.to_thread(time.sleep, n) for each nap")


# ---------------------------------------------------------------------------
# Exercise 7 — a counter that loses nothing.
#
# Start `threads` threads. Each increments one shared counter `per_thread`
# times. Return the final value, which must be exactly threads * per_thread.
#
# The checker runs your function with the interpreter's thread-switch
# interval turned down to a microsecond, which makes an unprotected
# read-add-write lose increments on every single run. A threading.Lock held
# around the read and the write is the direct answer. Accumulating into a
# local variable per thread and adding the subtotals at the end is the
# better one, and also passes.
# ---------------------------------------------------------------------------
def counter_that_loses_nothing(threads: int, per_thread: int) -> int:
    raise NotImplementedError("Exercise 7: protect the read-add-write, or stop sharing it")


# ---------------------------------------------------------------------------
# Exercise 8 — write the event loop.
#
# `tasks` is a list of (name, generator) pairs. Each generator yields to
# pause and eventually stops. Run them round-robin: take the first task,
# advance it exactly one step with next(), and if it has not finished, put
# it at the BACK of the queue. Return the list of names in the order they
# were stepped.
#
# collections.deque with popleft() and append() is the natural structure.
# A generator that has finished raises StopIteration from next(); catch it
# and drop that task.
#
# With three tasks of 3, 2 and 1 steps the answer is:
#   ['a', 'b', 'c', 'a', 'b', 'a']
# ---------------------------------------------------------------------------
def round_robin(tasks: list[tuple[str, object]]) -> list[str]:
    raise NotImplementedError("Exercise 8: a deque, popleft, next(task), append unless finished")
