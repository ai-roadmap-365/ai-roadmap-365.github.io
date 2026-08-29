"""Northside Gym — the PERSISTENCE ADAPTER (a repository).

This module is the *only* place in the lab that knows the club is stored as
JSON on disk. It imports `json` and `pathlib`; the core imports neither.

The point of the split: if the owner later wants SQLite, or a different JSON
shape, or a remote service, you rewrite this one class and the domain core
never notices. That is what "persistence is a boundary concern" means in
practice.
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
    """Loads and saves a Club as a JSON file.

    Two public methods — `save` and `load` — plus two private translators.
    The translators exist because the domain objects are the shape the *rules*
    want, and JSON is the shape the *file format* wants; keeping the mapping
    in one place stops file concerns from leaking into the model.
    """

    def __init__(self, path):
        self.path = Path(path)

    # -- domain -> plain data -------------------------------------------------

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
        number = MembershipNumber(raw["number"])
        plan = Plan(
            PlanTier(raw["plan"]["tier"]),
            Money(raw["plan"]["price_cents"], raw["plan"]["currency"]),
        )
        member = Member(
            number=number,
            name=raw["name"],
            joined_on=date.fromisoformat(raw["joined_on"]),
            plan=plan,
        )
        member.check_ins = [CheckIn(number, date.fromisoformat(d)) for d in raw["check_ins"]]
        return member

    # -- the two operations the rest of the program is allowed to call --------

    def save(self, club):
        """Write the whole club to `self.path` as JSON. Deterministic order."""
        payload = {
            "club": club.name,
            "members": [self._member_to_dict(m) for m in club.roster()],
        }
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return self.path

    def load(self):
        """Read `self.path` back into a fully valid Club.

        Every value goes back through the domain constructors, so a hand-edited
        file with a bad membership number or a negative price is rejected here
        rather than silently poisoning the model.
        """
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        club = Club(raw["club"])
        for member_raw in raw["members"]:
            club.enroll(self._member_from_dict(member_raw))
        return club
