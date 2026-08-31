"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.

Price a hosting option honestly, including the parts the pricing page omits.

Offline and standard-library only. No cloud account, no API calls, no spending.

A free tier is a real offer with an edge, and the edge is rarely where the
headline suggests. Four things decide what you actually pay, and only the first
appears on the front page:

  compute     per hour, or per request-second, or free below a threshold
  egress      per GB leaving the provider. Free tiers rarely include much
  idle        an always-on VM bills at 3am; scale-to-zero does not
  storage     small, steady, and the one people forget entirely

The interesting question is not "which is cheapest". It is "at what traffic
does the ranking change", because the answer is usually far lower than people
expect and the cheapest option at launch is frequently the most expensive one
six months later.

Nothing here judges reliability or developer experience, and -- importantly --
nothing here checks CAPACITY. The model will happily price a single 1 vCPU VM
serving twenty million requests a month, which it could not actually do. It
answers "what would this cost", not "would this work", and the second question
has to be answered separately.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
HOURS_PER_MONTH = 730

class Billing(str, Enum):
    ALWAYS_ON = 'always-on'
    PER_REQUEST = 'per-request'

@dataclass(frozen=True)
class Workload:
    """What the service is asked to do in a month."""
    requests: int
    seconds_per_request: float
    gb_out_per_request: float
    storage_gb: float = 1.0

    @property
    def compute_seconds(self) -> float:
        raise NotImplementedError('TASK 1: implement compute_seconds.')

    @property
    def egress_gb(self) -> float:
        raise NotImplementedError('TASK 2: implement egress_gb.')

@dataclass(frozen=True)
class Option:
    """A hosting option, priced the way providers actually price them."""
    name: str
    billing: Billing
    hourly_usd: float = 0.0
    per_gb_second_usd: float = 0.0
    per_million_requests_usd: float = 0.0
    free_compute_seconds: float = 0.0
    free_requests: float = 0.0
    free_egress_gb: float = 0.0
    egress_per_gb_usd: float = 0.0
    storage_per_gb_usd: float = 0.0
    free_storage_gb: float = 0.0

    def compute_usd(self, w: Workload) -> float:
        raise NotImplementedError('TASK 3: implement compute_usd.')

    def egress_usd(self, w: Workload) -> float:
        raise NotImplementedError('TASK 4: implement egress_usd.')

    def storage_usd(self, w: Workload) -> float:
        raise NotImplementedError('TASK 5: implement storage_usd.')

    def monthly_usd(self, w: Workload) -> float:
        raise NotImplementedError('TASK 6: implement monthly_usd.')

    def breakdown(self, w: Workload) -> dict[str, float]:
        raise NotImplementedError('TASK 7: implement breakdown.')

    def is_free(self, w: Workload) -> bool:
        raise NotImplementedError('TASK 8: implement is_free.')

def headroom(option: Option, w: Workload) -> dict[str, float]:
    """How many times the current workload each free allowance would absorb.

    A dimension with no free allowance has no headroom at all, and one that is
    unused reports infinity. The smallest finite number is the one that decides
    when the free tier ends.
    """
    raise NotImplementedError('TASK 9: implement headroom. How many times the current workload each free allowance would absorb.')

def binding_constraint(option: Option, w: Workload) -> tuple[str, float]:
    """Which free allowance runs out first, and at what multiple of this load.

    This is the number that matters and the one no pricing page prints. A free
    tier advertising two million requests can end at 1.25x current traffic
    because the egress allowance is a single gigabyte.
    """
    raise NotImplementedError('TASK 10: implement binding_constraint. Which free allowance runs out first, and at what multiple of this load.')

def cheapest(options: list[Option], w: Workload) -> Option:
    """Cheapest option for this workload, ties broken by name for stability."""
    raise NotImplementedError('TASK 11: implement cheapest. Cheapest option for this workload, ties broken by name for stability.')

def scale_workload(w: Workload, factor: float) -> Workload:
    """The same shape of traffic, more of it. Storage grows more slowly."""
    raise NotImplementedError('TASK 12: implement scale_workload. The same shape of traffic, more of it. Storage grows more slowly.')

def crossover(a: Option, b: Option, base: Workload, *, max_factor: float=10000.0) -> float | None:
    """The traffic multiple at which the cheaper option stops being cheaper.

    Returned as a multiple of the base workload. None if the ranking never
    changes within the search range -- which is itself a useful answer, because
    it means the choice is not sensitive to growth.
    """
    raise NotImplementedError('TASK 13: implement crossover. The traffic multiple at which the cheaper option stops being cheaper.')

def free_tier_ceiling(option: Option, base: Workload, *, max_factor: float=10000.0) -> float | None:
    """How much traffic the free tier absorbs, as a multiple of the base.

    None if the option is not free even at the base workload, or if it stays
    free all the way to the search limit.
    """
    raise NotImplementedError('TASK 14: implement free_tier_ceiling. How much traffic the free tier absorbs, as a multiple of the base.')
