"""Work out how big an AI image will be, and what is making it big.

Offline and standard-library only. Docker is not required: the input is a
described build -- stages, what each installs, and what the final stage keeps
-- so the arithmetic can be checked without pulling six gigabytes to find out.

Packaging an AI application is not packaging a web app with a bigger
requirements file. Three things dominate, and only one of them is obvious:

  build tooling   compilers and headers needed to BUILD wheels, never to run
  the framework   torch and CUDA runtime are gigabytes before your code exists
  model weights   frequently larger than everything else combined

The first is solved by a multi-stage build. The third is usually solved by NOT
solving it -- weights baked into an image are pulled onto every node on every
rollout, and a volume or object store is almost always the right answer.

Nothing here judges whether an image works. It computes what it costs to pull,
which is the number that decides how long a deploy takes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# Nominal compressed sizes in megabytes. The absolute values are illustrative;
# the ORDER OF MAGNITUDE between them is the part that drives every decision.
COMPONENT_MB = {
    "python-slim": 45,
    "python-full": 340,
    "build-essential": 280,     # gcc, make, headers -- build only
    "cuda-runtime": 1_600,
    "cuda-devel": 4_100,        # build only
    "torch": 2_400,
    "transformers": 480,
    "fastapi": 25,
    "app-code": 3,
    "model-weights-7b": 13_500,
    "model-weights-small": 420,
}


class Purpose(str, Enum):
    """Why a component is present, which decides whether it may be dropped."""

    BUILD = "build"      # needed to produce artefacts, never at run time
    RUNTIME = "runtime"  # needed by the running process
    DATA = "data"        # weights and assets -- runtime, but relocatable


@dataclass(frozen=True)
class Component:
    name: str
    purpose: Purpose

    @property
    def size_mb(self) -> int:
        return COMPONENT_MB.get(self.name, 0)


@dataclass
class Stage:
    name: str
    base: str
    components: list[Component] = field(default_factory=list)

    @property
    def size_mb(self) -> int:
        return COMPONENT_MB.get(self.base, 0) + sum(c.size_mb for c in self.components)


@dataclass
class ImagePlan:
    """A build described as stages plus what the final stage carries forward."""

    stages: list[Stage]
    final_stage: str
    carried: list[Component] = field(default_factory=list)

    @property
    def final(self) -> Stage:
        for s in self.stages:
            if s.name == self.final_stage:
                return s
        raise KeyError(f"no stage named {self.final_stage!r}")

    @property
    def size_mb(self) -> int:
        """Only the final stage ships. Earlier stages are discarded."""
        return self.final.size_mb + sum(c.size_mb for c in self.carried)

    @property
    def build_only_shipped(self) -> list[Component]:
        """Build tooling that reached the final image. Pure waste."""
        present = self.final.components + self.carried
        return [c for c in present if c.purpose is Purpose.BUILD]

    @property
    def weights_shipped(self) -> list[Component]:
        present = self.final.components + self.carried
        return [c for c in present if c.purpose is Purpose.DATA]


def pull_seconds(size_mb: int, mbps: float = 200.0) -> float:
    """How long one node waits to pull this image, at a given link speed."""
    if mbps <= 0:
        return 0.0
    return round(size_mb * 8 / mbps, 1)


def rollout_seconds(size_mb: int, nodes: int, mbps: float = 200.0) -> float:
    """A rollout pulls onto every node. This is where image size is felt."""
    return round(pull_seconds(size_mb, mbps) * max(0, nodes), 1)


@dataclass(frozen=True)
class Finding:
    rule: str
    message: str
    saves_mb: int = 0


def review(plan: ImagePlan) -> list[Finding]:
    """What is making this image big, and what removing it would save."""
    out: list[Finding] = []

    build = plan.build_only_shipped
    if build:
        waste = sum(c.size_mb for c in build)
        names = ", ".join(c.name for c in build)
        out.append(
            Finding(
                "build-tooling-shipped",
                f"build-only components in the final image ({names}); "
                "produce them in an earlier stage and copy the artefacts out",
                waste,
            )
        )

    weights = plan.weights_shipped
    if weights:
        waste = sum(c.size_mb for c in weights)
        out.append(
            Finding(
                "weights-baked-in",
                f"model weights are in the image ({sum(c.size_mb for c in weights)} MB); "
                "every node pulls them on every rollout even when only your code changed",
                waste,
            )
        )

    if plan.final.base == "python-full":
        out.append(
            Finding(
                "fat-base",
                "the final stage uses the full Python base; the slim base carries the same "
                "interpreter without the build toolchain",
                COMPONENT_MB["python-full"] - COMPONENT_MB["python-slim"],
            )
        )
    return out


def compare(before: ImagePlan, after: ImagePlan, *, nodes: int = 20) -> dict[str, float]:
    """What the change bought, in the units that are actually felt."""
    b, a = before.size_mb, after.size_mb
    return {
        "before_mb": b,
        "after_mb": a,
        "saved_mb": b - a,
        "ratio": round(b / a, 2) if a else 0.0,
        "before_rollout_s": rollout_seconds(b, nodes),
        "after_rollout_s": rollout_seconds(a, nodes),
    }
