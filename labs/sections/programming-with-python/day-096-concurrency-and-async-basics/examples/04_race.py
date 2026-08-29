#!/usr/bin/env python3
"""Shared state: a counter that loses increments, and three ways to keep them.

Run:  python3 examples/04_race.py

The interpreter lock protects the INTERPRETER — its reference counts, its
internal structures — so that a data race can never corrupt Python's own
memory. It does not protect YOUR data structures. `total = total + 1` is a
read, an addition and a write, and if a thread switch lands between the
read and the write, one increment is silently overwritten by another.

There is an honest wrinkle in reproducing that, and this script does not
hide it. Read the output: on the interpreter this lab was written on, the
naive version at the default settings does not lose a single increment.
That is not evidence the bug is gone. It is evidence the window is narrow.
The script therefore narrows nothing and widens nothing about the CODE —
it only shortens the interval at which the interpreter considers switching
threads, from the default 5 milliseconds to 1 microsecond, which makes the
same race land every single run instead of once in a very long while.

A bug you cannot reproduce is still a bug. It is just a worse bug.
"""

from __future__ import annotations

import queue
import sys
import threading
from contextlib import contextmanager

THREADS = 8
PER_THREAD = 50_000
EXPECTED = THREADS * PER_THREAD
TIGHT_INTERVAL = 1e-6


@contextmanager
def switch_interval(seconds: float | None):
    """Temporarily change how often the interpreter considers a thread switch.

    sys.setswitchinterval is process-wide, so it is restored in a finally
    block. The default is 0.005 seconds: a thread that neither blocks nor
    calls out gets roughly five milliseconds before the interpreter asks
    whether somebody else should have a turn.
    """
    previous = sys.getswitchinterval()
    try:
        if seconds is not None:
            sys.setswitchinterval(seconds)
        yield previous
    finally:
        sys.setswitchinterval(previous)


class SharedCounter:
    """A counter shared by every thread. Read, add, write — three steps."""

    def __init__(self) -> None:
        self.value = 0

    def read(self) -> int:
        return self.value

    def write(self, value: int) -> None:
        self.value = value


def bump_unsafely(counter: SharedCounter, times: int) -> None:
    # The read and the write are two separate operations with a gap between
    # them. Whatever another thread does in that gap is lost.
    for _ in range(times):
        counter.write(counter.read() + 1)


def bump_with_lock(counter: SharedCounter, times: int, lock: threading.Lock) -> None:
    # `with lock:` makes read-add-write one indivisible step. Only one thread
    # can be between the two lines at a time, so nothing can be overwritten.
    for _ in range(times):
        with lock:
            counter.write(counter.read() + 1)


def run_threads(target, *args) -> None:
    workers = [threading.Thread(target=target, args=args) for _ in range(THREADS)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()


def unsafe_total(interval: float | None) -> int:
    counter = SharedCounter()
    with switch_interval(interval):
        run_threads(bump_unsafely, counter, PER_THREAD)
    return counter.value


def locked_total(interval: float | None) -> int:
    counter = SharedCounter()
    lock = threading.Lock()
    with switch_interval(interval):
        run_threads(bump_with_lock, counter, PER_THREAD, lock)
    return counter.value


def queued_total(interval: float | None) -> int:
    """The answer that is usually better than a lock: do not share the state.

    Every worker sends its own subtotal down a queue. One consumer — here,
    the main thread after the join — adds them up. Nothing is shared and
    mutated, so there is nothing to protect and no lock to forget. A
    queue.Queue is internally locked so you do not have to be.
    """
    outbox: queue.Queue[int] = queue.Queue()

    def worker() -> None:
        subtotal = 0
        for _ in range(PER_THREAD):
            subtotal += 1  # a local variable: no other thread can see it
        outbox.put(subtotal)

    with switch_interval(interval):
        workers = [threading.Thread(target=worker) for _ in range(THREADS)]
        for w in workers:
            w.start()
        for w in workers:
            w.join()
    total = 0
    while not outbox.empty():
        total += outbox.get()
    return total


def deadlock_demonstration() -> tuple[bool, bool]:
    """Two locks, two threads, opposite orders. Returns (deadlocked, fixed_ok).

    This is a real deadlock and it would hang forever, so each thread takes
    its second lock with a timeout. The timeout is a detector, not a fix: in
    production it turns a hang into a mysterious slow path. The fix is the
    second half — every thread takes the locks in the SAME order, so a cycle
    of waiting cannot form.
    """
    first, second = threading.Lock(), threading.Lock()
    gate = threading.Barrier(2)
    stuck: list[bool] = []

    def grab(outer: threading.Lock, inner: threading.Lock) -> None:
        with outer:
            gate.wait()  # guarantee both threads hold one lock before either asks for two
            got = inner.acquire(timeout=0.5)
            stuck.append(not got)
            if got:
                inner.release()

    a = threading.Thread(target=grab, args=(first, second))
    b = threading.Thread(target=grab, args=(second, first))  # opposite order: the bug
    a.start()
    b.start()
    a.join()
    b.join()
    deadlocked = any(stuck)

    # Same two locks, same two threads, one rule: always first then second.
    #
    # Note there is no barrier here, and that is not an oversight — it is the
    # second lesson of this function. Adding one would make the FIXED version
    # hang: a thread holding `first` would wait at the barrier for a thread
    # that cannot reach the barrier because it is waiting for `first`. Forcing
    # an interleaving is itself a way to build a deadlock.
    stuck2: list[bool] = []

    def ordered() -> None:
        with first:
            got = second.acquire(timeout=0.5)
            stuck2.append(not got)
            if got:
                second.release()

    c = threading.Thread(target=ordered)
    d = threading.Thread(target=ordered)
    c.start()
    d.start()
    c.join()
    d.join()
    return deadlocked, not any(stuck2)


def main() -> int:
    print("Day 096 — a counter that loses increments")
    print(f"{THREADS} threads x {PER_THREAD:,} increments each; expected total {EXPECTED:,}")
    print(f"default switch interval on this interpreter: {sys.getswitchinterval()} s")
    print()

    print("1. the naive counter at the interpreter's DEFAULT switch interval")
    default_runs = [unsafe_total(None) for _ in range(3)]
    for index, got in enumerate(default_runs, 1):
        print(f"   run {index}: {got:,}   lost {EXPECTED - got:,}")
    print("   Report what you see, not what the textbook says. On this machine the")
    print("   read-add-write finishes well inside one thread's 5 ms slice, so the race")
    print("   almost never lands. That is a narrow window, not a safe program.")
    print()

    print(f"2. the same code with the switch interval at {TIGHT_INTERVAL} s")
    tight_runs = [unsafe_total(TIGHT_INTERVAL) for _ in range(3)]
    for index, got in enumerate(tight_runs, 1):
        print(f"   run {index}: {got:,}   lost {EXPECTED - got:,}")
    print("   The code did not change. Only the frequency of thread switches did.")
    print("   Every increment lost here was an increment that could be lost at the")
    print("   default setting too, on a busier machine, under a longer run, one day.")
    print()

    print("3. the same counter, one lock")
    locked_runs = [locked_total(TIGHT_INTERVAL) for _ in range(3)]
    for index, got in enumerate(locked_runs, 1):
        print(f"   run {index}: {got:,}   lost {EXPECTED - got:,}")
    print("   Exact, at the switch interval that broke the version above.")
    print()

    print("4. the answer that is usually better than a lock: stop sharing")
    queued_runs = [queued_total(TIGHT_INTERVAL) for _ in range(3)]
    for index, got in enumerate(queued_runs, 1):
        print(f"   run {index}: {got:,}   lost {EXPECTED - got:,}")
    print("   Each worker counts into a local variable and posts one subtotal to a")
    print("   queue. There is no shared mutable state, so there is no lock to forget,")
    print("   no lock ordering to get wrong, and nothing to deadlock.")
    print()

    print("5. deadlock, in eight lines")
    deadlocked, ordered_ok = deadlock_demonstration()
    print(f"   two locks taken in opposite orders  -> deadlocked: {'yes' if deadlocked else 'no'}")
    print(f"   the same two taken in the same order -> completed: "
          f"{'yes' if ordered_ok else 'no'}")
    print("   Each thread held one lock and waited for the other. Nothing was busy;")
    print("   nothing errored; the program simply stopped. The timeout above is a")
    print("   detector. The fix is the ordering rule.")
    print()

    worst_default = EXPECTED - min(default_runs)
    worst_tight = EXPECTED - min(tight_runs)
    print(f"RESULT race_lost_at_default_interval {worst_default}")
    print(f"RESULT race_lost_at_tight_interval {worst_tight}")
    print(f"RESULT locked_total {min(locked_runs)}")
    print(f"RESULT queued_total {min(queued_runs)}")
    print(f"RESULT expected_total {EXPECTED}")
    print(f"SHAPE unlocked_counter_loses_increments "
          f"{'yes' if worst_tight > 0 else 'no'}   (lost {worst_tight:,} of {EXPECTED:,})")
    print(f"SHAPE locked_counter_loses_nothing "
          f"{'yes' if all(r == EXPECTED for r in locked_runs) else 'no'}   "
          f"(3 runs, all exactly {EXPECTED:,})")
    print(f"SHAPE queue_version_loses_nothing "
          f"{'yes' if all(r == EXPECTED for r in queued_runs) else 'no'}   "
          f"(3 runs, all exactly {EXPECTED:,})")
    print(f"SHAPE opposite_lock_order_deadlocks {'yes' if deadlocked else 'no'}   "
          "(detected with a timeout; it would otherwise hang forever)")
    print(f"SHAPE consistent_lock_order_does_not "
          f"{'yes' if ordered_ok else 'no'}   (same locks, same threads, one rule)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
