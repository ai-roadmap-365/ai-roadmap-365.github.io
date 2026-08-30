"""Release gates, health checks and rollback for a capstone deployment.

Offline and standard-library only. There is no container runtime and no cloud
here; what is modelled is the decision structure of a deployment, which is
where deployments actually go wrong.

Four ideas, in the order they matter:

  preflight    refuse to deploy a build that fails a stated condition
  health       distinguish "the process started" from "the system works"
  progressive  send a fraction of traffic first, and decide on evidence
  rollback     get back to the last known-good state without a rebuild

The fourth is the one that decides how bad a bad day is. A deployment you
cannot reverse is not a deployment, it is a commitment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Stage(str, Enum):
    PREFLIGHT = "preflight"
    DEPLOYING = "deploying"
    CANARY = "canary"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"
    BLOCKED = "blocked"


class DeployBlocked(RuntimeError):
    """A preflight condition failed, so nothing was deployed."""


@dataclass(frozen=True)
class Build:
    version: str
    tests_passed: bool = True
    migrations_reversible: bool = True
    secrets_present: bool = True
    image_digest: str = "sha256:deadbeef"


@dataclass
class Health:
    """What a health endpoint reports.

    `liveness` means the process is running. `readiness` means it can actually
    serve -- dependencies reachable, model loaded, index warm. Conflating them
    is why a deployment can go green while every request fails.
    """

    liveness: bool = True
    readiness: bool = True
    dependency_ok: bool = True

    @property
    def serving(self) -> bool:
        return self.liveness and self.readiness and self.dependency_ok


@dataclass
class Event:
    stage: Stage
    detail: str = ""

    def line(self) -> str:
        return f"  {self.stage.value:<12} {self.detail}" if self.detail else f"  {self.stage.value}"


@dataclass
class Deployment:
    live_version: str
    previous_version: str | None = None
    events: list[Event] = field(default_factory=list)
    traffic_to_new: int = 0  # percent

    @property
    def stage(self) -> Stage:
        return self.events[-1].stage if self.events else Stage.PREFLIGHT

    def summary(self) -> str:
        return (
            f"{self.stage.value} live={self.live_version} "
            f"traffic_to_new={self.traffic_to_new}%"
        )


def preflight(build: Build) -> list[str]:
    """Reasons this build must not be deployed. Empty means it may proceed.

    Every condition here is one that is cheap to check now and expensive to
    discover in production. An irreversible migration is the worst of them,
    because it removes the rollback that every other failure depends on.
    """
    problems: list[str] = []
    if not build.tests_passed:
        problems.append("tests did not pass")
    if not build.migrations_reversible:
        problems.append("migration is not reversible")
    if not build.secrets_present:
        problems.append("required secrets are missing")
    if not build.image_digest.startswith("sha256:"):
        problems.append("image is not pinned to a digest")
    return problems


def deploy(
    current: Deployment,
    build: Build,
    *,
    health: Health | None = None,
    canary_percent: int = 10,
    error_rate: float = 0.0,
    error_budget: float = 0.02,
) -> Deployment:
    """Run the full release path, stopping at the first thing that says no."""
    health = health or Health()

    blockers = preflight(build)
    if blockers:
        current.events.append(Event(Stage.BLOCKED, "; ".join(blockers)))
        raise DeployBlocked("; ".join(blockers))

    current.events.append(Event(Stage.DEPLOYING, f"rolling out {build.version}"))

    # A process that started is not a system that works. Readiness is the
    # question worth asking, and it is the one a naive check skips.
    if not health.serving:
        failed = [
            name
            for name, ok in (
                ("liveness", health.liveness),
                ("readiness", health.readiness),
                ("dependency", health.dependency_ok),
            )
            if not ok
        ]
        current.events.append(
            Event(Stage.ROLLED_BACK, f"health check failed: {', '.join(failed)}")
        )
        current.traffic_to_new = 0
        return current

    current.traffic_to_new = canary_percent
    current.events.append(Event(Stage.CANARY, f"{canary_percent}% of traffic"))

    # Decide on evidence rather than on elapsed time. "It has been up for ten
    # minutes" is not the same claim as "it is serving correctly".
    if error_rate > error_budget:
        current.events.append(
            Event(
                Stage.ROLLED_BACK,
                f"error rate {error_rate:.1%} exceeds budget {error_budget:.1%}",
            )
        )
        current.traffic_to_new = 0
        return current

    current.previous_version = current.live_version
    current.live_version = build.version
    current.traffic_to_new = 100
    current.events.append(Event(Stage.PROMOTED, f"{build.version} at 100%"))
    return current


def rollback(current: Deployment) -> Deployment:
    """Return to the previous version without rebuilding anything.

    Rollback has to be a data operation -- swap which artefact is live -- not a
    build. A rollback that requires a rebuild takes as long as the deployment
    did, during which the incident continues.
    """
    if current.previous_version is None:
        current.events.append(Event(Stage.ROLLED_BACK, "no previous version to return to"))
        return current

    current.live_version, current.previous_version = (
        current.previous_version,
        current.live_version,
    )
    current.traffic_to_new = 0
    current.events.append(Event(Stage.ROLLED_BACK, f"back to {current.live_version}"))
    return current
