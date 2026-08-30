# Reading the retrospective output

## The calibration line

    median ratio 1.20x  under 6 / over 0  worst unfamiliar 3.33x  best familiar 1.15x

| Part | Meaning |
| --- | --- |
| median ratio | Actual over estimated across every task, at the median. 1.0 would be exact. |
| under / over | How many tasks ran long and how many ran short. A task at exactly 1.0 counts as neither. |
| worst | The area with the highest median ratio, and that ratio. |
| best | The area with the lowest. |

Read the median first and the last two second. If the worst and best are far
apart, the median is an average of two populations and describes neither.

## The uniformity flag

    uniform across areas: False

| Value | Meaning | What to do |
| --- | --- | --- |
| `True` | The highest area is within 1.5x of the lowest. | Apply the median as a multiplier to the next estimate. |
| `False` | The error lives in one kind of work. | Do not apply a single multiplier. Estimate the bad area differently, or split it until the pieces resemble work you have done. |

The 1.5x threshold is a judgement, not a law. It is the point at which two
areas stop being noisy versions of the same number.

## The future-estimate table

          4h estimated  ->    4.8h expected

Your own history applied to a new estimate. Note what this table is on this
record: computed from the overall median of 1.20x, and therefore **wrong for
the unfamiliar work**, where the record says 3.33x. The tool computes it; you
decide whether the uniformity flag permits you to use it.

## The detection summary

    review=1 tests=1 staging=1 monitoring=1 user=1  escaped=2 (40%)

| Stage | Meaning | Escaped |
| --- | --- | --- |
| `review` | Caught before it ran anywhere. | no |
| `tests` | Caught before it deployed. | no |
| `staging` | Deployed, no user affected. | no |
| `monitoring` | In production, a signal found it. | yes |
| `user` | In production, a person found it. | yes |

`escaped` counts the last two. Staging is deliberately not an escape: the code
was deployed, and it reached nobody.

## The findings

Sentences rather than scores, because a score is not an instruction. Four kinds
appear:

| Finding | Trigger |
| --- | --- |
| the multiplier | Median ratio above 1.0. |
| padding | Median ratio below 1.0 — estimates were conservative, which costs opportunities rather than deadlines. |
| concentrated error | The uniformity check failed. This one contradicts the multiplier finding, deliberately. |
| a named gate | One line per escaped incident that has a `preventable_by` set. |

If none of them fire, the report says the record is clean rather than
manufacturing a finding — which is the behaviour a retrospective tool most
often gets wrong.
