"""Northside Gym — the PURE DOMAIN CORE (your working file).

Everything in this module comes from a sentence in `examples/domain-rules.md`.
Your job is to finish the six numbered exercises below. Each one is a *rule*
from that page, turned into code that refuses to be broken.

THE ONE RULE FOR THIS FILE: it must never touch the outside world. Do not add
`import json`, `import os`, `open()`, `print()`, or `input()` here. The test
suite checks that this file imports nothing that does I/O, and it runs your
core from an empty directory to prove it needs no files at all.

Run the tests at any time to see where you are:

    bash tests/run_tests.sh
"""

import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

# ---------------------------------------------------------------------------
# Errors are part of the model (rule 11) — provided complete.
# ---------------------------------------------------------------------------


class GymError(Exception):
    """Base class for every rule this domain refuses to break."""


class InvalidMembershipNumber(GymError):
    """A membership number was not of the form GYM-#### (rule 2)."""


class InvalidMoney(GymError):
    """A money amount was negative or its currency code was malformed (rule 5)."""


class CurrencyMismatch(GymError):
    """Two money amounts in different currencies were combined (rule 5)."""


class InvalidDateRange(GymError):
    """A billing period ended before it started (rule 9)."""


class DuplicateMember(GymError):
    """A membership number already in the club was enrolled again (rule 2)."""


class UnknownMember(GymError):
    """A membership number that the club has never seen was used."""


class CheckInLimitExceeded(GymError):
    """A basic-tier member tried to check in a 13th time in one month (rule 6)."""


# ---------------------------------------------------------------------------
# Provided: the closed set of tiers and the limits table.
# ---------------------------------------------------------------------------


class PlanTier(Enum):
    """The only two tiers the rules allow (rule 4)."""

    BASIC = "basic"
    PLUS = "plus"


MEMBERSHIP_NUMBER_PATTERN = re.compile(r"^GYM-\d{4}$")
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")

#: How many check-ins each tier allows per calendar month. `None` = unlimited.
CHECKIN_LIMITS = {PlanTier.BASIC: 12, PlanTier.PLUS: None}


# ---------------------------------------------------------------------------
# EXERCISE 1 — the MembershipNumber value object (rule 2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MembershipNumber:
    """A membership number, e.g. GYM-0007. Frozen: it can never drift."""

    value: str

    def __post_init__(self):
        # EXERCISE 1: raise InvalidMembershipNumber unless `self.value` is a
        # string matching MEMBERSHIP_NUMBER_PATTERN. Put the offending value
        # in the message with !r so the error names what was wrong.
        # Replace the next line with your check.
        raise NotImplementedError("Exercise 1: validate the membership number")

    def __str__(self):
        return self.value


# ---------------------------------------------------------------------------
# EXERCISE 2 — the Money value object and its refusal to mix currencies (rule 5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Money:
    """An amount in whole cents, in one currency. Never a float."""

    cents: int
    currency: str

    def __post_init__(self):
        # EXERCISE 2a: raise InvalidMoney if `cents` is not an int (bools are
        # ints in Python — reject them too), if it is negative, or if
        # `currency` does not match CURRENCY_PATTERN.
        raise NotImplementedError("Exercise 2a: validate the money amount")

    @staticmethod
    def zero(currency):
        """The additive identity for a currency: Money.zero('EUR')."""
        return Money(0, currency)

    def __add__(self, other):
        # EXERCISE 2b: return NotImplemented if `other` is not Money; raise
        # CurrencyMismatch if the currencies differ; otherwise return a NEW
        # Money with the summed cents. Never mutate self — it is frozen.
        raise NotImplementedError("Exercise 2b: add two money amounts safely")

    def __str__(self):
        return f"{self.cents // 100}.{self.cents % 100:02d} {self.currency}"


# ---------------------------------------------------------------------------
# EXERCISE 3 — the DateRange value object (rule 9)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DateRange:
    """A billing period: start and end dates, both included."""

    start: date
    end: date

    def __post_init__(self):
        # EXERCISE 3a: raise InvalidDateRange if start is after end.
        raise NotImplementedError("Exercise 3a: reject a backwards billing period")

    def contains(self, day):
        # EXERCISE 3b: return True if `day` falls inside the period, ends
        # included. One comparison expression is enough.
        raise NotImplementedError("Exercise 3b: is this day inside the period?")


# ---------------------------------------------------------------------------
# Provided: Plan and CheckIn, two more value objects.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Plan:
    """A tier plus its monthly price (rule 4)."""

    tier: PlanTier
    monthly_price: Money

    @property
    def checkin_limit(self):
        """Check-ins allowed per calendar month; None means unlimited (rule 6)."""
        return CHECKIN_LIMITS[self.tier]

    def __str__(self):
        return f"{self.tier.value} ({self.monthly_price})"


@dataclass(frozen=True)
class CheckIn:
    """A member walked in on a day (rule 7). Frozen: history never changes."""

    member: MembershipNumber
    day: date


# ---------------------------------------------------------------------------
# EXERCISE 4 and 5 — the Member entity (rules 3, 6, 8)
# ---------------------------------------------------------------------------


@dataclass(eq=False)
class Member:
    """A person who belongs to the club. An ENTITY: identity, not values.

    `eq=False` switches off the dataclass's value equality deliberately, so
    you can define identity equality yourself in Exercise 4.
    """

    number: MembershipNumber
    name: str
    joined_on: date
    plan: Plan
    check_ins: list = field(default_factory=list)

    def __eq__(self, other):
        # EXERCISE 4a: two Members are equal when their membership NUMBERS are
        # equal — rule 3. Return NotImplemented for anything that is not a
        # Member.
        raise NotImplementedError("Exercise 4a: identity equality by membership number")

    def __hash__(self):
        # EXERCISE 4b: hash the identity, not the whole object, so a Member can
        # live in a set or a dict key and stay findable after their name or
        # plan changes.
        raise NotImplementedError("Exercise 4b: hash the identity")

    def switch_plan(self, new_plan):
        """Move this member onto another plan, keeping their history (rule 8)."""
        self.plan = new_plan

    def check_ins_in_month(self, year, month):
        """How many times this member checked in during one calendar month."""
        return sum(1 for c in self.check_ins if c.day.year == year and c.day.month == month)

    def check_in(self, day):
        # EXERCISE 5: enforce rule 6. Read the tier's limit from
        # `self.plan.checkin_limit`. If it is not None and this member already
        # has that many check-ins in `day`'s month, raise CheckInLimitExceeded
        # with a message naming the member, the tier, the limit, and the month.
        # Otherwise build a CheckIn, append it to self.check_ins, and return it.
        raise NotImplementedError("Exercise 5: enforce the monthly check-in limit")


# ---------------------------------------------------------------------------
# EXERCISE 6 — the Club entity, the one door into the model (rules 1, 10)
# ---------------------------------------------------------------------------


@dataclass
class Club:
    """The gym itself. Every change to a member goes through here."""

    name: str
    members: dict = field(default_factory=dict)

    def enroll(self, member):
        # EXERCISE 6a: store `member` under the key `member.number.value`.
        # Raise DuplicateMember if that key is already present (rule 2).
        # Return the member so callers can chain.
        raise NotImplementedError("Exercise 6a: enroll a member, refusing duplicates")

    def find(self, member_number):
        # EXERCISE 6b: accept either a MembershipNumber or a plain string,
        # look the member up, and raise UnknownMember if there is no such key.
        raise NotImplementedError("Exercise 6b: find a member or refuse")

    def check_in(self, member_number, day):
        """Record a visit for one member (rules 6, 7)."""
        return self.find(member_number).check_in(day)

    def monthly_revenue(self, currency="EUR"):
        """Sum every member's current monthly price into one amount (rule 10)."""
        total = Money.zero(currency)
        for key in sorted(self.members):
            total = total + self.members[key].plan.monthly_price
        return total

    def roster(self):
        """Members in membership-number order — deterministic, for reports."""
        return [self.members[key] for key in sorted(self.members)]
