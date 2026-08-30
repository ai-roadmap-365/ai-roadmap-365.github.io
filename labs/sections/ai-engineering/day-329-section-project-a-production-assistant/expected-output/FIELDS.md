# Reading the audit output

## A check line

      FAIL  erasure_is_complete -- still present in: cache

| Part | Meaning |
| --- | --- |
| `PASS` / `FAIL` | Whether this seam holds in the assistant under audit. |
| name | Which interaction was checked. |
| detail | Present only on failure, and names *what* was found — the offending chunk ids, the missing ledger stage, or the stores that still hold the subject. A failure without a detail is a bug report nobody can act on. |

## The summary line

    NON-CONFORMANT (2/5 checks passed)

The verdict plus the count. `CONFORMANT` requires every check to pass — these are properties, not a score to average.

## The five checks

| Check | The failure it catches |
| --- | --- |
| `redaction_before_indexing` | Identifiers reached the chunks, so they are inside the vectors and removing them means re-embedding. |
| `shared_budget` | Retrieval has its own accounting, so it is a path the spend cap does not bound. |
| `erasure_is_complete` | A deletion reached some stores and not others — usually the cache, which then keeps answering from deleted content. |
| `cursor_advances_on_failure` | A dead-lettered document blocks the head of the queue and is retried on every run. |
| `no_orphans_on_shrink` | A shorter document left stale chunks behind, still retrievable. |

## Why two assistants

The demo audits a conformant assistant and a deliberately broken one. The second is the important half: **an auditor that has never caught anything is not evidence of anything.** The broken assistant is wrong in exactly three ways, and the audit is expected to name exactly those three — no fewer, and no more.
