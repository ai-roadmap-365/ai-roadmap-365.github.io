"""The three in-process ways to run something later, and what each costs.

Working from the inside out, before we leave the process at all:

1. **A sleep loop.** ``while True: work(); time.sleep(interval)``. Everyone
   writes this first. It drifts, because the interval is measured from when
   the work *finished*, not from when it was supposed to start — so every run
   is late by the accumulated duration of every run before it.
2. **``sched.scheduler``.** The standard library's event scheduler. It takes
   its time source and its delay function as arguments, which is a small
   design decision with a large consequence: you can hand it a fake clock and
   test six hours of schedule in microseconds.
3. **``threading.Timer``.** One callback, once, after a delay, on its own
   thread. Fine for a single delayed action inside a running program; not a
   scheduler.

All three share the fatal property: they die with the process. Close the
terminal, deploy a new version, reboot the laptop — the schedule is gone, and
nothing tells you. That is why real recurring work belongs to the operating
system's scheduler, and why the rest of this lab is about that.

Every function here takes its time source as a parameter, so nothing in this
file ever actually waits.
"""

from __future__ import annotations

import sched
from collections.abc import Callable
from dataclasses import dataclass

from clock import FakeTime


@dataclass(frozen=True)
class LoopTrace:
    """When each run started, and how late it was against the ideal schedule."""

    starts: tuple[float, ...]
    interval: float

    @property
    def lateness(self) -> tuple[float, ...]:
        first = self.starts[0]
        return tuple(
            round(start - (first + index * self.interval), 6)
            for index, start in enumerate(self.starts)
        )

    @property
    def final_drift(self) -> float:
        return self.lateness[-1]


def naive_sleep_loop(
    *, runs: int, interval: float, work_seconds: float, fake: FakeTime | None = None
) -> LoopTrace:
    """``work(); sleep(interval)`` — the version that drifts.

    With a 60-second interval and 5 seconds of work, run 100 starts 495
    seconds late. The schedule is not 60 seconds; it is 65, and nobody wrote
    65 anywhere.
    """
    fake = fake or FakeTime()
    starts = []
    for _ in range(runs):
        starts.append(fake.time())
        fake.sleep(work_seconds)  # the work
        fake.sleep(interval)  # the wait
    return LoopTrace(tuple(starts), interval)


def deadline_corrected_loop(
    *, runs: int, interval: float, work_seconds: float, fake: FakeTime | None = None
) -> LoopTrace:
    """Sleep until the *next deadline*, not for a fixed span. No drift.

    The fix is three lines: track the next scheduled instant, and sleep for
    whatever is left of it. If a run overruns the interval entirely the sleep
    is zero and the next run starts immediately — which is a decision you have
    now made on purpose rather than by accident.
    """
    fake = fake or FakeTime()
    starts = []
    next_due = fake.time()
    for _ in range(runs):
        starts.append(fake.time())
        fake.sleep(work_seconds)
        next_due += interval
        remaining = next_due - fake.time()
        fake.sleep(max(0.0, remaining))
    return LoopTrace(tuple(starts), interval)


def run_sched_schedule(
    *, delays: list[float], fake: FakeTime | None = None
) -> tuple[list[tuple[float, int]], FakeTime]:
    """Drive ``sched.scheduler`` with a fake clock: hours of schedule, no waiting.

    ``sched.scheduler(timefunc, delayfunc)`` is stdlib dependency injection
    from 1990s Python, and it is the reason a schedule built on ``sched`` is
    testable while one built on ``time.sleep`` is not.
    """
    fake = fake or FakeTime()
    fired: list[tuple[float, int]] = []
    scheduler = sched.scheduler(timefunc=fake.time, delayfunc=fake.sleep)

    def record(index: int) -> None:
        fired.append((fake.time(), index))

    for index, delay in enumerate(delays):
        scheduler.enter(delay, priority=1, action=record, argument=(index,))
    scheduler.run()
    return fired, fake


def periodic_with_sched(
    *, interval: float, runs: int, work: Callable[[], None] | None = None,
    fake: FakeTime | None = None,
) -> list[float]:
    """``sched`` has no repeat: a recurring job re-enters itself. Still no drift.

    The re-entry is scheduled against ``next_due`` rather than "now", so the
    same deadline correction applies.
    """
    fake = fake or FakeTime()
    scheduler = sched.scheduler(timefunc=fake.time, delayfunc=fake.sleep)
    starts: list[float] = []
    state = {"remaining": runs, "next_due": fake.time()}

    def tick() -> None:
        starts.append(fake.time())
        if work is not None:
            work()
        state["remaining"] -= 1
        if state["remaining"] > 0:
            state["next_due"] += interval
            scheduler.enterabs(state["next_due"], priority=1, action=tick)

    scheduler.enterabs(state["next_due"], priority=1, action=tick)
    scheduler.run()
    return starts
