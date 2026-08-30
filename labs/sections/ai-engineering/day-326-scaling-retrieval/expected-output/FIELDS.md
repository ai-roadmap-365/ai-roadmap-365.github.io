# Reading the sweep output

    nprobe=1  recall@10=0.81 comparisons=6192   speedup=6.5x

| Field | Meaning |
| --- | --- |
| `nprobe` | How many of the 8 inverted lists this search examined. The tuning knob. |
| `recall@10` | Mean fraction of the true top-10 that the approximate search also returned, averaged over 20 queries. Membership, not ordering. |
| `comparisons` | Total vector comparisons across all queries — `nlist` centroid comparisons per query, plus one per vector in the probed lists. |
| `speedup` | Exact search's comparisons divided by this row's. Below 1.0 means the index costs more than not having one. |

## Why comparisons rather than seconds

Wall-clock time on a laptop is dominated by interpreter overhead and whatever else is running, so it is noisy and not reproducible. Comparisons are exact, stable across machines, and are the quantity an ANN index actually reduces.

The abstraction has limits, and the lesson names them: at real scale, memory layout and cache behaviour matter as much as the comparison count, which is why a quantised index can beat an unquantised one doing the same number of comparisons.

## The target lines

    recall>=0.90: nprobe=3 (2.5x cheaper than exact)
    recall>=0.99: nprobe=8 (1.0x cheaper than exact)

These answer the question worth asking of an index — not "what is the best recall it can reach" but "what is the cheapest configuration good enough for this job". The second line is the honest one: reaching 99 percent required probing everything, which cost more than exact search.
