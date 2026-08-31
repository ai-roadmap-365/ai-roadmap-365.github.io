"""Model Docker's build cache so you can see what an edit actually costs.

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

# Rough wall-clock seconds each kind of instruction costs when it has to run.
# The absolute numbers do not matter; the RATIO between installing dependencies
# and copying a file is what makes cache ordering worth caring about.
COST_SECONDS = {
    "FROM": 0.0,
    "WORKDIR": 0.0,
    "ENV": 0.0,
    "ARG": 0.0,
    "EXPOSE": 0.0,
    "USER": 0.0,
    "LABEL": 0.0,
    "ENTRYPOINT": 0.0,
    "CMD": 0.0,
    "HEALTHCHECK": 0.0,
    "COPY": 1.0,
    "ADD": 1.0,
    "RUN": 8.0,
}

# A RUN that installs dependencies is the expensive one, and it is the layer
# people accidentally invalidate.
INSTALL_RE = re.compile(
    r"\b(pip\s+install|apt-get\s+install|apk\s+add|npm\s+(ci|install)|poetry\s+install|uv\s+pip\s+install)\b",
    re.I,
)
INSTALL_SECONDS = 75.0


@dataclass(frozen=True)
class Instruction:
    line_no: int
    verb: str
    args: str

    @property
    def text(self) -> str:
        return f"{self.verb} {self.args}".strip()

    @property
    def cost_seconds(self) -> float:
        """What this layer costs when it actually has to run."""
        if self.verb == "RUN" and INSTALL_RE.search(self.args):
            return INSTALL_SECONDS
        return COST_SECONDS.get(self.verb, 1.0)

    @property
    def copied_paths(self) -> list[str]:
        """Sources a COPY or ADD reads. The last token is the destination."""
        if self.verb not in ("COPY", "ADD"):
            return []
        parts = [p for p in self.args.split() if not p.startswith("--")]
        return parts[:-1] if len(parts) >= 2 else []


def parse(dockerfile: str) -> list[Instruction]:
    """Parse a Dockerfile, joining backslash continuations.

    Comments and blank lines produce no layer, so they are dropped rather than
    numbered -- but the line numbers kept are the real ones, because that is
    what you need when the linter tells you where to look.
    """
    out: list[Instruction] = []
    pending = ""
    start = 0
    for i, raw in enumerate(dockerfile.split("\n"), start=1):
        line = raw.strip()
        if not pending and (not line or line.startswith("#")):
            continue
        if not pending:
            start = i
        if line.endswith("\\"):
            pending += line[:-1].strip() + " "
            continue
        full = (pending + line).strip()
        pending = ""
        if not full:
            continue
        verb, _, args = full.partition(" ")
        out.append(Instruction(line_no=start, verb=verb.upper(), args=args.strip()))
    return out


def _matches(pattern: str, path: str) -> bool:
    """Whether a COPY source covers a project file.

    Deliberately simple: `.` and `./` cover everything, a directory prefix
    covers what is under it, and anything else must match exactly. Docker's
    real matching is richer; this is the part that decides cache behaviour.
    """
    if pattern in (".", "./"):
        return True
    p = pattern.rstrip("/")
    return path == p or path.startswith(p + "/")


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
        return [x for x in self.layers if not x.reused]

    @property
    def seconds(self) -> float:
        return round(sum(x.cost_seconds for x in self.rebuilt), 1)

    @property
    def first_miss(self) -> Layer | None:
        return self.rebuilt[0] if self.rebuilt else None

    def summary(self) -> str:
        hit = len(self.layers) - len(self.rebuilt)
        return f"{hit}/{len(self.layers)} layers cached  rebuild {self.seconds:.1f}s"


def plan_build(
    instructions: list[Instruction],
    changed_files: set[str] | None = None,
    *,
    cold: bool = False,
) -> BuildPlan:
    """Which layers survive, given the files that changed since the last build.

    Once a layer misses, everything after it misses too -- that is the whole
    rule, and it is why the ORDER of instructions matters more than their
    content.
    """
    changed = changed_files or set()
    plan = BuildPlan()
    invalidated = False
    for ins in instructions:
        if cold:
            reason = "no cache (cold build)"
            reused = False
        elif invalidated:
            reason = "a previous layer changed"
            reused = False
        else:
            touched = [f for f in sorted(changed) if any(_matches(p, f) for p in ins.copied_paths)]
            if touched:
                reason = f"reads changed file(s): {', '.join(touched[:3])}"
                reused = False
                invalidated = True
            else:
                reason = "unchanged"
                reused = True
        plan.layers.append(
            Layer(
                instruction=ins,
                reused=reused,
                reason=reason,
                cost_seconds=0.0 if reused else ins.cost_seconds,
            )
        )
    return plan


def digest(dockerfile: str) -> str:
    """A stable identifier for a Dockerfile's instruction sequence."""
    text = "\n".join(i.text for i in parse(dockerfile))
    return hashlib.sha256(text.encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Finding:
    line_no: int
    rule: str
    message: str


def lint(instructions: list[Instruction]) -> list[Finding]:
    """The mistakes that cost real time or ship a real risk."""
    out: list[Finding] = []
    install_idx = next(
        (i for i, x in enumerate(instructions) if x.verb == "RUN" and INSTALL_RE.search(x.args)),
        None,
    )
    broad_copy_idx = next(
        (i for i, x in enumerate(instructions) if x.copied_paths and any(p in (".", "./") for p in x.copied_paths)),
        None,
    )
    if install_idx is not None and broad_copy_idx is not None and broad_copy_idx < install_idx:
        out.append(
            Finding(
                instructions[broad_copy_idx].line_no,
                "copy-before-install",
                "COPY . . before the install layer: every source edit re-runs the install. "
                "Copy the dependency manifest first, install, then copy the source.",
            )
        )

    for ins in instructions:
        if ins.verb == "FROM":
            ref = ins.args.split(" AS ")[0].strip()
            if ":" not in ref.rsplit("/", 1)[-1] or ref.endswith(":latest"):
                out.append(
                    Finding(ins.line_no, "unpinned-base",
                            f"base image '{ref}' is unpinned; a rebuild months later gets a different image")
                )
        if ins.verb == "RUN" and re.search(r"\bapt-get\s+install\b", ins.args, re.I):
            if "rm -rf /var/lib/apt/lists" not in ins.args:
                out.append(
                    Finding(ins.line_no, "apt-cache-kept",
                            "apt-get install without removing /var/lib/apt/lists in the SAME layer "
                            "leaves the package index in the image")
                )
        if ins.verb == "RUN" and re.search(r"\bpip\s+install\b", ins.args, re.I):
            if "--no-cache-dir" not in ins.args:
                out.append(
                    Finding(ins.line_no, "pip-cache-kept",
                            "pip install without --no-cache-dir bakes the wheel cache into the layer")
                )

    if not any(x.verb == "USER" for x in instructions):
        out.append(Finding(0, "runs-as-root", "no USER instruction: the container runs as root"))
    return out
