"""Stage 3 — Store.

**The promise:** running the pipeline twice stores the data once.

That promise is the hinge of the whole design, and it is bought with one thing:
an **idempotence key**, a column or set of columns that identifies a record by
what it *is* rather than by when it arrived. Here it is
``(station_id, reading_id)`` — the pair the source itself assigns, declared
``UNIQUE``.

Two layers enforce it, deliberately:

1. ``store_readings`` asks the database which keys it already holds and inserts
   only the rest. This is what makes the *count* honest: the run can report "4
   new, 3 already held" rather than "7 written".
2. The ``UNIQUE`` constraint plus ``ON CONFLICT DO NOTHING`` catches anything
   layer 1 missed — a duplicate inside the same batch, or a second copy of the
   pipeline that started while this one was between the SELECT and the INSERT.

Layer 1 without layer 2 is a promise the application makes and the database
cannot keep. Layer 2 without layer 1 works and reports nothing useful. The
schema is where correctness lives; the query is where the reporting lives.

Everything else here is Days 88, 91 and 93 applied without ceremony: integer
minor units instead of floats (deci-Celsius — 18.4 C is stored as 184, and the
division by ten happens at the display edge and nowhere else), timestamps as ISO
8601 text in UTC so lexicographic order is chronological order, CHECK
constraints that make the illegal states unrepresentable rather than merely
discouraged, and an index on the column the report actually filters by.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    func,
    select,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from validate import Reading


class Base(DeclarativeBase):
    pass


class StoredReading(Base):
    """One reading, as it lives on disk."""

    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(32), nullable=False)
    reading_id: Mapped[str] = mapped_column(String(64), nullable=False)
    #: ISO 8601 in UTC. Fixed width, most significant field first, so ordering
    #: the text orders the instants (Day 91, Day 95).
    observed_at: Mapped[str] = mapped_column(String(20), nullable=False)
    #: Deci-Celsius as an integer. 18.4 C is 184. No float ever reaches disk.
    temperature_dc: Mapped[int] = mapped_column(Integer, nullable=False)
    humidity_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Which run put it here. This is what makes a bad backfill undoable.
    ingested_by_run: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint("station_id", "reading_id", name="uq_readings_idempotence"),
        CheckConstraint("humidity_pct BETWEEN 0 AND 100", name="ck_readings_humidity"),
        CheckConstraint("temperature_dc BETWEEN -900 AND 600", name="ck_readings_temperature"),
        CheckConstraint("length(observed_at) = 20", name="ck_readings_observed_at_iso"),
        Index("ix_readings_observed_at", "observed_at"),
    )


class RunRow(Base):
    """One row per pipeline run. A run id you cannot look up is a run id you
    cannot act on, and 'delete everything run abc123 wrote' is the cheapest
    recovery a pipeline can offer."""

    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    started_at: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    records_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_accepted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_duplicate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


@dataclass(frozen=True)
class StoreResult:
    considered: int
    inserted: int
    duplicates: int
    total_rows: int
    inserted_keys: tuple[tuple[str, str], ...] = field(default=())


def build_engine(database_url: str = "sqlite://") -> Engine:
    """Create the engine and the schema. ``sqlite://`` alone means in memory."""
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return engine


def existing_keys(session: Session, keys: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """Which of these idempotence keys the store already holds."""
    if not keys:
        return set()
    stations = {station for station, _ in keys}
    rows = session.execute(
        select(StoredReading.station_id, StoredReading.reading_id).where(
            StoredReading.station_id.in_(stations)
        )
    ).all()
    held = {(row[0], row[1]) for row in rows}
    return held & set(keys)


def store_readings(
    session: Session,
    readings: list[Reading],
    *,
    run_id: str,
) -> StoreResult:
    """Insert only what is new. Report exactly what happened."""
    keys = [(reading.station_id, reading.reading_id) for reading in readings]
    already = existing_keys(session, keys)

    seen_in_batch: set[tuple[str, str]] = set()
    rows: list[dict] = []
    for reading in readings:
        key = (reading.station_id, reading.reading_id)
        if key in already or key in seen_in_batch:
            continue
        seen_in_batch.add(key)
        rows.append(
            {
                "station_id": reading.station_id,
                "reading_id": reading.reading_id,
                "observed_at": reading.observed_at_text,
                "temperature_dc": reading.temperature_dc,
                "humidity_pct": reading.humidity_pct,
                "ingested_by_run": run_id,
            }
        )

    if rows:
        # Layer 2: the database's own guarantee, in case layer 1 raced.
        statement = sqlite_insert(StoredReading).on_conflict_do_nothing(
            index_elements=["station_id", "reading_id"]
        )
        session.execute(statement, rows)
        session.commit()

    total = session.execute(select(func.count()).select_from(StoredReading)).scalar_one()
    return StoreResult(
        considered=len(readings),
        inserted=len(rows),
        duplicates=len(readings) - len(rows),
        total_rows=int(total),
        inserted_keys=tuple(sorted((row["station_id"], row["reading_id"]) for row in rows)),
    )


def record_run(
    session: Session,
    *,
    run_id: str,
    started_at: str,
    status: str,
    fetched: int,
    accepted: int,
    rejected: int,
    inserted: int,
    duplicates: int,
) -> None:
    """Write (or overwrite) this run's row. Re-running a run id is not an error;
    it is a rerun, and the counts it reports are the counts of the rerun."""
    statement = (
        sqlite_insert(RunRow)
        .values(
            run_id=run_id,
            started_at=started_at,
            status=status,
            records_fetched=fetched,
            records_accepted=accepted,
            records_rejected=rejected,
            records_inserted=inserted,
            records_duplicate=duplicates,
        )
        .on_conflict_do_update(
            index_elements=["run_id"],
            set_={
                "started_at": started_at,
                "status": status,
                "records_fetched": fetched,
                "records_accepted": accepted,
                "records_rejected": rejected,
                "records_inserted": inserted,
                "records_duplicate": duplicates,
            },
        )
    )
    session.execute(statement)
    session.commit()


def utc_text(moment: datetime | None = None) -> str:
    moment = moment or datetime.now(timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
