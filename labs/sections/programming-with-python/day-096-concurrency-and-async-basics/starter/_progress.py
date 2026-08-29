"""The progress checker behind `bash starter/02_check.sh`.

You do not need to edit this file, but reading it is worthwhile: it is the
same measure-do-not-believe discipline the lesson argues for, applied to
your own code. Nothing here inspects how you wrote a function. Every check
either compares a real answer against the right one, or times two versions
of the same work and compares the ratio.

Speed checks are stated as ratios with generous margins — "at least three
times faster", never "under 200 milliseconds" — so that a slow laptop, a
busy machine or a different operating system does not fail work that is
correct. The ratio is the claim that travels.

Usage:  python3 starter/_progress.py [path-to-module]
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "examples"))

import labkit  # noqa: E402

TOTAL = 8
REQUESTS = 12
REQUEST_DELAY = 0.05
PRIME_LIMIT = 400_000
PRIME_TASKS = 4
PRIME_ANSWER = 33860  # the number of primes below 400,000
NAPS = [0.15] * 5
RACE_THREADS = 8
RACE_PER_THREAD = 50_000
TIGHT_INTERVAL = 1e-6

results: list[tuple[int, str, bool, str]] = []


def record(number: int, title: str, passed: bool, detail: str) -> None:
    results.append((number, title, passed, detail))


def load(path: Path):
    spec = importlib.util.spec_from_file_location("under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call(module, name: str, *args):
    """Call an exercise. Returns (elapsed, value) or (None, reason-string)."""
    function = getattr(module, name, None)
    if function is None:
        return None, f"no function named {name}"
    start = time.perf_counter()
    try:
        value = function(*args)
    except NotImplementedError:
        return None, "not started"
    except Exception as error:  # noqa: BLE001 - report anything, do not crash
        return None, f"{type(error).__name__}: {error}"
    return time.perf_counter() - start, value


def bodies_ok(value: object, count: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == count
        and all(isinstance(body, str) and "waited" in body for body in value)
        and all(f"/item/{n}" in value[n - 1] for n in range(1, count + 1))
    )


def check_waiting(module) -> float | None:
    """Exercises 1-3. Returns the sequential baseline, or None if it failed."""
    with labkit.fixture_server(delay=REQUEST_DELAY) as base:
        labkit.fetch(base + "/warmup")
        targets = labkit.urls(base, REQUESTS)

        elapsed, value = call(module, "fetch_all_sequentially", targets)
        if elapsed is None:
            record(1, "fetch_all_sequentially", False, str(value))
            baseline = None
        elif not bodies_ok(value, REQUESTS):
            record(1, "fetch_all_sequentially", False, "wrong bodies or wrong order")
            baseline = None
        else:
            baseline = elapsed
            record(1, "fetch_all_sequentially", True, f"{REQUESTS} bodies in order, {elapsed:.3f}s")

        for number, name, args in (
            (2, "fetch_all_with_threads", (targets, REQUESTS)),
            (3, "fetch_all_with_asyncio", (targets,)),
        ):
            elapsed, value = call(module, name, *args)
            if elapsed is None:
                record(number, name, False, str(value))
                continue
            if not bodies_ok(value, REQUESTS):
                record(number, name, False, "wrong bodies or wrong order")
                continue
            if baseline is None:
                record(number, name, False, "cannot judge speed: exercise 1 is not working yet")
                continue
            ratio = baseline / elapsed
            record(
                number,
                name,
                ratio >= 2.5,
                f"{ratio:.1f}x faster than sequential ({elapsed:.3f}s); needs >= 2.5x",
            )
    return baseline


def check_computing(module) -> None:
    """Exercises 4 and 5."""
    limits = [PRIME_LIMIT] * PRIME_TASKS
    expected = [PRIME_ANSWER] * PRIME_TASKS
    start = time.perf_counter()
    sequential_answer = [labkit.count_primes(limit) for limit in limits]
    baseline = time.perf_counter() - start
    assert sequential_answer == expected, "the checker's own baseline is wrong"

    elapsed, value = call(module, "count_primes_with_threads", limits, PRIME_TASKS)
    if elapsed is None:
        record(4, "count_primes_with_threads", False, str(value))
    elif value != expected:
        record(4, "count_primes_with_threads", False, f"wrong counts: {value}")
    else:
        record(
            4,
            "count_primes_with_threads",
            True,
            f"counts correct; {baseline / elapsed:.2f}x sequential — threads do not help here, "
            "and are not required to",
        )

    elapsed, value = call(module, "count_primes_with_processes", limits, PRIME_TASKS)
    if elapsed is None:
        record(5, "count_primes_with_processes", False, str(value))
    elif value != expected:
        record(5, "count_primes_with_processes", False, f"wrong counts: {value}")
    else:
        ratio = baseline / elapsed
        record(
            5,
            "count_primes_with_processes",
            ratio >= 1.4,
            f"counts correct; {ratio:.2f}x sequential ({elapsed:.3f}s); needs >= 1.4x",
        )


def check_offloading(module) -> None:
    """Exercise 6."""
    elapsed, value = call(module, "wait_without_blocking_the_loop", NAPS)
    if elapsed is None:
        record(6, "wait_without_blocking_the_loop", False, str(value))
        return
    if value != NAPS:
        record(6, "wait_without_blocking_the_loop", False, f"expected {NAPS}, got {value}")
        return
    serial = sum(NAPS)
    record(
        6,
        "wait_without_blocking_the_loop",
        elapsed < serial * 0.6,
        f"{elapsed:.3f}s against a serial floor of {serial:.2f}s; needs < {serial * 0.6:.2f}s",
    )


def check_counter(module) -> None:
    """Exercise 7, run at a switch interval that breaks unprotected code."""
    function = getattr(module, "counter_that_loses_nothing", None)
    if function is None:
        record(7, "counter_that_loses_nothing", False, "no function of that name")
        return
    expected = RACE_THREADS * RACE_PER_THREAD
    previous = sys.getswitchinterval()
    seen: list[int] = []
    try:
        sys.setswitchinterval(TIGHT_INTERVAL)
        for _ in range(3):
            try:
                seen.append(function(RACE_THREADS, RACE_PER_THREAD))
            except NotImplementedError:
                record(7, "counter_that_loses_nothing", False, "not started")
                return
            except Exception as error:  # noqa: BLE001
                record(7, "counter_that_loses_nothing", False, f"{type(error).__name__}: {error}")
                return
    finally:
        sys.setswitchinterval(previous)
    exact = all(value == expected for value in seen)
    worst = min(seen)
    record(
        7,
        "counter_that_loses_nothing",
        exact,
        f"3 runs at a {TIGHT_INTERVAL}s switch interval; "
        + (f"all exactly {expected:,}" if exact else f"lost up to {expected - worst:,} increments"),
    )


def make_task(steps: int):
    def task():
        for _ in range(steps):
            yield

    return task()


def check_scheduler(module) -> None:
    """Exercise 8."""
    tasks = [("a", make_task(3)), ("b", make_task(2)), ("c", make_task(1))]
    elapsed, value = call(module, "round_robin", tasks)
    if elapsed is None:
        record(8, "round_robin", False, str(value))
        return
    expected = ["a", "b", "c", "a", "b", "a"]
    record(
        8,
        "round_robin",
        value == expected,
        f"expected {expected}, got {value}",
    )


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else LAB / "starter" / "01_exercises.py"
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    if not target.exists():
        print(f"No such file: {target}")
        return 2

    print(f"Checking {target.name}")
    print(f"python {sys.version.split()[0]}   "
          f"default switch interval {sys.getswitchinterval()} s")
    print()

    try:
        module = load(target)
    except Exception as error:  # noqa: BLE001
        print(f"The module would not import: {type(error).__name__}: {error}")
        print()
        print(f"0 of {TOTAL} exercises complete.")
        return 1

    check_waiting(module)
    check_computing(module)
    check_offloading(module)
    check_counter(module)
    check_scheduler(module)

    passed = 0
    for number, title, ok, detail in sorted(results):
        mark = "ok  " if ok else "open"
        passed += 1 if ok else 0
        print(f"  [{mark}] {number}. {title}")
        print(f"         {detail}")
    print()
    print(f"{passed} of {TOTAL} exercises complete.")
    return 0 if passed == TOTAL else 1


if __name__ == "__main__":
    raise SystemExit(main())
