#!/usr/bin/env python3
"""Four ways to host the same AI endpoint, priced at three traffic levels."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hosting_cost import (
    Billing,
    Option,
    Workload,
    binding_constraint,
    cheapest,
    crossover,
    free_tier_ceiling,
    scale_workload,
)

# A small AI endpoint: 20k requests a month, 400ms each, 50 KB out.
BASE = Workload(
    requests=20_000,
    seconds_per_request=0.4,
    gb_out_per_request=0.00004,
    storage_gb=2.0,
)

OPTIONS = [
    Option(
        "serverless-free-tier", Billing.PER_REQUEST,
        per_gb_second_usd=0.000024, per_million_requests_usd=0.40,
        free_compute_seconds=180_000, free_requests=2_000_000, free_egress_gb=1.0,
        egress_per_gb_usd=0.12, storage_per_gb_usd=0.026, free_storage_gb=5.0,
    ),
    Option(
        "serverless-paid", Billing.PER_REQUEST,
        per_gb_second_usd=0.000024, per_million_requests_usd=0.40,
        egress_per_gb_usd=0.12, storage_per_gb_usd=0.023,
    ),
    Option(
        "small-vm", Billing.ALWAYS_ON,
        hourly_usd=0.0104,                     # a 1 vCPU / 1 GB instance
        free_egress_gb=100.0, egress_per_gb_usd=0.09,
        storage_per_gb_usd=0.10,
    ),
    Option(
        "managed-container", Billing.ALWAYS_ON,
        hourly_usd=0.034,
        free_egress_gb=10.0, egress_per_gb_usd=0.12,
        storage_per_gb_usd=0.10,
    ),
]


def headroom_of(option: Option) -> dict[str, float]:
    from hosting_cost import headroom
    return headroom(option, BASE)


def table(label: str, w: Workload) -> None:
    print(f"--- {label}: {w.requests:,} requests/month ---")
    for o in OPTIONS:
        b = o.breakdown(w)
        free = "  FREE" if o.is_free(w) else ""
        print(f"  {o.name:<22} ${b['total']:>9,.2f}   "
              f"compute ${b['compute']:>8,.2f}  egress ${b['egress']:>7,.2f}"
              f"  storage ${b['storage']:>5,.2f}{free}")
    print(f"  -> cheapest: {cheapest(OPTIONS, w).name}")


def main() -> int:
    table("launch", BASE)
    table("50x", scale_workload(BASE, 50))
    table("1000x", scale_workload(BASE, 1000))

    print("--- where the free tier ends, and why ---")
    for o in OPTIONS:
        ceiling = free_tier_ceiling(o, BASE)
        which, at = binding_constraint(o, BASE)
        limit = "never in range" if at == float("inf") else f"{at:,.2f}x"
        if ceiling is None:
            state = "free throughout the range" if o.is_free(BASE) else "not free at launch"
            print(f"  {o.name:<22} {state:<26} binds on {which} at {limit}")
        else:
            w = scale_workload(BASE, ceiling)
            print(f"  {o.name:<22} free until {ceiling:>6,.2f}x ({w.requests:,}/mo)  "
                  f"binds on {which} at {limit}")
    print("  the headline allowance is rarely the one that runs out first:")
    fh = {k: v for k, v in headroom_of(OPTIONS[0]).items()}
    for k, v in sorted(fh.items(), key=lambda kv: kv[1]):
        print(f"      {k:<16} {'unused' if v == float('inf') else f'{v:,.2f}x current load'}")

    print("--- where the ranking changes ---")
    free_tier = OPTIONS[0]
    vm = OPTIONS[2]
    x = crossover(free_tier, vm, BASE)
    if x:
        w = scale_workload(BASE, x)
        print(f"  serverless-free-tier stops beating small-vm at {x:,.1f}x "
              f"({w.requests:,} requests/month)")
        print(f"    at that point: serverless ${free_tier.monthly_usd(w):,.2f} "
              f"vs vm ${vm.monthly_usd(w):,.2f}")
    else:
        print("  the ranking never changes in the range tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
