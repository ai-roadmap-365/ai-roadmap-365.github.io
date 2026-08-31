"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.

Model Docker's build cache so you can see what an edit actually costs.

Offline and standard-library only. Nothing is built and Docker does not need
to be installed -- the point is the RULE the cache follows, which you can
reason about without waiting three minutes to find out you were wrong.

The rule is short and almost everyone gets it wrong at least once:

  a layer is reused only if every layer before it was reused, AND
  its own inputs are unchanged

The consequence is the whole lesson. `COPY . .` early in a Dockerfile makes
every later layer depend on every file in your project, so editing one line of
Python re-runs `pip install`. Copying the dependency manifest first, installing,
and only then copying source costs nothing extra on a cold build and saves the
install on every warm one.

Nothing here judges whether an image is good. It computes which layers survive
an edit, which is the part that decides how long you wait.
"""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field
COST_SECONDS = {'FROM': 0.0, 'WORKDIR': 0.0, 'ENV': 0.0, 'ARG': 0.0, 'EXPOSE': 0.0, 'USER': 0.0, 'LABEL': 0.0, 'ENTRYPOINT': 0.0, 'CMD': 0.0, 'HEALTHCHECK': 0.0, 'COPY': 1.0, 'ADD': 1.0, 'RUN': 8.0}
INSTALL_RE = re.compile('\\b(pip\\s+install|apt-get\\s+install|apk\\s+add|npm\\s+(ci|install)|poetry\\s+install|uv\\s+pip\\s+install)\\b', re.I)
INSTALL_SECONDS = 75.0

@dataclass(frozen=True)
class Instruction:
    line_no: int
    verb: str
    args: str

    @property
    def text(self) -> str:
        raise NotImplementedError('TASK 1: implement text.')

    @property
    def cost_seconds(self) -> float:
        """What this layer costs when it actually has to run."""
        raise NotImplementedError('TASK 2: implement cost_seconds. What this layer costs when it actually has to run.')

    @property
    def copied_paths(self) -> list[str]:
        """Sources a COPY or ADD reads. The last token is the destination."""
        raise NotImplementedError('TASK 3: implement copied_paths. Sources a COPY or ADD reads. The last token is the destination.')

def parse(dockerfile: str) -> list[Instruction]:
    """Parse a Dockerfile, joining backslash continuations.

    Comments and blank lines produce no layer, so they are dropped rather than
    numbered -- but the line numbers kept are the real ones, because that is
    what you need when the linter tells you where to look.
    """
    raise NotImplementedError('TASK 4: implement parse. Parse a Dockerfile, joining backslash continuations.')

def _matches(pattern: str, path: str) -> bool:
    """Whether a COPY source covers a project file.

    Deliberately simple: `.` and `./` cover everything, a directory prefix
    covers what is under it, and anything else must match exactly. Docker's
    real matching is richer; this is the part that decides cache behaviour.
    """
    raise NotImplementedError('TASK 5: implement _matches. Whether a COPY source covers a project file.')

@dataclass
class Layer:
    instruction: Instruction
    reused: bool
    reason: str
    cost_seconds: float

@dataclass
class BuildPlan:
    layers: list[Layer] = field(default_factory=list)

    @property
    def rebuilt(self) -> list[Layer]:
        raise NotImplementedError('TASK 6: implement rebuilt.')

    @property
    def seconds(self) -> float:
        raise NotImplementedError('TASK 7: implement seconds.')

    @property
    def first_miss(self) -> Layer | None:
        raise NotImplementedError('TASK 8: implement first_miss.')

    def summary(self) -> str:
        raise NotImplementedError('TASK 9: implement summary.')

def plan_build(instructions: list[Instruction], changed_files: set[str] | None=None, *, cold: bool=False) -> BuildPlan:
    """Which layers survive, given the files that changed since the last build.

    Once a layer misses, everything after it misses too -- that is the whole
    rule, and it is why the ORDER of instructions matters more than their
    content.
    """
    raise NotImplementedError('TASK 10: implement plan_build. Which layers survive, given the files that changed since the last build.')

def digest(dockerfile: str) -> str:
    """A stable identifier for a Dockerfile's instruction sequence."""
    raise NotImplementedError("TASK 11: implement digest. A stable identifier for a Dockerfile's instruction sequence.")

@dataclass(frozen=True)
class Finding:
    line_no: int
    rule: str
    message: str

def lint(instructions: list[Instruction]) -> list[Finding]:
    """The mistakes that cost real time or ship a real risk."""
    raise NotImplementedError('TASK 12: implement lint. The mistakes that cost real time or ship a real risk.')
