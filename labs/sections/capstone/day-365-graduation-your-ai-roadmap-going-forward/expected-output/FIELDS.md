# Reading the plan check

## The load line

    needs 17.0h/week  have 5.0h/week  3.40x  OVER

| Part | Meaning |
| --- | --- |
| needs | The weekly hours every commitment adds up to. |
| have | The hours you actually have, which is the number people guess rather than measure. |
| ratio | How many times over budget the plan is. 1.0 exactly fits. |
| fits / OVER | Whether the plan is executable at all. |

The plan is printed twice: as written, and re-costed at your measured
calibration from day 364. Both are shown because the gap between them is the
part optimism hides.

    as written        needs 17.0h/week   3.40x  OVER
    in my own hours   needs 20.4h/week   4.08x  OVER

## The summary line

    2 kept / 4 cut  not-actionable=3 no-artifact=3

| Field | Meaning |
| --- | --- |
| kept | Commitments that fit inside the available hours. |
| cut | Commitments that do not. Cut now and deliberately, or in week three by attrition. |
| not-actionable | The next action names a topic rather than something you could start within the hour. |
| no-artifact | Nothing will exist afterwards that did not exist before. |

## What the trim does, and what it deliberately does not

It keeps commitments highest-priority-first while they still fit, and it
**skips past one that does not fit** rather than stopping. Stopping would waste
every remaining hour.

That has a consequence worth seeing rather than hiding: a cheap low-priority
commitment can survive when a dear high-priority one does not fit at the point
it is considered.

    keep  p1   3.6h/wk  evaluation harness for my capstone
    keep  p2   1.2h/wk  writing about the work
    cut   p2   2.4h/wk  open-source contribution

The open-source contribution is the same priority as the writing and was cut,
because 3.6 + 2.4 exceeds 5.0 while 3.6 + 1.2 does not. The right response to
that output is usually to **split the expensive commitment**, not to accept the
substitution the tool made. The tool cannot make that call, and it should not
pretend to.

## The trim is not proportional

Six commitments at half the hours each is six things done badly. Two
commitments at full hours is two things done. The plan that fits is the plan
that happens, which is why the trim drops commitments rather than shaving them.

## The findings

Sentences rather than a score, because a score is not an instruction:

| Finding | Trigger |
| --- | --- |
| calibration applied | A calibration above 1.0 was used, so the reader knows which hours these are. |
| how far over | The load does not fit. |
| how many survive, and each cut named | The load does not fit. |
| rewrite this wording | A next action that names a topic, quoted so the fix is obvious. |
| name what will exist | A commitment with no artifact. |
| the plan fits | Everything fits — reported explicitly, and worth not filling. |
