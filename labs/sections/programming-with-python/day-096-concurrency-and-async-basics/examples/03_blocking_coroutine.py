#!/usr/bin/env python3
"""The one rule you must not break, broken on purpose and then repaired.

Run:  python3 examples/03_blocking_coroutine.py

**Never call a blocking function inside a coroutine.**

An event loop is one thread running one callback at a time. A coroutine
gives that thread back at every `await` and at no other moment. So a
coroutine that calls something which blocks — `time.sleep`, a synchronous
HTTP client, a database driver that is not async, a file read on a slow
disk, `requests.get` — does not suspend. It holds the only thread there
is, and every other task on the loop stops dead until it returns.

The failure is quiet. Nothing raises. The program still produces correct
answers. It is simply serial while looking concurrent, which is why this
bug survives code review and is found in production by a latency graph.

The script measures four things:
  1. five blocking sleeps inside coroutines, gathered
  2. the same five with `await asyncio.sleep`, gathered
  3. the same five blocking calls handed to `asyncio.to_thread`
  4. what the blocking coroutine does to an UNRELATED task on the same loop
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import labkit  # noqa: E402

TASKS = 5
NAP = 0.20


# ---------------------------------------------------------------------------
# 1. Broken: `async def` around a blocking call.
# ---------------------------------------------------------------------------


async def blocking_task(index: int) -> int:
    # time.sleep does not yield to the event loop. It parks the whole thread.
    time.sleep(NAP)
    return index


async def all_blocking() -> list[int]:
    return list(await asyncio.gather(*(blocking_task(i) for i in range(TASKS))))


# ---------------------------------------------------------------------------
# 2. Correct: an awaitable sleep.
# ---------------------------------------------------------------------------


async def awaiting_task(index: int) -> int:
    # asyncio.sleep is a coroutine. `await` is the pause point: the loop takes
    # the thread back here and gives it to whichever task is ready next.
    await asyncio.sleep(NAP)
    return index


async def all_awaiting() -> list[int]:
    return list(await asyncio.gather(*(awaiting_task(i) for i in range(TASKS))))


# ---------------------------------------------------------------------------
# 3. The repair for code you cannot change: push it to a thread.
# ---------------------------------------------------------------------------


async def offloaded_task(index: int) -> int:
    # asyncio.to_thread runs the blocking call in a worker thread and gives
    # you a coroutine to await. The blocking still happens — it just happens
    # somewhere that is allowed to block. This is the fix for a synchronous
    # library you do not own and cannot rewrite.
    await asyncio.to_thread(time.sleep, NAP)
    return index


async def all_offloaded() -> list[int]:
    return list(await asyncio.gather(*(offloaded_task(i) for i in range(TASKS))))


# ---------------------------------------------------------------------------
# 4. The collateral damage: what it does to a task that is not even involved.
# ---------------------------------------------------------------------------


async def heartbeat(stop_after: float) -> list[float]:
    """Tick every 10ms and record when each tick actually happened.

    A healthy loop produces ticks about 10ms apart. A loop with a blocked
    task produces a gap the size of the blockage. This is the shape you look
    for in a real service: not an error, a gap.
    """
    started = time.perf_counter()
    ticks: list[float] = []
    while time.perf_counter() - started < stop_after:
        await asyncio.sleep(0.01)
        ticks.append(time.perf_counter() - started)
    return ticks


async def measure_starvation(block: bool) -> float:
    """Return the largest gap between heartbeats while one task runs.

    The `await asyncio.sleep(0.03)` is load-bearing and is worth a sentence,
    because leaving it out is itself a classic asyncio mistake. `create_task`
    only *schedules* the heartbeat; it does not start it. Nothing on a loop
    starts until the currently running coroutine gives the thread back at an
    `await`. Without that line the heartbeat would not have ticked once
    before the blocking call began, and the gap being measured would not
    exist yet.
    """
    beat = asyncio.create_task(heartbeat(NAP * 2))
    await asyncio.sleep(0.03)
    if block:
        await blocking_task(0)
    else:
        await awaiting_task(0)
    ticks = await beat
    gaps = [second - first for first, second in zip(ticks, ticks[1:])]
    return max(gaps) if gaps else 0.0


def main() -> int:
    print("Day 096 — a blocking call inside a coroutine")
    print(f"{TASKS} tasks, each waiting {NAP:.2f}s, gathered on one event loop")
    print()

    blocking_samples, blocking_result = labkit.repeat(lambda: asyncio.run(all_blocking()), 3)
    awaiting_samples, awaiting_result = labkit.repeat(lambda: asyncio.run(all_awaiting()), 3)
    offload_samples, offload_result = labkit.repeat(lambda: asyncio.run(all_offloaded()), 3)

    print("timings")
    blocking = labkit.report("async def + time.sleep  (broken)", blocking_samples)
    awaiting = labkit.report("async def + await asyncio.sleep", awaiting_samples)
    offloaded = labkit.report("async def + asyncio.to_thread", offload_samples)
    print()

    serial_floor = TASKS * NAP
    print("what the numbers mean")
    print(f"  {TASKS} tasks x {NAP:.2f}s = {serial_floor:.2f}s if nothing overlaps.")
    print(f"  The broken version took {blocking:.3f}s, which is the serial floor. It ran")
    print("  one task at a time while the code said gather. Nothing raised.")
    print(f"  Both repairs took about {NAP:.2f}s, which is one task's worth of waiting.")
    print()

    print("correctness — all three produce the same answers, which is the trap")
    for name, got in (
        ("blocking", blocking_result),
        ("awaiting", awaiting_result),
        ("to_thread", offload_result),
    ):
        print(f"  {name:<11} {got}  correct: {'yes' if got == list(range(TASKS)) else 'no'}")
    print()

    print("collateral damage to an unrelated task on the same loop")
    blocked_gap = asyncio.run(measure_starvation(block=True))
    healthy_gap = asyncio.run(measure_starvation(block=False))
    print(f"  largest heartbeat gap while a coroutine BLOCKED : {blocked_gap * 1000:7.1f} ms")
    print(f"  largest heartbeat gap while a coroutine AWAITED : {healthy_gap * 1000:7.1f} ms")
    print("  The heartbeat asked for a tick every 10 ms and had nothing to do with the")
    print("  sleeping task. It was starved anyway, because there is only one thread.")
    print()

    labkit.result_line("blocking_gathered_s", blocking)
    labkit.result_line("awaiting_gathered_s", awaiting)
    labkit.result_line("to_thread_gathered_s", offloaded)
    labkit.result_line("blocking_vs_await_speedup", blocking / awaiting)
    labkit.result_line("blocking_vs_to_thread_speedup", blocking / offloaded)
    labkit.result_line("blocked_heartbeat_gap_ms", blocked_gap * 1000)
    labkit.result_line("healthy_heartbeat_gap_ms", healthy_gap * 1000)
    labkit.shape_line(
        "blocking_in_a_coroutine_serialises_the_loop",
        blocking >= serial_floor * 0.9,
        f"took {blocking:.3f}s against a serial floor of {serial_floor:.2f}s",
    )
    labkit.shape_line(
        "await_asyncio_sleep_repairs_it",
        blocking / awaiting >= 2.5,
        f"awaiting is {blocking / awaiting:.1f}x faster; the claim is >= 2.5x",
    )
    labkit.shape_line(
        "to_thread_repairs_it_for_code_you_cannot_change",
        blocking / offloaded >= 2.5,
        f"to_thread is {blocking / offloaded:.1f}x faster; the claim is >= 2.5x",
    )
    labkit.shape_line(
        "blocking_starves_an_unrelated_task",
        blocked_gap >= healthy_gap * 3,
        f"gap {blocked_gap * 1000:.1f} ms against {healthy_gap * 1000:.1f} ms when healthy",
    )
    print()
    print("How to find this in code you did not write: any call inside an `async def`")
    print("that is not preceded by `await` and is not obviously pure computation is a")
    print("suspect. `time.sleep`, `requests.get`, `open(...).read()` on a network mount,")
    print("and every synchronous database driver are the usual four.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
