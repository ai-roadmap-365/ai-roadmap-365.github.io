"""Northside Gym — the PERSISTENCE ADAPTER (your working file).

This is the ONLY file in your program allowed to know that the club lives in
a JSON file. It imports `json` and `pathlib`; `gym_core.py` imports neither,
and that asymmetry is the whole design.

Finish Exercise 7 below. When you have, swapping JSON for a different format
later means editing this one class and nothing else.
"""

import json
from datetime import date
from pathlib import Path

from gym_core import (
    CheckIn,
    Club,
    Member,
    MembershipNumber,
    Money,
    Plan,
    PlanTier,
)


class JsonClubRepository:
    """Loads and saves a Club as a JSON file."""

    def __init__(self, path):
        self.path = Path(path)

    # -- domain -> plain data (provided) --------------------------------------

    @staticmethod
    def _member_to_dict(member):
        return {
            "number": member.number.value,
            "name": member.name,
            "joined_on": member.joined_on.isoformat(),
            "plan": {
                "tier": member.plan.tier.value,
                "price_cents": member.plan.monthly_price.cents,
                "currency": member.plan.monthly_price.currency,
            },
            "check_ins": [c.day.isoformat() for c in member.check_ins],
        }

    # -- plain data -> domain -------------------------------------------------

    @staticmethod
    def _member_from_dict(raw):
        # EXERCISE 7a: rebuild a Member from the dict `_member_to_dict` wrote.
        # Build the value objects FIRST — MembershipNumber(raw["number"]),
        # Money(raw["plan"]["price_cents"], raw["plan"]["currency"]),
        # Plan(PlanTier(raw["plan"]["tier"]), that money) — so a hand-edited
        # file with a bad number or a negative price is refused right here.
        # Use date.fromisoformat() for the dates, then attach the check-ins:
        #   member.check_ins = [CheckIn(number, date.fromisoformat(d))
        #                       for d in raw["check_ins"]]
        raise NotImplementedError("Exercise 7a: rebuild a Member from plain data")

    # -- the two operations the rest of the program is allowed to call --------

    def save(self, club):
        # EXERCISE 7b: write {"club": club.name, "members": [...]} to
        # self.path as JSON with indent=2 and a trailing newline, using
        # club.roster() so the order is deterministic. Return self.path.
        # Path.write_text(text, encoding="utf-8") is the whole write.
        raise NotImplementedError("Exercise 7b: save the club as JSON")

    def load(self):
        # EXERCISE 7c: read self.path with Path.read_text(encoding="utf-8"),
        # json.loads it, build a Club(raw["club"]), and enroll every member
        # rebuilt by _member_from_dict. Return the club.
        raise NotImplementedError("Exercise 7c: load the club back from JSON")
