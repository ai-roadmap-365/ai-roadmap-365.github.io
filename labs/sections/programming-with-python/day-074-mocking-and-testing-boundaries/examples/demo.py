"""The whole lab in one run: the problem, the painful fix, the real fix.

    python3 examples/demo.py

Sections:
  1. what a boundary costs — the real service, timed twice
  2. report_v1 under patch — the right target and the wrong one
  3. report_v2 with hand-written fakes — no patching anywhere
  4. retries and failure, proved with a spy that never waits
  5. a model call behind the same boundary
  6. the purity proof — the core run from an empty directory

Section 1 is the only part of this program whose output changes between runs.
That is not a defect in the demo; it is the defect in the design that the rest
of the lab removes.
"""

from __future__ import annotations

import ast
import datetime
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import sensor_service
from adapters import write_report
from fakes import FakeSensorClient, RecordingSleep, ScriptedModel, SpyClock, frozen_clock
from model_boundary import ModelUnavailable, build_prompt, classify_day
from report_v2 import ReadingsUnavailable, ReportUnavailable, build_report
from sensor_service import ServiceError

DAY = datetime.date(2026, 4, 12)
READINGS = [12.0, 14.0, 20.0, 22.0] * 6  # 24 values, mean exactly 17.0
GOOD_REPLY = "label: mild\nconfidence: 0.82\nnote: a calm spring day"


def heading(text: str) -> None:
    print()
    print(text)
    print("=" * len(text))


# --- 1 ----------------------------------------------------------------------


def what_a_boundary_costs() -> None:
    heading("1. What a boundary costs")
    print("Two calls to the real service. No sockets are opened — the module")
    print("simulates latency and failure — but the two properties are the real ones.")
    for attempt in (1, 2):
        started = time.perf_counter()
        try:
            readings = sensor_service.fetch_readings("ALPHA", DAY.isoformat())
            outcome = f"{len(readings)} readings, first three {readings[:3]}"
        except ServiceError as exc:
            outcome = f"ServiceError: {exc}"
        elapsed = time.perf_counter() - started
        print(f"  call {attempt}: {elapsed:.2f}s  {outcome}")
    print("  slow, and different every time. Multiply by a suite of 200 tests.")


# --- 2 ----------------------------------------------------------------------


def report_v1_under_patch() -> None:
    heading("2. report_v1 under patch — target matters")
    import report_v1

    print("  report_v1.py says: from sensor_service import fetch_readings")
    print("  so the name lives in report_v1's namespace, not sensor_service's.")

    for target in ("report_v1.fetch_readings", "sensor_service.fetch_readings"):
        with tempfile.TemporaryDirectory() as out_dir:
            started = time.perf_counter()
            try:
                with (
                    patch(target, return_value=READINGS),
                    patch("report_v1.datetime") as fake_datetime,
                ):
                    fake_datetime.date.today.return_value = DAY
                    path = report_v1.write_daily_report("ALPHA", out_dir)
                mean_line = path.read_text(encoding="utf-8").splitlines()[-1].strip()
                outcome = f"{mean_line}"
            except Exception as exc:
                outcome = f"{type(exc).__name__}: {exc}"
            elapsed = time.perf_counter() - started
        verdict = "the stub was used" if outcome == "mean     17.0" else "the REAL service was used"
        print(f"  patch({target!r})")
        print(f"      -> {outcome}   [{elapsed:.2f}s — {verdict}]")
    print("  the second target is not an error. It patches something nobody looks at.")


# --- 3 ----------------------------------------------------------------------


def report_v2_with_fakes() -> None:
    heading("3. report_v2 with hand-written fakes — nothing patched")
    clock = SpyClock(DAY)
    client = FakeSensorClient([READINGS])
    started = time.perf_counter()
    report = build_report("ALPHA", clock=clock, client=client)
    elapsed = time.perf_counter() - started
    print(report.render())
    print(f"  built in {elapsed * 1000:.2f} ms, clock read {clock.calls}x, calls {client.calls}")

    with tempfile.TemporaryDirectory() as out_dir:
        path = write_report(report, out_dir)
        print(f"  the adapter wrote {path.name} ({path.stat().st_size} bytes) and did no thinking")


# --- 4 ----------------------------------------------------------------------


def retries_and_failure() -> None:
    heading("4. Retries and failure, without waiting")
    waits = RecordingSleep()
    client = FakeSensorClient(
        [ReadingsUnavailable("timeout"), ReadingsUnavailable("timeout"), READINGS]
    )
    started = time.perf_counter()
    report = build_report(
        "BRAVO", clock=frozen_clock(DAY), client=client, attempts=3, sleep=waits
    )
    elapsed = time.perf_counter() - started
    print(f"  two failures then success -> mean {report.mean}")
    print(f"  attempts made: {len(client.calls)}   backoff requested: {sum(waits.waits)}s")
    print(f"  wall-clock time actually spent: {elapsed * 1000:.2f} ms")

    waits = RecordingSleep()
    client = FakeSensorClient([ReadingsUnavailable("timeout")] * 3)
    try:
        build_report("BRAVO", clock=frozen_clock(DAY), client=client, attempts=3, sleep=waits)
    except ReportUnavailable as exc:
        print(f"  three failures -> {type(exc).__name__}: {exc}")


# --- 5 ----------------------------------------------------------------------


def the_model_boundary() -> None:
    heading("5. A model call behind the same boundary")
    report = build_report("ALPHA", clock=frozen_clock(DAY), client=FakeSensorClient([READINGS]))
    prompt = build_prompt(report)
    print("  the prompt your code builds (this is the testable part):")
    for line in prompt.splitlines():
        print(f"    | {line}")

    model = ScriptedModel([GOOD_REPLY])
    verdict = classify_day(report, model=model)
    print(f"  one scripted reply -> {verdict}")

    waits = RecordingSleep()
    model = ScriptedModel([ModelUnavailable("rate limited"), "I would rather not say.", GOOD_REPLY])
    verdict = classify_day(report, model=model, attempts=3, sleep=waits)
    print(f"  unavailable, then malformed, then good -> {verdict.label} after {len(model.prompts)} calls")
    print(f"  the same prompt was resent each time: {len(set(model.prompts)) == 1}")
    print(f"  backoff requested {waits.waits}s, cost 0 currency units, took no time")


# --- 6 ----------------------------------------------------------------------


def the_purity_proof() -> None:
    heading("6. The purity proof")
    here = Path(__file__).resolve().parent
    for name in ("report_v1.py", "report_v2.py"):
        tree = ast.parse((here / name).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        imported.discard("__future__")
        print(f"  {name:14s} imports {sorted(imported)}")
    print("  report_v2 imports two ways of writing a value down, and nothing else.")
    print("  That is why section 3 needed no patching, no fixtures, and no files.")


def main() -> None:
    print("Test the Logic, Stub the World — Day 074")
    what_a_boundary_costs()
    report_v1_under_patch()
    report_v2_with_fakes()
    retries_and_failure()
    the_model_boundary()
    the_purity_proof()
    print()
    print("Done.")


if __name__ == "__main__":
    main()
