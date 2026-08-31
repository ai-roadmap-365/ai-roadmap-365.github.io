# Reading the pipeline analysis

## The two durations

    wall clock   12.7 min   along checkout -> install -> integration -> deploy
    runner time  22.2 min billed
    the gap       9.5 min of work happening in parallel

| Number | Meaning | Who cares |
| --- | --- | --- |
| wall clock | The critical path — the longest chain of dependent jobs. | The person waiting for the green tick. |
| runner time | The sum of every job's duration. | Whoever pays the bill. |
| the gap | Work happening in parallel. | Nobody, directly — but it explains why the two differ. |

These are different quantities and they are optimised by different actions.
Confusing them is the mistake this lab exists to prevent.

## The finish table

        0.3 min  checkout
        4.8 min  install
        5.6 min  lint
        7.2 min  licence-scan
        7.9 min  docs-build
        8.0 min  unit
       11.3 min  integration
       12.7 min  deploy

When each job finishes, assuming enough runners. Everything from `lint` to
`integration` starts at 4.8 — they all depend on `install` and on nothing else,
so they run at the same time.

`deploy` waits for `unit`, `integration` and `lint`, so it starts when the last
of those finishes at 11.3, not when the first does.

## The findings

| Rule | Meaning |
| --- | --- |
| `dependency-cycle` | Fatal. No job in the cycle can run, and it suppresses every other finding. |
| `undefined-need` | A `needs:` naming a job the workflow does not define. |
| `secrets-exposed-to-forks` | A secret-using job under `pull_request_target`. See `security.md`. |
| `gate-never-fires` | A job that has never failed. It costs time and there is no evidence it catches anything. |
| `no-cache` | A job of three minutes or more with nothing cached. |

## The result worth reading twice

    licence-scan   NOT on the critical path   wall 12.7 -> 12.7 (saves 0.0)   runner minutes saved 2.4
    docs-build     NOT on the critical path   wall 12.7 -> 12.7 (saves 0.0)   runner minutes saved 3.1

    install 4.5 -> 0.8 min (a dependency cache)
    wall 12.7 -> 9.0 min   saves 3.7 min per run

**Deleting both useless jobs makes the pipeline zero seconds faster.** They are
not on the critical path, so nothing was waiting for them. It saves 5.5 runner
minutes, which is money, and it is not the thing anyone was complaining about.

One cache on `install` — which *is* on the critical path — saves 3.7 minutes per
run, every run, for everyone.

The general rule: **to make a pipeline faster, shorten the critical path. To
make it cheaper, remove work anywhere.** Those are different jobs, and the
instinct to delete the stage that looks pointless usually addresses the second
while the complaint was about the first.

## Removal re-points dependants

`without` does not merely delete a job. Anything that needed the removed job
inherits that job's own dependencies, because that is what happens when you
delete a stage from a real workflow. Without this, dependants become root jobs,
start immediately, and the wall-clock saving is overstated.
