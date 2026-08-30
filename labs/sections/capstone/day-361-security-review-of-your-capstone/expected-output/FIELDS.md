# Reading the review output

## A finding line

      HIGH    spend_bounds: no per-request and no per-user daily cap
              fix: cap before the call, not after; anything a user can trigger
              an attacker can trigger repeatedly

| Part | Meaning |
| --- | --- |
| severity | `OK`, `LOW`, `MEDIUM` or `HIGH`, weighted by **blast radius** rather than sophistication. |
| check | Which of the seven areas. Each owns one failure. |
| detail | What was actually found, with the specifics — which scopes, which caps, which controls. |
| fix | The remediation. A finding without one is a complaint rather than a review. |

## The verdict line

      => FAIL high=6 medium=1 low=0

`PASS` requires the worst finding to be `OK` or `LOW`. Any medium or high fails — a low finding is worth recording without blocking.

## The severity scale

| Severity | Meaning |
| --- | --- |
| `HIGH` | An attacker can act, data leaves, or the service can be taken down. |
| `MEDIUM` | Real exposure by a narrower path, or one of a pair of controls missing. |
| `LOW` | Worth noting. A destructive scope that exists but is gated behind confirmation. |
| `OK` | The control is present. |

## The isolation runs

    drop the spend caps                  FAIL high=1   ['spend_bounds']

One configuration change should produce one finding. This is how you know the checks are independent, and it is what makes the output prioritisable: each finding points at exactly one decision you could reverse.

## Why two postures are reviewed

The demo reviews a sound configuration and a deliberately weak one. The second is the important half — a review that has never found anything is not evidence of safety, because a clean report and a review that checks nothing look identical from outside.
