# Reading the deployment output

## An event line

      rolled_back  error rate 9.0% exceeds budget 2.0%

| Part | Meaning |
| --- | --- |
| stage | `preflight`, `deploying`, `canary`, `promoted`, `rolled_back` or `blocked`. |
| detail | Why. On a block, every reason at once; on a rollback, which signal failed and by how much. |

## A summary line

      => rolled_back live=v1.0.0 traffic_to_new=0%

| Field | Meaning |
| --- | --- |
| stage | The last event's stage — where the release path stopped. |
| `live` | Which version is serving now. On any failure this must be the *old* one. |
| `traffic_to_new` | Percentage routed to the new version. Zero after any failure, 100 after promotion. |

## The six stages

| Stage | Meaning |
| --- | --- |
| `blocked` | Preflight refused. **Nothing was deployed** — `live` is unchanged and traffic is zero. |
| `deploying` | The new version is rolling out. |
| `canary` | A fraction of real traffic is on the new version, pending a decision. |
| `promoted` | All traffic moved, and the outgoing version recorded so rollback is possible. |
| `rolled_back` | Returned to the previous version. Reachable from health, from canary, or manually. |

## What to compare

Run the demo and read how far each failure travelled before something stopped it:

- **preflight** — nothing deployed, no user affected;
- **health** — deployed, no user affected;
- **canary** — 10 percent of users saw errors;
- **after promotion** — everyone did.

Same defect, four very different costs. That gradient is why the gates exist.
