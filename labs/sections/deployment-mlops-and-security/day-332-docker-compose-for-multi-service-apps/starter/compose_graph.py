"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.

Work out what a Compose file will actually do before you run it.

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
    STARTED = 'service_started'
    HEALTHY = 'service_healthy'
    COMPLETED = 'service_completed_successfully'

@dataclass(frozen=True)
class Dependency:
    on: str
    condition: Condition = Condition.STARTED

@dataclass
class Service:
    name: str
    image: str
    ports: list[tuple[int, int]] = field(default_factory=list)
    depends_on: list[Dependency] = field(default_factory=list)
    healthcheck: bool = False
    start_seconds: float = 0.5
    ready_seconds: float = 0.5

    @property
    def host_ports(self) -> list[int]:
        raise NotImplementedError('TASK 1: implement host_ports.')

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
    raise NotImplementedError('TASK 3: implement find_cycles. Every dependency cycle, each reported once starting from its smallest name.')

def missing_dependencies(services: dict[str, Service]) -> list[Finding]:
    """Dependencies naming a service the file does not define."""
    raise NotImplementedError('TASK 4: implement missing_dependencies. Dependencies naming a service the file does not define.')

def port_conflicts(services: dict[str, Service]) -> list[Finding]:
    """Two services publishing the same host port.

    Only the HOST side conflicts. Two containers may both listen on 8080
    internally -- they are on different network namespaces.
    """
    raise NotImplementedError('TASK 5: implement port_conflicts. Two services publishing the same host port.')

def startup_order(services: dict[str, Service]) -> list[str]:
    """A topological order, ties broken by name so the result is stable.

    Raises if the graph has a cycle, because there is no valid order.
    """
    raise NotImplementedError('TASK 6: implement startup_order. A topological order, ties broken by name so the result is stable.')

def ready_times(services: dict[str, Service]) -> dict[str, float]:
    """When each service can actually serve, honouring the depends_on condition.

    This is the whole point. With service_started a dependant waits only for the
    container; with service_healthy it waits until the dependency is usable.
    """
    raise NotImplementedError('TASK 7: implement ready_times. When each service can actually serve, honouring the depends_on condition.')

def premature_starts(services: dict[str, Service]) -> list[Finding]:
    """Services that will begin work before a dependency can answer them."""
    raise NotImplementedError('TASK 8: implement premature_starts. Services that will begin work before a dependency can answer them.')

def review(services: dict[str, Service]) -> list[Finding]:
    """Everything wrong with this graph that is visible without running it."""
    raise NotImplementedError('TASK 9: implement review. Everything wrong with this graph that is visible without running it.')
