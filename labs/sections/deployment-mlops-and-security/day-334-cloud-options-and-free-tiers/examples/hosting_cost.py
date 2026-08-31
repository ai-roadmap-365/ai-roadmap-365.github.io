"""Price a hosting option honestly, including the parts the pricing page omits.

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
    ALWAYS_ON = "always-on"      # billed by the hour whether used or not
    PER_REQUEST = "per-request"  # billed by compute actually consumed


@dataclass(frozen=True)
class Workload:
    """What the service is asked to do in a month."""

    requests: int
    seconds_per_request: float
    gb_out_per_request: float
    storage_gb: float = 1.0

    @property
    def compute_seconds(self) -> float:
        return self.requests * self.seconds_per_request

    @property
    def egress_gb(self) -> float:
        return self.requests * self.gb_out_per_request


@dataclass(frozen=True)
class Option:
    """A hosting option, priced the way providers actually price them."""

    name: str
    billing: Billing
    hourly_usd: float = 0.0            # ALWAYS_ON only
    per_gb_second_usd: float = 0.0     # PER_REQUEST only
    per_million_requests_usd: float = 0.0
    free_compute_seconds: float = 0.0
    free_requests: float = 0.0
    free_egress_gb: float = 0.0
    egress_per_gb_usd: float = 0.0
    storage_per_gb_usd: float = 0.0
    free_storage_gb: float = 0.0

    def compute_usd(self, w: Workload) -> float:
        if self.billing is Billing.ALWAYS_ON:
            # The defining property: you pay for the hours, not the requests.
            return self.hourly_usd * HOURS_PER_MONTH
        billable = max(0.0, w.compute_seconds - self.free_compute_seconds)
        billable_requests = max(0.0, w.requests - self.free_requests)
        per_req = self.per_million_requests_usd * (billable_requests / 1_000_000)
        return billable * self.per_gb_second_usd + per_req

    def egress_usd(self, w: Workload) -> float:
        return max(0.0, w.egress_gb - self.free_egress_gb) * self.egress_per_gb_usd

    def storage_usd(self, w: Workload) -> float:
        return max(0.0, w.storage_gb - self.free_storage_gb) * self.storage_per_gb_usd

    def monthly_usd(self, w: Workload) -> float:
        return round(self.compute_usd(w) + self.egress_usd(w) + self.storage_usd(w), 2)

    def breakdown(self, w: Workload) -> dict[str, float]:
        return {
            "compute": round(self.compute_usd(w), 2),
            "egress": round(self.egress_usd(w), 2),
            "storage": round(self.storage_usd(w), 2),
            "total": self.monthly_usd(w),
        }

    def is_free(self, w: Workload) -> bool:
        return self.monthly_usd(w) == 0.0


def headroom(option: Option, w: Workload) -> dict[str, float]:
    """How many times the current workload each free allowance would absorb.

    A dimension with no free allowance has no headroom at all, and one that is
    unused reports infinity. The smallest finite number is the one that decides
    when the free tier ends.
    """
    out: dict[str, float] = {}
    pairs = (
        ("compute-seconds", option.free_compute_seconds, w.compute_seconds),
        ("requests", option.free_requests, float(w.requests)),
        ("egress-gb", option.free_egress_gb, w.egress_gb),
        ("storage-gb", option.free_storage_gb, w.storage_gb),
    )
    for name, allowance, used in pairs:
        if used <= 0:
            out[name] = float("inf")
        else:
            out[name] = allowance / used
    return out


def binding_constraint(option: Option, w: Workload) -> tuple[str, float]:
    """Which free allowance runs out first, and at what multiple of this load.

    This is the number that matters and the one no pricing page prints. A free
    tier advertising two million requests can end at 1.25x current traffic
    because the egress allowance is a single gigabyte.
    """
    h = headroom(option, w)
    name = min(h, key=lambda k: (h[k], k))
    return name, round(h[name], 2) if h[name] != float("inf") else float("inf")


def cheapest(options: list[Option], w: Workload) -> Option:
    """Cheapest option for this workload, ties broken by name for stability."""
    if not options:
        raise ValueError("no options to choose from")
    return min(options, key=lambda o: (o.monthly_usd(w), o.name))


def scale_workload(w: Workload, factor: float) -> Workload:
    """The same shape of traffic, more of it. Storage grows more slowly."""
    return Workload(
        requests=int(w.requests * factor),
        seconds_per_request=w.seconds_per_request,
        gb_out_per_request=w.gb_out_per_request,
        storage_gb=round(w.storage_gb * (1 + (factor - 1) * 0.1), 3),
    )


def crossover(a: Option, b: Option, base: Workload, *, max_factor: float = 10_000.0) -> float | None:
    """The traffic multiple at which the cheaper option stops being cheaper.

    Returned as a multiple of the base workload. None if the ranking never
    changes within the search range -- which is itself a useful answer, because
    it means the choice is not sensitive to growth.
    """
    if a.monthly_usd(base) == b.monthly_usd(base):
        return None
    a_first = a.monthly_usd(base) < b.monthly_usd(base)
    lo, hi = 1.0, max_factor
    at_hi = scale_workload(base, hi)
    if (a.monthly_usd(at_hi) < b.monthly_usd(at_hi)) == a_first:
        return None                     # same ordering at the far end
    for _ in range(60):                 # bisect; 60 halvings is ample
        mid = (lo + hi) / 2
        w = scale_workload(base, mid)
        if (a.monthly_usd(w) < b.monthly_usd(w)) == a_first:
            lo = mid
        else:
            hi = mid
    return round(hi, 2)


def free_tier_ceiling(option: Option, base: Workload, *, max_factor: float = 10_000.0) -> float | None:
    """How much traffic the free tier absorbs, as a multiple of the base.

    None if the option is not free even at the base workload, or if it stays
    free all the way to the search limit.
    """
    if not option.is_free(base):
        return None
    if option.is_free(scale_workload(base, max_factor)):
        return None
    lo, hi = 1.0, max_factor
    for _ in range(60):
        mid = (lo + hi) / 2
        if option.is_free(scale_workload(base, mid)):
            lo = mid
        else:
            hi = mid
    return round(lo, 2)
