"""The same two models expressed for the from-scratch validator.

Put this file beside ``models.py`` and read them together. The shapes are
identical; what differs is how much of "valid" each one can actually say.

The miniature validator understands types, presence, nullability, nesting and
unexpected keys. It has no vocabulary at all for ranges, patterns, lengths,
dates, aliases or cross-field rules — every one of those would have to be
hand-written per field, which is precisely how hand-written validation rots.
"""

from __future__ import annotations

from scratch_validator import MiniModel


class ScratchStation(MiniModel):
    code: str
    name: str
    elevation_m: int


class ScratchReading(MiniModel):
    reading_id: str
    station: ScratchStation
    recorded_at: str
    pm2_5: float
    temperature_c: float
    humidity_pct: int
    operator: str | None
    notes: str | None = None
