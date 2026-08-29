"""Your work. A pipeline that runs, and breaks every promise it should keep.

Nothing here is broken in the sense of raising a mysterious error. It is worse
than that: it is a pipeline that looks finished. It fetches, it validates, it
stores, it reports, it exits. Point it at a healthy source on a good day and you
would never know. The nine exercises below turn each of its five stages into a
stage that keeps a promise.

Run the skeleton first, before you change anything:

    .venv/bin/pytest starter -q          # 1 passed, 9 skipped

The one passing test proves the skeleton runs end to end and reports failure —
because it aborts at the first malformed record. That is exercise 3.

Work in order. After each exercise, delete that exercise's ``@exercise(...)``
decorator in ``test_stages.py`` and run pytest again.
"""

from __future__ import annotations

import io
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, TextIO

from pydantic import BaseModel, ValidationError
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_PARTIAL = 3


# ---------------------------------------------------------------------------
# Stage 1 — Ingest
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FetchResult:
    source: str
    ok: bool
    records: list[dict] = field(default_factory=list)
    attempts: int = 0
    status: int | None = None
    error: str = ""


#: Statuses worth a second attempt.
#:
#:     EXERCISE 2 — Retry only what is worth retrying.
#:     A 500 means the server had a bad moment. A 404 means the URL is wrong,
#:     and it will be just as wrong in two seconds. Fill this set with the
#:     codes that describe a moment rather than a mistake, then use it in
#:     fetch_source() to break out of the loop instead of retrying.
#:     Check with: .venv/bin/pytest starter -q -k retryable
RETRYABLE_STATUS: frozenset[int] = frozenset()


def fetch_source(
    base_url: str,
    source: str,
    *,
    token: str = "",
    timeout: float = 5.0,
    attempts: int = 3,
    backoff: float = 0.05,
    sleep: Callable[[float], None] = time.sleep,
) -> FetchResult:
    """Fetch one source.

    EXERCISE 1 — Give this a deadline and a second chance.
    Right now it makes exactly one attempt and passes no ``timeout`` to
    ``urlopen``, so a hung server hangs your 3 a.m. run forever and a source
    that blinks is lost for the day. Wrap the request in a loop that tries up
    to ``attempts`` times, pass ``timeout=timeout`` to ``urlopen``, and call
    ``sleep(backoff * 2 ** (tried - 1))`` between attempts.
    Check with: .venv/bin/pytest starter -q -k retries
    """
    url = f"{base_url.rstrip('/')}/stations/{source}/readings"
    request = urllib.request.Request(url, method="GET")
    request.add_header("Accept", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
            return FetchResult(source, True, list(payload.get("records", [])), 1, response.status)
    except urllib.error.HTTPError as exc:
        # HTTPError is a file object; not closing it leaks a socket.
        with exc:
            body = exc.read().decode("utf-8", errors="replace")
        try:
            message = str(json.loads(body).get("error", body))
        except json.JSONDecodeError:
            message = body
        return FetchResult(source, False, [], 1, exc.code, message)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return FetchResult(source, False, [], 1, None, f"{type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Stage 2 — Validate
# ---------------------------------------------------------------------------
class Reading(BaseModel):
    """One reading.

    EXERCISE 4 — Make this model refuse what the store would have to argue with.
    As written it accepts humidity of 155 and a naive timestamp, and it silently
    ignores any extra field the source starts sending. Add
    ``model_config = ConfigDict(extra="forbid")``, constrain ``humidity_pct`` to
    0-100 and ``temperature_c`` to -90.0-60.0 with ``Field(ge=..., le=...)``,
    and add a ``field_validator`` on ``observed_at`` that rejects a value whose
    ``tzinfo`` is None — an instant without an offset is an assumption, not a
    time (Day 95).
    Check with: .venv/bin/pytest starter -q -k out_of_range
    """

    station_id: str
    reading_id: str
    observed_at: datetime
    temperature_c: float
    humidity_pct: int

    @property
    def temperature_dc(self) -> int:
        return round(self.temperature_c * 10)

    @property
    def observed_at_text(self) -> str:
        return self.observed_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Rejection:
    source: str
    index: int
    reading_id: str
    problems: tuple[str, ...]


def validate_all(fetched: dict[str, list[dict]]) -> tuple[list[Reading], list[Rejection]]:
    """Validate every fetched record.

    EXERCISE 3 — Collect the failures instead of dying on the first.
    This raises the moment one record is malformed, which throws away every good
    record that came with it and tells whoever owns the source exactly one thing
    that is wrong. Catch ``ValidationError`` per record, build a ``Rejection``
    from ``error.errors()`` (each entry has ``loc`` and ``msg``), and return
    both lists.
    Check with: .venv/bin/pytest starter -q -k collects
    """
    accepted: list[Reading] = []
    rejected: list[Rejection] = []
    for source, records in fetched.items():
        for index, raw in enumerate(records):
            accepted.append(Reading.model_validate(raw))  # raises on the first bad one
    return accepted, rejected


# ---------------------------------------------------------------------------
# Stage 3 — Store
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class StoredReading(Base):
    """One reading on disk.

    EXERCISE 5a — Declare the idempotence key.
    Add to ``__table_args__`` a
    ``UniqueConstraint("station_id", "reading_id", name="uq_readings_idempotence")``.
    This is the promise the database keeps even when your code is wrong.
    """

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(32), nullable=False)
    reading_id: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_at: Mapped[str] = mapped_column(String(20), nullable=False)
    temperature_dc: Mapped[int] = mapped_column(Integer, nullable=False)
    humidity_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    ingested_by_run: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = ()


@dataclass(frozen=True)
class StoreResult:
    considered: int
    inserted: int
    duplicates: int
    total_rows: int


def store_readings(session: Session, readings: list[Reading], *, run_id: str) -> StoreResult:
    """Write the accepted readings.

    EXERCISE 5b — Store what is new, and only what is new.
    This inserts everything it is given, so the duplicate inside one payload
    lands twice and a second run of the pipeline doubles the table. Select the
    ``(station_id, reading_id)`` pairs the table already holds, skip those and
    any repeat inside this batch, and report ``inserted`` and ``duplicates``
    honestly. Then use ``sqlalchemy.dialects.sqlite.insert(...)
    .on_conflict_do_nothing(index_elements=["station_id", "reading_id"])`` so
    the database backs you up.
    Check with: .venv/bin/pytest starter -q -k idempotent
    """
    for reading in readings:
        session.add(
            StoredReading(
                station_id=reading.station_id,
                reading_id=reading.reading_id,
                observed_at=reading.observed_at_text,
                temperature_dc=reading.temperature_dc,
                humidity_pct=reading.humidity_pct,
                ingested_by_run=run_id,
            )
        )
    session.commit()
    total = len(session.execute(select(StoredReading.id)).all())
    return StoreResult(len(readings), len(readings), 0, total)


# ---------------------------------------------------------------------------
# Stage 4 — Report
# ---------------------------------------------------------------------------
def build_report(session: Session, *, window_hours: int, stations: list[str]) -> dict[str, Any]:
    """Summarise the last ``window_hours``.

    EXERCISE 6 — Make the instant a parameter.
    This reads the clock, so its answer changes every second and no test can
    assert on it. Add a keyword-only ``report_at: str`` argument, parse it with
    ``datetime.fromisoformat(report_at.replace("Z", "+00:00"))``, require an
    offset, and derive the window from it. Then the report is testable, a
    backfill is possible, and "what did the 3 a.m. run see?" has an answer.
    Check with: .venv/bin/pytest starter -q -k fixed_instant
    """
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=window_hours)
    end_text = end.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_text = start.strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = session.execute(
        select(StoredReading.station_id, StoredReading.observed_at, StoredReading.temperature_dc)
        .where(StoredReading.observed_at >= start_text)
        .where(StoredReading.observed_at <= end_text)
    ).all()
    per_station: dict[str, list[int]] = {name: [] for name in stations}
    for station_id, _observed_at, temperature_dc in rows:
        per_station.setdefault(station_id, []).append(temperature_dc)
    return {
        "report_at": end_text,
        "window_start": start_text,
        "readings_in_window": len(rows),
        "stations": {name: len(values) for name, values in sorted(per_station.items())},
    }


# ---------------------------------------------------------------------------
# Stage 5 — Observe
# ---------------------------------------------------------------------------
class RunLogger:
    """One JSON object per line.

    EXERCISE 7 — Carry the run id on every line.
    A log line with no run id cannot be joined to the run that wrote it, and at
    3 a.m. that is the difference between "this run failed" and "something
    failed". Put ``run_id`` into every record.

    EXERCISE 9 — Redact secrets in the logger, not by remembering.
    charlie's error body echoes the API token back, so the token reaches the log
    without anybody writing code to log it. Store ``secrets`` on the logger and
    replace every occurrence in every string value with ``"***redacted***"``
    before writing. Strings nested inside lists and dicts count.
    Check with: .venv/bin/pytest starter -q -k "run_id or secret"
    """

    def __init__(self, run_id: str, *, stream: TextIO, secrets: tuple[str, ...] = ()) -> None:
        self.run_id = run_id
        self.stream = stream
        self.secrets = secrets
        self.emitted: list[dict[str, Any]] = []

    def event(self, event: str, level: str = "info", **fields: Any) -> None:
        record = {"level": level, "event": event}
        record.update(fields)
        self.emitted.append(record)
        self.stream.write(json.dumps(record) + "\n")


def run(
    base_url: str,
    *,
    sources: list[str],
    token: str = "",
    database_url: str = "sqlite://",
    window_hours: int = 12,
    run_id: str = "starter-run",
    log_stream: TextIO | None = None,
    out: TextIO | None = None,
) -> int:
    """Run all five stages once and return an exit code.

    EXERCISE 8 — Say partial success out loud.
    This returns 0 whenever it did not crash, so a scheduler cannot tell a clean
    run from one where a source has been dark for a week. Return
    ``EXIT_PARTIAL`` (3) when any source failed permanently or any record was
    rejected, ``EXIT_FAILURE`` (1) when no source answered at all, and
    ``EXIT_SUCCESS`` (0) only when neither happened.
    Check with: .venv/bin/pytest starter -q -k exit_code
    """
    log_stream = log_stream if log_stream is not None else io.StringIO()
    out = out if out is not None else sys.stdout
    logger = RunLogger(run_id, stream=log_stream, secrets=(token,) if token else ())

    results = [fetch_source(base_url, source, token=token) for source in sources]
    fetched = {result.source: result.records for result in results if result.ok}
    failed = [result.source for result in results if not result.ok]
    for result in results:
        if not result.ok:
            logger.event(
                "ingest.source_failed",
                level="warning",
                source=result.source,
                status=result.status,
                error=result.error,
            )
    logger.event(
        "stage.ingest",
        sources_ok=len(fetched),
        sources_failed=len(failed),
        records_fetched=sum(len(records) for records in fetched.values()),
    )
    if not fetched:
        logger.event("run.end", level="error", status="failure")
        out.write("no source answered\n")
        return EXIT_FAILURE

    try:
        accepted, rejected = validate_all(fetched)
    except ValidationError as error:
        logger.event("run.end", level="error", status="failure", error=str(error).splitlines()[0])
        out.write("aborted at the first bad record\n")
        return EXIT_FAILURE
    logger.event("stage.validate", accepted=len(accepted), rejected=len(rejected))

    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        stored = store_readings(session, accepted, run_id=run_id)
        logger.event(
            "stage.store",
            inserted=stored.inserted,
            duplicates_skipped=stored.duplicates,
            total_rows=stored.total_rows,
        )
        summary = build_report(session, window_hours=window_hours, stations=sources)
        logger.event("stage.report", **summary)
        out.write(json.dumps(summary, sort_keys=True) + "\n")
    logger.event("stage.observe", status="success")
    logger.event("run.end", status="success")
    engine.dispose()
    return EXIT_SUCCESS
