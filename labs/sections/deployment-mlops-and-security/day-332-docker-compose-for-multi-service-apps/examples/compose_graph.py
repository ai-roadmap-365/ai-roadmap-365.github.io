"""Work out what a Compose file will actually do before you run it.

Offline and standard-library only. Docker Compose is not required: the input is
a parsed service graph, and the questions worth asking are graph questions.

A multi-service application is a dependency graph, and three things go wrong in
it that are all visible before anything starts:

  cycles          a depends on b depends on a -- nothing can ever start
  port clashes    two services claiming the same host port
  false ordering  depends_on waits for the container, NOT for the service

The third is the one that bites. `depends_on` means "start this container
first". It does not mean "wait until the database can accept a connection", so
an API that starts in 200ms against a Postgres that takes 4 seconds to accept
connections will crash on its first query -- reliably in CI, intermittently on
a laptop, which is the worst possible failure distribution.

The fix is a condition: service_healthy plus a healthcheck. This module shows
the difference the condition makes to the order things are actually usable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Condition(str, Enum):
    """What `depends_on` actually waits for."""

    STARTED = "service_started"    # the container exists. Says nothing about readiness.
    HEALTHY = "service_healthy"    # the healthcheck passed.
    COMPLETED = "service_completed_successfully"  # a one-shot job finished.


@dataclass(frozen=True)
class Dependency:
    on: str
    condition: Condition = Condition.STARTED


@dataclass
class Service:
    name: str
    image: str
    ports: list[tuple[int, int]] = field(default_factory=list)  # (host, container)
    depends_on: list[Dependency] = field(default_factory=list)
    healthcheck: bool = False
    start_seconds: float = 0.5      # until the container is running
    ready_seconds: float = 0.5      # until it can actually serve

    @property
    def host_ports(self) -> list[int]:
        return [h for h, _ in self.ports]


@dataclass(frozen=True)
class Finding:
    rule: str
    service: str
    message: str


def find_cycles(services: dict[str, Service]) -> list[list[str]]:
    """Every dependency cycle, each reported once starting from its smallest name.

    A cycle means nothing in it can ever start, so this is a hard error rather
    than a warning.
    """
    seen: set[tuple[str, ...]] = set()
    out: list[list[str]] = []

    def walk(node: str, path: list[str]) -> None:
        if node in path:
            cycle = path[path.index(node):]
            rotated = min(
                (tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))),
                default=(),
            )
            if rotated and rotated not in seen:
                seen.add(rotated)
                out.append(list(rotated))
            return
        svc = services.get(node)
        if not svc:
            return
        for dep in svc.depends_on:
            walk(dep.on, path + [node])

    for name in sorted(services):
        walk(name, [])
    return out


def missing_dependencies(services: dict[str, Service]) -> list[Finding]:
    """Dependencies naming a service the file does not define."""
    out: list[Finding] = []
    for name in sorted(services):
        for dep in services[name].depends_on:
            if dep.on not in services:
                out.append(
                    Finding("undefined-dependency", name,
                            f"depends on '{dep.on}', which no service defines")
                )
    return out


def port_conflicts(services: dict[str, Service]) -> list[Finding]:
    """Two services publishing the same host port.

    Only the HOST side conflicts. Two containers may both listen on 8080
    internally -- they are on different network namespaces.
    """
    claims: dict[int, list[str]] = {}
    for name in sorted(services):
        for port in services[name].host_ports:
            claims.setdefault(port, []).append(name)
    return [
        Finding("port-conflict", ", ".join(names),
                f"host port {port} is claimed by {len(names)} services: {', '.join(names)}")
        for port, names in sorted(claims.items())
        if len(names) > 1
    ]


def startup_order(services: dict[str, Service]) -> list[str]:
    """A topological order, ties broken by name so the result is stable.

    Raises if the graph has a cycle, because there is no valid order.
    """
    cycles = find_cycles(services)
    if cycles:
        raise ValueError(f"dependency cycle: {' -> '.join(cycles[0] + [cycles[0][0]])}")
    order: list[str] = []
    placed: set[str] = set()
    while len(order) < len(services):
        ready = sorted(
            n for n in services
            if n not in placed
            and all(d.on in placed or d.on not in services for d in services[n].depends_on)
        )
        if not ready:
            raise ValueError("no service can start; check the dependency graph")
        for n in ready:
            order.append(n)
            placed.add(n)
    return order


def ready_times(services: dict[str, Service]) -> dict[str, float]:
    """When each service can actually serve, honouring the depends_on condition.

    This is the whole point. With service_started a dependant waits only for the
    container; with service_healthy it waits until the dependency is usable.
    """
    times: dict[str, float] = {}
    for name in startup_order(services):
        svc = services[name]
        begins = 0.0
        for dep in svc.depends_on:
            if dep.on not in services:
                continue
            target = services[dep.on]
            if dep.condition is Condition.STARTED:
                begins = max(begins, times[dep.on] - target.ready_seconds)
            else:
                begins = max(begins, times[dep.on])
        times[name] = round(begins + svc.start_seconds + svc.ready_seconds, 2)
    return times


def premature_starts(services: dict[str, Service]) -> list[Finding]:
    """Services that will begin work before a dependency can answer them."""
    times = ready_times(services)
    out: list[Finding] = []
    for name in sorted(services):
        svc = services[name]
        began = times[name] - svc.ready_seconds - svc.start_seconds
        for dep in svc.depends_on:
            target = services.get(dep.on)
            if not target or dep.condition is not Condition.STARTED:
                continue
            if times[dep.on] > began + 1e-9:
                gap = round(times[dep.on] - began, 2)
                out.append(
                    Finding(
                        "starts-before-ready", name,
                        f"starts {gap}s before '{dep.on}' can answer; depends_on without a "
                        "condition waits for the container, not the service",
                    )
                )
    return out


def review(services: dict[str, Service]) -> list[Finding]:
    """Everything wrong with this graph that is visible without running it."""
    out = missing_dependencies(services) + port_conflicts(services)
    for cycle in find_cycles(services):
        out.append(
            Finding("dependency-cycle", cycle[0],
                    f"cycle: {' -> '.join(cycle + [cycle[0]])}; nothing in it can start")
        )
    if not any(f.rule == "dependency-cycle" for f in out):
        out.extend(premature_starts(services))
    for name in sorted(services):
        svc = services[name]
        depended_on = any(
            d.on == name and d.condition is Condition.HEALTHY
            for other in services.values() for d in other.depends_on
        )
        if depended_on and not svc.healthcheck:
            out.append(
                Finding("healthy-without-healthcheck", name,
                        "another service waits for service_healthy but this one defines no "
                        "healthcheck, so the condition can never be satisfied")
            )
    return out
