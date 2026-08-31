"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.

Work out how big an AI image will be, and what is making it big.

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
COMPONENT_MB = {'python-slim': 45, 'python-full': 340, 'build-essential': 280, 'cuda-runtime': 1600, 'cuda-devel': 4100, 'torch': 2400, 'transformers': 480, 'fastapi': 25, 'app-code': 3, 'model-weights-7b': 13500, 'model-weights-small': 420}

class Purpose(str, Enum):
    """Why a component is present, which decides whether it may be dropped."""
    BUILD = 'build'
    RUNTIME = 'runtime'
    DATA = 'data'

@dataclass(frozen=True)
class Component:
    name: str
    purpose: Purpose

    @property
    def size_mb(self) -> int:
        raise NotImplementedError('TASK 1: implement size_mb.')

@dataclass
class Stage:
    name: str
    base: str
    components: list[Component] = field(default_factory=list)

    @property
    def size_mb(self) -> int:
        raise NotImplementedError('TASK 2: implement size_mb.')

@dataclass
class ImagePlan:
    """A build described as stages plus what the final stage carries forward."""
    stages: list[Stage]
    final_stage: str
    carried: list[Component] = field(default_factory=list)

    @property
    def final(self) -> Stage:
        raise NotImplementedError('TASK 3: implement final.')

    @property
    def size_mb(self) -> int:
        """Only the final stage ships. Earlier stages are discarded."""
        raise NotImplementedError('TASK 4: implement size_mb. Only the final stage ships. Earlier stages are discarded.')

    @property
    def build_only_shipped(self) -> list[Component]:
        """Build tooling that reached the final image. Pure waste."""
        raise NotImplementedError('TASK 5: implement build_only_shipped. Build tooling that reached the final image. Pure waste.')

    @property
    def weights_shipped(self) -> list[Component]:
        raise NotImplementedError('TASK 6: implement weights_shipped.')

def pull_seconds(size_mb: int, mbps: float=200.0) -> float:
    """How long one node waits to pull this image, at a given link speed."""
    raise NotImplementedError('TASK 7: implement pull_seconds. How long one node waits to pull this image, at a given link speed.')

def rollout_seconds(size_mb: int, nodes: int, mbps: float=200.0) -> float:
    """A rollout pulls onto every node. This is where image size is felt."""
    raise NotImplementedError('TASK 8: implement rollout_seconds. A rollout pulls onto every node. This is where image size is felt.')

@dataclass(frozen=True)
class Finding:
    rule: str
    message: str
    saves_mb: int = 0

def review(plan: ImagePlan) -> list[Finding]:
    """What is making this image big, and what removing it would save."""
    raise NotImplementedError('TASK 9: implement review. What is making this image big, and what removing it would save.')

def compare(before: ImagePlan, after: ImagePlan, *, nodes: int=20) -> dict[str, float]:
    """What the change bought, in the units that are actually felt."""
    raise NotImplementedError('TASK 10: implement compare. What the change bought, in the units that are actually felt.')
