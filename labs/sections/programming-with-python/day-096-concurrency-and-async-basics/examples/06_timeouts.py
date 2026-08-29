#!/usr/bin/env python3
"""Cancellation, timeouts, and what gather does that TaskGroup does not.

Run:  python3 examples/06_timeouts.py

Starting concurrent work is the easy half. Stopping it is where the bugs
are. Four things are measured here, all against the fixture server so the
"slow" request is slow by arrangement rather than by luck:

  1. asyncio.timeout around a request that will not finish in time
  2. what cancellation actually is — a CancelledError raised INSIDE the
     task at its next await, which means cleanup in a finally block runs
  3. asyncio.gather with return_exceptions, where one failure does not
     stop the others and you get the exception back as a value
  4. asyncio.TaskGroup, where one failure DOES cancel its siblings

The difference in 3 and 4 is a design decision, not a style preference.
"Fetch nine things and tell me which ones worked" wants gather. "Do these
four things or do none of them" wants a TaskGroup.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import labkit  # noqa: E402

SLOW = 0.40
BUDGET = 0.15


async def slow_fetch(base: str, tag: str, log: list[str]) -> str:
    """A request that takes longer than the caller's patience.

    The finally block is the part worth studying. Cancellation in asyncio is
    an exception raised inside the coroutine at its next suspension point,
    so ordinary Python cleanup works: finally runs, context managers exit,
    connections close. It is not a kill.
    """
    log.append(f"{tag} started")
    try:
        return await labkit.fetch_async(f"{base}/slow/{tag}")
    except asyncio.CancelledError:
        log.append(f"{tag} received CancelledError")
        raise  # re-raise: swallowing it is how you get a task that will not die
    finally:
        log.append(f"{tag} cleaned up")


async def failing_task(tag: str, log: list[str]) -> str:
    await asyncio.sleep(0.02)
    log.append(f"{tag} about to fail")
    raise ValueError(f"{tag} could not be fetched")


async def steady_task(tag: str, seconds: float, log: list[str]) -> str:
    try:
        await asyncio.sleep(seconds)
        log.append(f"{tag} finished")
        return f"{tag} ok"
    except asyncio.CancelledError:
        log.append(f"{tag} was cancelled")
        raise


async def demo_timeout(base: str) -> tuple[bool, list[str], float]:
    log: list[str] = []
    timed_out = False
    start = asyncio.get_running_loop().time()
    try:
        async with asyncio.timeout(BUDGET):
            await slow_fetch(base, "report", log)
    except TimeoutError:
        timed_out = True
    return timed_out, log, asyncio.get_running_loop().time() - start


async def demo_gather() -> tuple[list[object], list[str]]:
    log: list[str] = []
    results = await asyncio.gather(
        steady_task("a", 0.05, log),
        failing_task("b", log),
        steady_task("c", 0.10, log),
        return_exceptions=True,
    )
    return list(results), log


async def demo_taskgroup() -> tuple[list[str], list[str]]:
    log: list[str] = []
    messages: list[str] = []
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(steady_task("a", 0.05, log))
            group.create_task(failing_task("b", log))
            group.create_task(steady_task("c", 0.50, log))
    except* ValueError as group_error:
        messages = [str(error) for error in group_error.exceptions]
    return messages, log


async def main_async() -> int:
    with labkit.fixture_server(delay=SLOW) as base:
        print("Day 096 — cancellation and timeouts")
        print(f"the fixture server now sleeps {SLOW:.2f}s; the caller's budget is "
              f"{BUDGET:.2f}s")
        print()

        print("1. asyncio.timeout around work that will not finish in time")
        timed_out, timeout_log, elapsed = await demo_timeout(base)
        print(f"   TimeoutError raised: {'yes' if timed_out else 'no'}")
        print(f"   gave up after {elapsed:.3f}s, not after {SLOW:.2f}s")
        for line in timeout_log:
            print(f"   log: {line}")
        print("   Cancellation is an exception delivered inside the task, so the")
        print("   finally block ran and the socket was closed. Nothing leaked.")
        print()

        print("2. asyncio.gather(return_exceptions=True): one failure, others survive")
        gathered, gather_log = await demo_gather()
        for index, item in enumerate(gathered):
            kind = type(item).__name__ if isinstance(item, BaseException) else "result"
            print(f"   [{index}] {kind:<10} {item}")
        for line in gather_log:
            print(f"   log: {line}")
        survivors = sum(1 for item in gathered if not isinstance(item, BaseException))
        print(f"   {survivors} of {len(gathered)} finished; the failure came back as a value")
        print()

        print("3. asyncio.TaskGroup: one failure cancels its siblings")
        messages, group_log = await demo_taskgroup()
        for message in messages:
            print(f"   caught in the ExceptionGroup: {message}")
        for line in group_log:
            print(f"   log: {line}")
        cancelled = [line for line in group_log if "cancelled" in line]
        print(f"   {len(cancelled)} sibling(s) were cancelled rather than left running")
        print("   Task c asked for half a second and never got it. With gather it")
        print("   would have run to completion, doing work nobody was going to use.")
        print()

        labkit.result_line("timeout_elapsed_s", elapsed)
        labkit.result_line("timeout_budget_s", BUDGET)
        labkit.result_line("gather_survivors", float(survivors))
        labkit.result_line("taskgroup_cancelled_siblings", float(len(cancelled)))
        labkit.shape_line(
            "timeout_fires_at_the_budget_not_at_the_work",
            timed_out and elapsed < SLOW,
            f"gave up after {elapsed:.3f}s with a budget of {BUDGET:.2f}s and "
            f"work of {SLOW:.2f}s",
        )
        labkit.shape_line(
            "cancellation_runs_the_finally_block",
            any("cleaned up" in line for line in timeout_log),
            "the cancelled task's finally block appears in the log above",
        )
        labkit.shape_line(
            "gather_lets_siblings_finish",
            survivors == 2,
            f"{survivors} of 3 completed despite one raising",
        )
        labkit.shape_line(
            "taskgroup_cancels_siblings",
            len(cancelled) >= 1,
            f"{len(cancelled)} sibling(s) cancelled when one task raised",
        )
        print()
        print("Choosing between them: gather when partial success is a real answer,")
        print("TaskGroup when it is not. TaskGroup also refuses to let you leak a task,")
        print("because the `async with` block does not exit until every child is done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main_async()))
