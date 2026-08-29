"""The clock as an injected boundary.

Day 74 named six boundaries a unit test must not cross, and the clock was the
first of them. Today the clock is not incidental — it is the subject. Every
question worth asking about a scheduled job ("has today's run already
happened?", "is this run overdue?", "what instant does 02:30 mean on the day
the clocks change?") is a question about time, and none of it is testable if
the answer comes from `datetime.now()` buried three calls deep.

So nothing in this lab calls `datetime.now()` except `system_clock`, which is
the one adapter at the edge. Everything else takes a `Clock` parameter.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from zoneinfo import ZoneInfo

#: A clock is any zero-argument callable that returns an aware datetime.
#: That is the whole interface. It needs no class and no library.
Clock = Callable[[], dt.datetime]

UTC = dt.timezone.utc


def system_clock(tz: str = "UTC") -> Clock:
    """The real clock: the only function in this lab that reads the system time.

    Returns an *aware* datetime. A naive datetime (one with no ``tzinfo``) is
    the root of most scheduling bugs, because it silently means "whatever the
    machine happens to think local time is" — and a cron job's machine often
    disagrees with your laptop.
    """
    zone = UTC if tz.upper() == "UTC" else ZoneInfo(tz)
    return lambda: dt.datetime.now(tz=zone)


def frozen_clock(moment: dt.datetime) -> Clock:
    """A clock stuck at one instant. Five words of code; replaces a library."""
    if moment.tzinfo is None:
        raise ValueError("frozen_clock needs an aware datetime, not a naive one")
    return lambda: moment


def ticking_clock(start: dt.datetime, step: dt.timedelta) -> Clock:
    """A clock that advances by ``step`` every time it is read.

    Useful for measuring a duration in a test without any duration passing:
    the runner reads the clock once before the work and once after, so a
    one-second step makes every job take exactly one second, deterministically.
    """
    if start.tzinfo is None:
        raise ValueError("ticking_clock needs an aware datetime, not a naive one")
    state = {"now": start}

    def read() -> dt.datetime:
        current = state["now"]
        state["now"] = current + step
        return current

    return read


class FakeTime:
    """A stand-in for ``time.monotonic`` and ``time.sleep`` together.

    ``sched.scheduler`` takes its time source and its delay function as
    constructor arguments precisely so that they can be replaced. Handing it a
    ``FakeTime`` makes a scheduler that "waits" six hours in microseconds,
    which is how you test a schedule instead of watching one.
    """

    def __init__(self, start: float = 0.0) -> None:
        self.now = start
        self.slept: list[float] = []

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds

    @property
    def total_slept(self) -> float:
        return sum(self.slept)
