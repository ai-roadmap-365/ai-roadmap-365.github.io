# Reading the cost output

## The per-configuration lines

    cache, trimmed ctx     calls=6 cached=2 total=$0.0066  per_request=$0.00109
                           by model: cache=$0.0000, large=$0.0061, small=$0.0005

| Field | Meaning |
| --- | --- |
| `calls` | Entries in the ledger, including cache hits. |
| `cached` | How many of those were hits. Recorded as zero-cost calls rather than skipped, so the hit rate stays visible. |
| `total` | Dollar spend for the workload. |
| `per_request` | Total divided by calls — the number that gets multiplied by volume. |
| `by model` | Attribution. This line is the whole point: a total says what you spent, attribution says where to act. |

## Why `by model` matters more than `total`

Compare the baseline and the cached run:

    no cache    large=$0.0073, small=$0.0012     total $0.0085
    + cache     large=$0.0073, small=$0.0006     total $0.0079

The cache changed only the small-model column. The large model — 86 percent of spend from two of six requests — was untouched, because the repeated question was a cheap one.

A dashboard reporting "33% cache hit rate" would call this a success. The attribution shows it saved 7 percent.

## The budget line

    tight budget           STOPPED: request would cost $0.0036, only $0.0009 left

The cap is checked **before** the call. Spend stops at or below the budget rather than overshooting by the size of the last request. Note also that the pipeline degrades — downgrading large-model requests to the small model — before it refuses outright.

## The projection

    projection at 1M requests: $1,092 (from $0.00109 per request)

Cost per request multiplied by expected volume. This belongs in a design document before the feature ships, not in a retrospective after the invoice.
