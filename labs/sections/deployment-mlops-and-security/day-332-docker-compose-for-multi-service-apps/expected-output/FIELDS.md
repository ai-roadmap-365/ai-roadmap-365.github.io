# Reading the compose graph report

## The start order

    start order  postgres -> qdrant -> api -> worker

A topological order of the dependency graph, ties broken by name so the result
is stable. It says what starts before what. It says nothing about when anything
is *usable*, which is the next line and the whole point.

## The readiness line

    usable at    api 1.2s  postgres 4.4s  qdrant 2.3s  worker 1.2s

When each service can actually serve. Read `api` against `postgres`:

    api      usable at 1.2s
    postgres usable at 4.4s

The api is up three seconds before the database it queries can answer. That is
not a bug in the model — it is exactly what `depends_on` without a condition
means, and the report exists to make it visible.

## The findings

| Rule | Severity | Meaning |
| --- | --- | --- |
| `dependency-cycle` | fatal | Nothing in the cycle can ever start. Suppresses the timing findings, because there is no order. |
| `undefined-dependency` | error | A `depends_on` naming a service the file does not define. |
| `port-conflict` | error | Two services binding the same **host** port. |
| `starts-before-ready` | warning | A dependant begins before its dependency can answer. |
| `healthy-without-healthcheck` | error | Something waits for `service_healthy` on a service that defines no healthcheck, so the condition can never be satisfied. |

## The three conditions

| Condition | Waits for | When to use it |
| --- | --- | --- |
| `service_started` | The container exists. | Almost never on its own — this is the default and the source of the problem. |
| `service_healthy` | The healthcheck passed. | Anything a dependant will immediately query. |
| `service_completed_successfully` | A one-shot job exited zero. | Migrations, seeding, index building. |

## What the condition changed

    api usable at    1.2s  ->  5.2s
    worker usable at 1.2s  ->  5.8s
    premature starts 4  ->  0

**The correct stack is slower.** That is not a cost to be weighed — at 1.2s the
api was not usable, it was merely running, and any query it issued would have
failed. The second column is the first honest measurement of when the stack
works.

This is the reverse of the usual optimisation story, and it is why
`test_waiting_properly_is_slower_and_that_is_the_point` exists: a student who
"improves" the numbers has broken the lesson.

## Only the host side of a port can conflict

    port-conflict  host port 8000 is claimed by 2 services: api, worker

Two containers may both listen on 8080 internally; they are in separate network
namespaces. `ports: ["8000:8080"]` binds 8000 on the host, and the host has one
of each.
