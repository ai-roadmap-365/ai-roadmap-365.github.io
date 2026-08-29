"""Northside Gym — the CLI ADAPTER (the outermost ring).

Run it:  python3 starter/demo.py [path-to-json]   (default: club.json)

This file does every messy thing the core refuses to do: it prints, it takes
a command-line argument, it decides an exit code, and it turns domain errors
into sentences a human can act on. It holds no rules of its own — every rule
it appears to apply is really enforced one layer in, by the model.

Provided complete — you do not need to edit this file. It is here so that the
moment your core and repository are finished, you have a working program. If
you ever feel tempted to put a rule in here, that is the signal the rule
belongs in `gym_core.py` instead.
"""

import sys
from datetime import date

from gym_core import (
    Club,
    GymError,
    Member,
    MembershipNumber,
    Money,
    Plan,
    PlanTier,
)
from gym_repository import JsonClubRepository

BASIC = Plan(PlanTier.BASIC, Money(2900, "EUR"))
PLUS = Plan(PlanTier.PLUS, Money(4900, "EUR"))


def build_club():
    """Create a small, fixed club. Pure: no files, no clock, no randomness."""
    club = Club("Northside Gym")
    club.enroll(Member(MembershipNumber("GYM-0001"), "Ada", date(2026, 1, 15), BASIC))
    club.enroll(Member(MembershipNumber("GYM-0002"), "Grace", date(2026, 2, 1), PLUS))
    club.enroll(Member(MembershipNumber("GYM-0003"), "Ada", date(2026, 3, 9), BASIC))
    for day in (3, 5, 8, 10):
        club.check_in(MembershipNumber("GYM-0001"), date(2026, 4, day))
    for day in range(1, 16):
        club.check_in(MembershipNumber("GYM-0002"), date(2026, 4, day))
    return club


def print_roster(club):
    print(f"{club.name} — roster")
    for member in club.roster():
        print(
            f"  {member.number}  {member.name:<6} joined {member.joined_on}  "
            f"plan {member.plan}  April check-ins: {member.check_ins_in_month(2026, 4)}"
        )
    print(f"  monthly revenue: {club.monthly_revenue()}")


def show_rules_being_enforced(club):
    """Break each rule on purpose and print what the model says. Adapters do this."""
    print("Rules the model refuses to break")
    attempts = [
        ("a membership number that is not GYM-####", lambda: MembershipNumber("0007")),
        ("a negative price", lambda: Money(-100, "EUR")),
        ("adding dollars to euros", lambda: Money(100, "EUR") + Money(100, "USD")),
        ("enrolling a number twice", lambda: club.enroll(
            Member(MembershipNumber("GYM-0001"), "Impostor", date(2026, 5, 1), BASIC))),
        ("a member the club never met", lambda: club.find(MembershipNumber("GYM-9999"))),
        ("a 13th basic check-in in one month", lambda: [
            club.check_in(MembershipNumber("GYM-0003"), date(2026, 4, d)) for d in range(1, 14)
        ]),
    ]
    for label, attempt in attempts:
        try:
            attempt()
        except GymError as err:
            print(f"  {label}: {type(err).__name__}: {err}")
        else:
            print(f"  {label}: NOT REFUSED — the model has a hole")


def main(argv):
    path = argv[1] if len(argv) > 1 else "club.json"
    try:
        club = build_club()
        print_roster(club)
        print()

        repository = JsonClubRepository(path)
        repository.save(club)
        reloaded = repository.load()
        same = [
            reloaded.name == club.name,
            reloaded.roster() == club.roster(),
            reloaded.monthly_revenue() == club.monthly_revenue(),
            reloaded.find(MembershipNumber("GYM-0002")).check_ins_in_month(2026, 4) == 15,
        ]
        print(f"Saved to {path} and reloaded — round trip intact: {all(same)}")
        print()

        show_rules_being_enforced(club)
    except GymError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
