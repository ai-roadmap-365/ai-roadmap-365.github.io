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
    # TASK 1: return EVERY reason not to deploy, not just the first.
    #   tests_passed False           -> "tests did not pass"
    #   migrations_reversible False  -> "migration is not reversible"
    #   secrets_present False        -> "required secrets are missing"
    #   image_digest not sha256:...  -> "image is not pinned to a digest"
    # A build with three problems should tell you three things once, rather
    # than sending you round the loop three times.
    raise NotImplementedError("implement preflight")

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
    # TASK 2: run the release path, stopping at the first gate that says no.
    #   - preflight blockers -> append a BLOCKED event and raise DeployBlocked,
    #     WITHOUT changing live_version or traffic_to_new. Nothing deployed.
    #   - append DEPLOYING, then check health BEFORE routing any traffic. If it
    #     is not serving, append ROLLED_BACK naming every failing signal.
    #   - set traffic_to_new to canary_percent and append CANARY.
    #   - if error_rate > error_budget, append ROLLED_BACK and return traffic to
    #     zero. Decide on the rate, never on elapsed time.
    #   - otherwise record the outgoing version as previous_version, promote,
    #     and set traffic to 100.
    raise NotImplementedError("implement deploy")

def rollback(current: Deployment) -> Deployment:
    """Return to the previous version without rebuilding anything.

    Rollback has to be a data operation -- swap which artefact is live -- not a
    build. A rollback that requires a rebuild takes as long as the deployment
    did, during which the incident continues.
    """
    # TASK 3: return to the previous version without rebuilding.
    # SWAP live_version and previous_version rather than discarding, so the
    # rollback is itself reversible -- which matters on the day the rollback
    # was the mistake. With no previous version, append a ROLLED_BACK event
    # saying so rather than crashing.
    raise NotImplementedError("implement rollback")
