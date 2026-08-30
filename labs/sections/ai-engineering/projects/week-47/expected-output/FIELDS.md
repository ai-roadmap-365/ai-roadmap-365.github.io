# Reading the assistant output

## Ingest lines

    scanned=5 indexed=6 unchanged=0 dead=2 redactions=4

| Field | Meaning |
| --- | --- |
| `scanned` | Documents above the checkpoint cursor. Zero on a second run means the cursor advanced correctly. |
| `indexed` | Chunks written. |
| `unchanged` | Documents whose content hash matched, so the expensive path was skipped. |
| `dead` | Documents dead-lettered — no body, or a failed quality gate. |
| `redactions` | Identifiers replaced. This happens **before** chunking, so no vector carries them. |

The three runs together demonstrate the properties: run 1 ingests, run 2 scans nothing because the cursor has not moved, run 3 picks up a single edited document.

## Answer lines

    [small] What is the refund window? -- sources: refunds::0, sla::0, sla::1

The model in brackets is the routing decision. The sources are chunk ids, so an answer can be traced to what produced it.

## Cost line

    total=$0.00230  by stage: cache=$0.00000, large=$0.00210, retrieval=$0.00002, small=$0.00017

Attribution across stages, not a single total. Two things worth noticing: `retrieval` appears alongside the models, because it is charged to the same budget; and `large` is 91 percent of spend from one of three questions.

## Erasure line

    verified: {'index': True, 'hashes': True, 'cache': True}

Each value comes from a **read-back** after the deletes, not from the deletes returning. All three must be true for the erasure to be complete — and the cache is the store most often missed.
