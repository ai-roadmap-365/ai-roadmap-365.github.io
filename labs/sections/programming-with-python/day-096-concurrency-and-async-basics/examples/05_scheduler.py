#!/usr/bin/env python3
"""An event loop in forty lines, so `async`/`await` stops being magic.

Run:  python3 examples/05_scheduler.py

Strip asyncio of its socket handling, its thread pools, its cancellation
machinery and its exception groups, and what is left is this: a queue of
functions that can pause, and a loop that keeps taking the next one.

Python has had functions that can pause since generators arrived in 2001.
A generator runs until `yield`, hands control back to whoever called
`next()` on it, and remembers exactly where it was. That is the entire
mechanism underneath a coroutine. `async def` and `await` are a dedicated
syntax for the same idea with a nicer set of rules; PEP 492 added them in
Python 3.5, and coroutines were built on generators before that.

So: `yield` is our `await`, a generator function is our `async def`, and
the class below is our event loop. Once you have written the loop, the
question "why did my whole server freeze?" answers itself — look at the
loop and ask what happens if `next(task)` takes two seconds to return.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


# ---------------------------------------------------------------------------
# The scheduler. This is the whole thing.
# ---------------------------------------------------------------------------

PAUSE = None  # a task yields this to say "give somebody else a turn"


def sleep(ticks: int) -> tuple[str, int]:
    """A task yields this to say "wake me in N ticks". Our asyncio.sleep."""
    return ("sleep", ticks)


class Scheduler:
    """A ready queue, a sleeping list, a clock, and a loop. Nothing else."""

    def __init__(self) -> None:
        self.ready: deque[tuple[str, object]] = deque()
        self.sleeping: list[tuple[int, str, object]] = []
        self.tick = 0
        self.trace: list[str] = []
        self.results: dict[str, object] = {}

    def spawn(self, name: str, task) -> None:
        """Schedule a generator. Note it does not start: it is only queued."""
        self.ready.append((name, task))

    def _wake(self) -> None:
        due = [entry for entry in self.sleeping if entry[0] <= self.tick]
        self.sleeping = [entry for entry in self.sleeping if entry[0] > self.tick]
        for _wake_at, name, task in sorted(due, key=lambda e: e[0]):
            self.ready.append((name, task))

    def run(self) -> dict[str, object]:
        while self.ready or self.sleeping:
            if not self.ready:
                # Everybody is waiting. A real loop would block in select()
                # here until a socket became readable; we jump the clock.
                self.tick = min(entry[0] for entry in self.sleeping)
                self._wake()
            name, task = self.ready.popleft()
            try:
                instruction = next(task)  # resume it; it runs until its next yield
            except StopIteration as finished:
                self.results[name] = finished.value
                continue
            if instruction is PAUSE:
                self.ready.append((name, task))  # straight to the back of the queue
            else:
                _kind, ticks = instruction
                self.sleeping.append((self.tick + ticks, name, task))
            self.tick += 1
            self._wake()
        return self.results

    def step(self, name: str) -> None:
        """Record that a task did one unit of visible work."""
        self.trace.append(f"{name}:{self.tick}")


# ---------------------------------------------------------------------------
# Tasks written against it. `yield` is the pause point.
# ---------------------------------------------------------------------------


def counting_task(loop: Scheduler, name: str, steps: int):
    for _ in range(steps):
        loop.step(name)
        yield PAUSE  # <- this is the `await`. Control goes back to the loop.
    return f"{name} did {steps} step" + ("" if steps == 1 else "s")


def sleeping_task(loop: Scheduler, name: str, nap: int):
    loop.step(f"{name}-start")
    yield sleep(nap)  # <- like `await asyncio.sleep(nap)`
    loop.step(f"{name}-woke")
    return f"{name} slept {nap}"


def greedy_task(loop: Scheduler, name: str, steps: int):
    """The bug, in a form you can see. It never yields until it is finished."""
    for _ in range(steps):
        loop.step(name)
    yield PAUSE
    return f"{name} hogged {steps} steps"


def main() -> int:
    print("Day 096 — a cooperative scheduler built from generators")
    print()

    print("1. three tasks, round-robin")
    loop = Scheduler()
    loop.spawn("alpha", counting_task(loop, "alpha", 3))
    loop.spawn("beta", counting_task(loop, "beta", 2))
    loop.spawn("gamma", counting_task(loop, "gamma", 1))
    results = loop.run()
    order = [entry.split(":")[0] for entry in loop.trace]
    print(f"   trace:  {' '.join(loop.trace)}")
    print(f"   order:  {' '.join(order)}")
    print("   Each task ran ONE step and then gave the loop back. That interleaving")
    print("   is concurrency, and it happened in a single thread with no lock in")
    print("   sight — which is why no increment can be lost between two yields.")
    for name in sorted(results):
        print(f"   returned: {results[name]}")
    print()

    print("2. a task that waits, while the others carry on")
    loop = Scheduler()
    loop.spawn("napper", sleeping_task(loop, "napper", 4))
    loop.spawn("worker", counting_task(loop, "worker", 5))
    loop.run()
    print(f"   trace:  {' '.join(loop.trace)}")
    print("   napper yielded a sleep instruction and left the ready queue entirely.")
    print("   worker had the loop to itself until napper's tick came round. That is")
    print("   exactly what an await on a socket read does in a real event loop.")
    print()

    print("3. the same loop, with one task that refuses to yield")
    loop = Scheduler()
    loop.spawn("greedy", greedy_task(loop, "greedy", 4))
    loop.spawn("polite", counting_task(loop, "polite", 3))
    loop.run()
    print(f"   trace:  {' '.join(loop.trace)}")
    print("   polite did not run once until greedy had finished all four steps.")
    print("   Nothing errored. Nothing was slow. The loop simply never got the")
    print("   thread back, because `next(task)` does not return until the task")
    print("   reaches a yield. That is the blocking call in 03_blocking_coroutine.py,")
    print("   seen from inside the loop rather than from outside it.")
    print()

    expected_round_robin = "alpha beta gamma alpha beta alpha"
    loop = Scheduler()
    loop.spawn("alpha", counting_task(loop, "alpha", 3))
    loop.spawn("beta", counting_task(loop, "beta", 2))
    loop.spawn("gamma", counting_task(loop, "gamma", 1))
    loop.run()
    actual = " ".join(entry.split(":")[0] for entry in loop.trace)
    print(f"RESULT round_robin_order {actual.replace(' ', ',')}")
    print(f"SHAPE scheduler_interleaves_tasks "
          f"{'yes' if actual == expected_round_robin else 'no'}   "
          f"(expected '{expected_round_robin}')")

    loop = Scheduler()
    loop.spawn("greedy", greedy_task(loop, "greedy", 4))
    loop.spawn("polite", counting_task(loop, "polite", 3))
    loop.run()
    hogged = " ".join(entry.split(":")[0] for entry in loop.trace)
    print(f"RESULT greedy_order {hogged.replace(' ', ',')}")
    print(f"SHAPE a_task_that_never_yields_starves_the_others "
          f"{'yes' if hogged.startswith('greedy greedy greedy greedy') else 'no'}   "
          f"(got '{hogged}')")
    print()
    print("Forty lines. A ready queue, a sleeping list and a while loop. Everything")
    print("asyncio adds on top of this — socket readiness from the operating system,")
    print("cancellation, timeouts, TaskGroups, thread offloading — is machinery around")
    print("that same idea, not a different idea.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
