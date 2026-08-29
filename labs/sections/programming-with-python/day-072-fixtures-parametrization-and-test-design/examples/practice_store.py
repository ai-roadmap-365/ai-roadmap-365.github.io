"""A tiny CSV-backed store of practice sessions — the code under test.

This module is deliberately small and deliberately ordinary. It is the kind of
thing you wrote on Days 64 and 65: a dataclass with a few rules, and a class
that reads and writes one CSV file. Nothing here knows that pytest exists.

The interesting part of this lab is not this file. It is the shape of the test
suite that surrounds it.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

FIELDNAMES = ["ref", "logged_on", "topic", "minutes"]

#: The longest single session the log will accept, in minutes.
MAX_MINUTES = 600


class StoreError(Exception):
    """Any rule of the practice-log domain that was refused."""


class InvalidSession(StoreError):
    """A session was built from values the rules forbid."""


class DuplicateRef(StoreError):
    """A reference already present in the store was added again."""


class UnknownRef(StoreError):
    """A reference the store has never seen was asked for."""


@dataclass(frozen=True)
class Session:
    """One practice session: a reference, a date, a topic, and a duration."""

    ref: str
    logged_on: date
    topic: str
    minutes: int

    def __post_init__(self) -> None:
        if not isinstance(self.ref, str) or not _looks_like_ref(self.ref):
            raise InvalidSession(f"reference must look like S-001, got {self.ref!r}")
        if not isinstance(self.logged_on, date):
            raise InvalidSession(f"logged_on must be a date, got {self.logged_on!r}")
        if not self.topic or self.topic != self.topic.strip().lower():
            raise InvalidSession(
                f"topic must be non-empty and lower case with no padding, got {self.topic!r}"
            )
        if isinstance(self.minutes, bool) or not isinstance(self.minutes, int):
            raise InvalidSession(f"minutes must be a whole number, got {self.minutes!r}")
        if self.minutes <= 0:
            raise InvalidSession(f"minutes must be positive, got {self.minutes}")
        if self.minutes > MAX_MINUTES:
            raise InvalidSession(
                f"minutes must be at most {MAX_MINUTES}, got {self.minutes}"
            )

    def as_row(self) -> dict[str, str]:
        """Render this session as the dictionary one CSV row holds."""
        return {
            "ref": self.ref,
            "logged_on": self.logged_on.isoformat(),
            "topic": self.topic,
            "minutes": str(self.minutes),
        }

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Session":
        """Rebuild a session from one CSV row, through the same rules."""
        try:
            minutes = int(row["minutes"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidSession(f"minutes column is not a whole number: {exc}") from exc
        try:
            logged_on = date.fromisoformat(row["logged_on"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidSession(f"logged_on column is not an ISO date: {exc}") from exc
        return cls(
            ref=row.get("ref", ""),
            logged_on=logged_on,
            topic=row.get("topic", ""),
            minutes=minutes,
        )


def _looks_like_ref(ref: str) -> bool:
    """True when ref is the letter S, a hyphen, and exactly three digits."""
    return (
        len(ref) == 5
        and ref[0] == "S"
        and ref[1] == "-"
        and ref[2:].isdigit()
    )


class PracticeStore:
    """A practice log kept in one CSV file.

    Every read goes to the file, so the store never holds a stale copy. That is
    a deliberate design choice for this lab: it makes the store slow enough
    that the cost of rebuilding it in every test is visible, which is exactly
    the pressure that makes fixtures and their scopes worth learning.
    """

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def initialise(self) -> "PracticeStore":
        """Create the file with its header row, replacing anything there."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=FIELDNAMES).writeheader()
        return self

    def add(self, session: Session) -> Session:
        """Append one session, refusing a reference the store already holds."""
        if any(existing.ref == session.ref for existing in self.all()):
            raise DuplicateRef(f"{session.ref} is already in the log")
        with self.path.open("a", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=FIELDNAMES).writerow(session.as_row())
        return session

    def all(self) -> list[Session]:
        """Every session in the file, in the order it was written."""
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as handle:
            return [Session.from_row(row) for row in csv.DictReader(handle)]

    def find(self, ref: str) -> Session:
        """The session with this reference, or UnknownRef."""
        for session in self.all():
            if session.ref == ref:
                return session
        raise UnknownRef(f"{ref} is not in the log")

    def total_minutes(self, topic: str | None = None) -> int:
        """Total minutes practised, optionally narrowed to one topic."""
        return sum(
            session.minutes
            for session in self.all()
            if topic is None or session.topic == topic
        )

    def topics(self) -> list[str]:
        """Every distinct topic in the log, in alphabetical order."""
        return sorted({session.topic for session in self.all()})
