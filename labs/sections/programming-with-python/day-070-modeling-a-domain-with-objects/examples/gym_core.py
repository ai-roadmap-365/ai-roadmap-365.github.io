"""Northside Gym — the PURE DOMAIN CORE.

This module is the whole model of the gym: its value objects, its entities,
its invariants, and its errors. It is deliberately free of input and output.

Read the import list: `dataclasses`, `datetime`, `enum`, `re`. There is no
`json`, no `pathlib`, no `open()`, no `print()`, no `input()`, no `os`. That
is not an accident and it is not a style preference — it is the design. A
module that cannot touch a file can be tested with nothing but function
calls, can never corrupt data by surprise, and can be reused behind a CLI, a
web app, or a test harness without changing a line.

Everything here maps back to a sentence in `domain-rules.md`.
"""

import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

# ---------------------------------------------------------------------------
# Errors are part of the model (rule 11)
# ---------------------------------------------------------------------------


class GymError(Exception):
    """Base class for every rule this domain refuses to break.

    An adapter (the CLI, a web handler, a test) can catch `GymError` and know
    it is holding a *domain* problem — a broken rule — rather than a bug or a
    disk failure.
    """


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
# Value objects: defined entirely by their values, immutable, compared by value
# ---------------------------------------------------------------------------


class PlanTier(Enum):
    """The closed set of plan tiers (rule 4).

    A string would let `Plan(tier="pluss", ...)` sail through and fail months
    later. An enum makes the typo impossible: `PlanTier("pluss")` raises
    immediately, and the set of legal tiers is written down in one place.
    """

    BASIC = "basic"
    PLUS = "plus"


MEMBERSHIP_NUMBER_PATTERN = re.compile(r"^GYM-\d{4}$")
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")

#: How many check-ins each tier allows per calendar month. `None` = unlimited.
CHECKIN_LIMITS = {PlanTier.BASIC: 12, PlanTier.PLUS: None}


@dataclass(frozen=True)
class MembershipNumber:
    """A membership number, e.g. GYM-0007 (rule 2).

    A value object: two membership numbers with the same text ARE the same
    membership number. Frozen, so it can never drift after validation.
    """

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not MEMBERSHIP_NUMBER_PATTERN.match(self.value):
            raise InvalidMembershipNumber(
                f"membership number must look like GYM-0001, got {self.value!r}"
            )

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Money:
    """An amount of money in one currency (rule 5).

    Stored in whole cents, because binary floats cannot represent 0.10
    exactly and money you cannot add up exactly is money you have lost.
    Frozen and compared by value: Money(1000, "EUR") == Money(1000, "EUR").
    """

    cents: int
    currency: str

    def __post_init__(self):
        if not isinstance(self.cents, int) or isinstance(self.cents, bool):
            raise InvalidMoney(f"money must be a whole number of cents, got {self.cents!r}")
        if self.cents < 0:
            raise InvalidMoney(f"money cannot be negative, got {self.cents} cents")
        if not isinstance(self.currency, str) or not CURRENCY_PATTERN.match(self.currency):
            raise InvalidMoney(
                f"currency must be a three-letter code like EUR, got {self.currency!r}"
            )

    @staticmethod
    def zero(currency):
        """The additive identity for a currency: Money.zero('EUR')."""
        return Money(0, currency)

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise CurrencyMismatch(f"cannot add {other.currency} to {self.currency}")
        return Money(self.cents + other.cents, self.currency)

    def __str__(self):
        return f"{self.cents // 100}.{self.cents % 100:02d} {self.currency}"


@dataclass(frozen=True)
class DateRange:
    """A billing period: a start date and an end date, inclusive (rule 9)."""

    start: date
    end: date

    def __post_init__(self):
        if self.start > self.end:
            raise InvalidDateRange(f"billing period {self.start} .. {self.end} ends before it starts")

    def contains(self, day):
        """True if `day` falls inside the period (both ends included)."""
        return self.start <= day <= self.end


@dataclass(frozen=True)
class Plan:
    """A tier plus its monthly price (rule 4).

    A plan is a value object: two basic plans at 29.00 EUR are the same plan.
    Nothing about a plan has a life story of its own, so it needs no identity.
    """

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
# Entities: they have identity and a life cycle
# ---------------------------------------------------------------------------


@dataclass(eq=False)
class Member:
    """A person who belongs to the club (rules 2, 3, 6, 8).

    An ENTITY. `eq=False` turns off the dataclass's value equality on purpose
    so that identity — the membership number — decides who is who. Change a
    member's name, add fifty check-ins, switch their plan: it is still the
    same member, exactly as rule 3 says.
    """

    number: MembershipNumber
    name: str
    joined_on: date
    plan: Plan
    check_ins: list = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Member):
            return NotImplemented
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)

    def switch_plan(self, new_plan):
        """Move this member onto another plan, keeping their history (rule 8)."""
        self.plan = new_plan

    def check_ins_in_month(self, year, month):
        """How many times this member checked in during one calendar month."""
        return sum(1 for c in self.check_ins if c.day.year == year and c.day.month == month)

    def check_in(self, day):
        """Record a visit, enforcing the tier's monthly limit (rule 6).

        Raises CheckInLimitExceeded rather than quietly dropping the visit.
        """
        limit = self.plan.checkin_limit
        if limit is not None and self.check_ins_in_month(day.year, day.month) >= limit:
            raise CheckInLimitExceeded(
                f"{self.number} is on the {self.plan.tier.value} plan "
                f"and already used all {limit} check-ins in {day.year}-{day.month:02d}"
            )
        visit = CheckIn(self.number, day)
        self.check_ins.append(visit)
        return visit


@dataclass
class Club:
    """The gym itself (rules 1, 10) — the one door into the model.

    Every change to a member goes through the club, so the club is the single
    place where "no duplicate numbers" and "no unknown members" are enforced.
    """

    name: str
    members: dict = field(default_factory=dict)

    def enroll(self, member):
        """Add a new member, refusing a number already in use (rule 2)."""
        key = member.number.value
        if key in self.members:
            raise DuplicateMember(f"{key} is already a member of {self.name}")
        self.members[key] = member
        return member

    def find(self, number):
        """Look a member up by membership number, or refuse."""
        key = number.value if isinstance(number, MembershipNumber) else str(number)
        if key not in self.members:
            raise UnknownMember(f"{key} is not a member of {self.name}")
        return self.members[key]

    def check_in(self, number, day):
        """Record a visit for one member (rules 6, 7)."""
        return self.find(number).check_in(day)

    def monthly_revenue(self, currency="EUR"):
        """Sum every member's current monthly price into one amount (rule 10)."""
        total = Money.zero(currency)
        for member in sorted(self.members):
            total = total + self.members[member].plan.monthly_price
        return total

    def roster(self):
        """Members in membership-number order — deterministic, for reports."""
        return [self.members[key] for key in sorted(self.members)]
