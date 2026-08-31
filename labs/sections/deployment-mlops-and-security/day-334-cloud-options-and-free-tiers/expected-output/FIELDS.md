# Reading the cost table

## A row

    serverless-free-tier   $     0.00   compute $    0.00  egress $   0.00  storage $ 0.00  FREE

| Column | Meaning |
| --- | --- |
| total | The monthly bill for this workload. |
| compute | Hours for an always-on option; billed seconds and requests for a per-request one. |
| egress | Per GB leaving the provider, after any free allowance. |
| storage | Small, steady, and the line people forget entirely. |
| `FREE` | The total rounds to zero. Not the same as "inside the free tier" — see below. |

## The two billing models

| Model | Costs at zero traffic | Costs at high traffic |
| --- | --- | --- |
| `ALWAYS_ON` | The full hourly rate. A VM bills at 3am. | The same. Compute is flat. |
| `PER_REQUEST` | Nothing. This is scale-to-zero. | Grows with usage, without limit. |

That difference is the whole decision, and it is why the ranking changes with
traffic rather than being a fixed preference.

## Where the free tier ends, and why

    serverless-free-tier   free until 1.30x (26,000/mo)  binds on egress-gb at 1.25x

    the headline allowance is rarely the one that runs out first:
        egress-gb          1.25x current load
        storage-gb         2.50x current load
        compute-seconds   22.50x current load
        requests         100.00x current load

**This is the table to read.** The tier advertises two million free requests,
which at this workload is a hundred times current traffic. It ends at 1.25x,
because the egress allowance is a single gigabyte.

The advertised number and the binding number differ by a factor of eighty. No
pricing page prints the second one, and it is the only one that matters.

The small gap between "binds at 1.25x" and "free until 1.30x" is rounding: a
fraction of a gigabyte of egress costs less than a cent and shows as $0.00. The
binding constraint is the honest figure.

## Where the ranking changes

    serverless-free-tier stops beating small-vm at 45.0x (899,599 requests/month)
      at that point: serverless $8.66 vs vm $8.67

A crossover is the traffic multiple at which the cheaper option stops being
cheaper. It is computed by bisection, and `None` is a real answer meaning the
ordering never changes in the range — which tells you the choice is not
sensitive to growth.

Note how low the crossover is. Serverless is free at launch and a VM costs
$7.79; nine hundred thousand requests a month is a small service, and past it
the VM is cheaper for good.

## What this model does not do

It prices a workload. It does not check that an option can **serve** it.

At the 1000x row the model quotes `small-vm` at $90.77 for twenty million
requests a month on one vCPU, which that machine could not actually deliver.
Cost is one input to a hosting decision; capacity, reliability and blast radius
are others, and the extension exercises add the first of them.
