# Reading the delivery gate

## The verdict line

    solid=4 weak=4 stale=1 missing=1  NOT READY (5 blocking)

| Part | Meaning | What it needs |
| --- | --- | --- |
| solid | Backed by evidence somebody else could check, recently. | nothing |
| weak | Backed by a claim rather than a check. | replace the claim with a command, URL or measurement |
| stale | Was checkable once and has not been re-checked. | re-run one command |
| missing | No evidence at all. | do the work |
| READY / NOT READY | Whether any **blocking** requirement is unsatisfied. | — |

Nine of the ten requirements in the demo have *something* offered for them, and
the delivery is still not ready. That gap — between everything having been
thought about and everything being checkable — is what the gate exists to find.

## The evidence kinds, in ascending order of worth

| Kind | Example | Checkable |
| --- | --- | --- |
| `none` | nothing offered | no |
| `assertion` | "monitoring is set up" | no |
| `file` | `security-review.md` exists | no |
| `url` | a dashboard somebody can open | yes |
| `command` | `curl -f $URL/healthz` | yes |
| `measurement` | `p95 840ms` | yes |

The line falls between `file` and `url`, and it is worth defending. A document
existing is evidence that a document exists. It is not evidence that the review
it describes was done, or that its findings were acted on. A command is
different in kind: somebody who does not trust you can run it and watch it
fail.

## The per-requirement table

    weak    ! day 359  A rollback that has been exercised     assertion
    missing ! day 360  A hard spend cap                       -

| Column | Meaning |
| --- | --- |
| category | solid, stale, weak or missing. |
| `!` | The requirement is blocking. A blank means delivery can proceed without it. |
| day | Which day of week 52 introduced the requirement. |
| kind | The best evidence offered, or `-` for none. |

The categories are exclusive and assigned in the order missing, weak, stale,
solid — because the advice differs. Missing needs the work done; weak needs the
claim replaced; stale needs one command re-run.

## Best evidence, not first listed

A requirement backed by both an assertion and a command is backed by the
command. The order somebody happened to list their evidence in must not change
the verdict, which is why `evidence_for` takes the maximum by kind rather than
the first match.

In the demo, `demo` is offered both "the demo works" and `bash scripts/demo.sh`,
and it correctly lands in `solid`.

## Undated evidence

Evidence with no `verified_on` is treated as ancient rather than fresh. This is
deliberate and it is the asymmetry that makes the gate safe: an undated claim
is one nobody has checked recently enough to remember when, and defaulting it
to fresh would let the least verified evidence in the delivery pass silently.
