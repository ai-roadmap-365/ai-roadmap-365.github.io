"""The answer key for ``starter/stages.py`` — all nine exercises completed.

Read this *after* you have tried the exercises, not instead of them. It is here
so the test harness can prove the exercises are achievable rather than merely
asserted, and so the instructor solution has something to point at.

Run the starter suite against it:

    DAY098_SOLUTION=1 .venv/bin/pytest starter -q       # 10 passed
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

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sqlalchemy import Integer, String, UniqueConstraint, create_engine, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_PARTIAL = 3
REDACTED = "***redacted***"


@dataclass(frozen=True)
class FetchResult:
    source: str
    ok: bool
    records: list[dict] = field(default_factory=list)
    attempts: int = 0
    status: int | None = None
    error: str = ""


# EXERCISE 2 — a moment, not a mistake.
RETRYABLE_STATUS: frozenset[int] = frozenset({429, 500, 502, 503, 504})


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
    """EXERCISE 1 and 2 — a deadline, bounded retries, and only what is worth it."""
    url = f"{base_url.rstrip('/')}/stations/{source}/readings"
    tried = 0
    last_status: int | None = None
    last_error = ""
    while tried < attempts:
        tried += 1
        request = urllib.request.Request(url, method="GET")
        request.add_header("Accept", "application/json")
        if token:
            request.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                payload = json.loads(response.read().decode("utf-8"))
            return FetchResult(
                source, True, list(payload.get("records", [])), tried, 200
            )
        except urllib.error.HTTPError as exc:
            with exc:
                last_status = exc.code
                body = exc.read().decode("utf-8", errors="replace")
            try:
                last_error = str(json.loads(body).get("error", body))
            except json.JSONDecodeError:
                last_error = body
            if exc.code not in RETRYABLE_STATUS:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_status = None
            last_error = f"{type(exc).__name__}: {exc}"
        if tried < attempts:
            sleep(backoff * (2 ** (tried - 1)))
    return FetchResult(source, False, [], tried, last_status, last_error)


class Reading(BaseModel):
    """EXERCISE 4 — the gate refuses what the store would have to argue with."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    station_id: str = Field(min_length=1, max_length=32)
    reading_id: str = Field(min_length=1, max_length=64)
    observed_at: datetime
    temperature_c: float = Field(ge=-90.0, le=60.0)
    humidity_pct: int = Field(ge=0, le=100)

    @field_validator("observed_at")
    @classmethod
    def must_be_absolute(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("observed_at must carry a UTC offset")
        return value.astimezone(timezone.utc)

    @property
    def temperature_dc(self) -> int:
        return round(self.temperature_c * 10)

    @property
    def observed_at_text(self) -> str:
        return self.observed_at.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Rejection:
    source: str
    index: int
    reading_id: str
    problems: tuple[str, ...]


def validate_all(fetched: dict[str, list[dict]]) -> tuple[list[Reading], list[Rejection]]:
    """EXERCISE 3 — collect every failure; never abort the run for one record."""
    accepted: list[Reading] = []
    rejected: list[Rejection] = []
    for source, records in fetched.items():
        for index, raw in enumerate(records):
            try:
                accepted.append(Reading.model_validate(raw))
            except ValidationError as error:
                problems = tuple(
                    f"{'.'.join(str(part) for part in detail['loc']) or '<record>'}: {detail['msg']}"
                    for detail in error.errors()
                )
                rejected.append(
                    Rejection(
                        source=source,
                        index=index,
                        reading_id=str(raw.get("reading_id", "<no reading_id>")),
                        problems=problems,
                    )
                )
    return accepted, rejected


class Base(DeclarativeBase):
    pass


class StoredReading(Base):
    """EXERCISE 5a — the idempotence key, declared where the database enforces it."""

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(32), nullable=False)
    reading_id: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_at: Mapped[str] = mapped_column(String(20), nullable=False)
    temperature_dc: Mapped[int] = mapped_column(Integer, nullable=False)
    humidity_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    ingested_by_run: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint("station_id", "reading_id", name="uq_readings_idempotence"),
    )


@dataclass(frozen=True)
class StoreResult:
    considered: int
    inserted: int
    duplicates: int
    total_rows: int


def store_readings(session: Session, readings: list[Reading], *, run_id: str) -> StoreResult:
    """EXERCISE 5b — insert only what is new, and report it honestly."""
    keys = [(r.station_id, r.reading_id) for r in readings]
    held = set()
    if keys:
        rows = session.execute(
            select(StoredReading.station_id, StoredReading.reading_id)
        ).all()
        held = {(row[0], row[1]) for row in rows}

    seen: set[tuple[str, str]] = set()
    payload: list[dict] = []
    for reading in readings:
        key = (reading.station_id, reading.reading_id)
        if key in held or key in seen:
            continue
        seen.add(key)
        payload.append(
            {
                "station_id": reading.station_id,
                "reading_id": reading.reading_id,
                "observed_at": reading.observed_at_text,
                "temperature_dc": reading.temperature_dc,
                "humidity_pct": reading.humidity_pct,
                "ingested_by_run": run_id,
            }
        )
    if payload:
        session.execute(
            sqlite_insert(StoredReading).on_conflict_do_nothing(
                index_elements=["station_id", "reading_id"]
            ),
            payload,
        )
        session.commit()
    total = len(session.execute(select(StoredReading.id)).all())
    return StoreResult(len(readings), len(payload), len(readings) - len(payload), total)


def build_report(
    session: Session,
    *,
    report_at: str,
    window_hours: int,
    stations: list[str],
) -> dict[str, Any]:
    """EXERCISE 6 — the instant is a parameter, so the answer is reproducible."""
    end = datetime.fromisoformat(report_at.replace("Z", "+00:00"))
    if end.tzinfo is None:
        raise ValueError("report_at must carry a UTC offset")
    end = end.astimezone(timezone.utc)
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


def _redact(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        for secret in secrets:
            if secret and secret in value:
                value = value.replace(secret, REDACTED)
        return value
    if isinstance(value, dict):
        return {key: _redact(item, secrets) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item, secrets) for item in value]
    return value


class RunLogger:
    """EXERCISE 7 and 9 — a run id on every line, and redaction in one place."""

    def __init__(self, run_id: str, *, stream: TextIO, secrets: tuple[str, ...] = ()) -> None:
        self.run_id = run_id
        self.stream = stream
        self.secrets = tuple(s for s in secrets if s)
        self.emitted: list[dict[str, Any]] = []

    def event(self, event: str, level: str = "info", **fields: Any) -> None:
        record: dict[str, Any] = {"level": level, "run_id": self.run_id, "event": event}
        record.update(_redact(fields, self.secrets))
        self.emitted.append(record)
        self.stream.write(json.dumps(record) + "\n")


def run(
    base_url: str,
    *,
    sources: list[str],
    token: str = "",
    database_url: str = "sqlite://",
    window_hours: int = 12,
    report_at: str = "2026-08-16T12:00:00Z",
    run_id: str = "starter-run",
    log_stream: TextIO | None = None,
    out: TextIO | None = None,
) -> int:
    """EXERCISE 8 — three outcomes, three exit codes."""
    log_stream = log_stream if log_stream is not None else io.StringIO()
    out = out if out is not None else sys.stdout
    logger = RunLogger(run_id, stream=log_stream, secrets=(token,) if token else ())

    results = [
        fetch_source(base_url, source, token=token, backoff=0.0, sleep=lambda _s: None)
        for source in sources
    ]
    fetched = {r.source: r.records for r in results if r.ok}
    failed = [r.source for r in results if not r.ok]
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

    accepted, rejected = validate_all(fetched)
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
        summary = build_report(
            session, report_at=report_at, window_hours=window_hours, stations=sources
        )
        logger.event("stage.report", **summary)
        out.write(json.dumps(summary, sort_keys=True) + "\n")

    if failed or rejected:
        status, code = "partial_success", EXIT_PARTIAL
    else:
        status, code = "success", EXIT_SUCCESS
    logger.event("stage.observe", status=status, exit_code=code)
    logger.event("run.end", level="warning" if code else "info", status=status, exit_code=code)
    engine.dispose()
    return code
