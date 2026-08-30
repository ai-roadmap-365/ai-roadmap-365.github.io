"""A security posture review for an AI application.

Offline and standard-library only. Everything here is DEFENSIVE: the checks
describe a system's configuration and report weaknesses so they can be fixed.
There is no exploit code, and nothing here attacks anything.

The checks follow the shape of the OWASP Top 10 for LLM Applications, reduced
to the seven that a capstone can actually get wrong:

  untrusted_content_boundary   retrieved text treated as instructions
  output_handling              model output rendered or executed unescaped
  tool_permissions             an agent that can do more than the task needs
  spend_bounds                 no cap, so cost is an availability risk
  secret_handling              credentials in the image or the repository
  data_retention               traces kept forever, undeleted
  dependency_pinning           mutable references in the supply chain

Two ideas run through it.

  * Severity is about BLAST RADIUS, not about how clever the flaw is. A missing
    spend cap is dull and can take the service down.
  * A review that finds nothing is not evidence of safety unless you know it
    can find something -- which is why a deliberately weak configuration ships
    alongside a sound one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    OK = "ok"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


ORDER = {Severity.OK: 0, Severity.LOW: 1, Severity.MEDIUM: 2, Severity.HIGH: 3}


@dataclass(frozen=True)
class Posture:
    """How an application is configured. The subject of the review.

    Deliberately a flat description rather than live introspection: a review
    should be runnable against a design document before any code exists.
    """

    # Is retrieved/user content kept separate from instructions?
    marks_untrusted_content: bool = True
    # Is model output escaped before rendering, and never executed?
    escapes_output: bool = True
    executes_model_output: bool = False
    # What may the agent's tools do?
    tool_scopes: tuple[str, ...] = ("read:docs",)
    tools_require_confirmation: tuple[str, ...] = ()
    # Cost bounds
    per_request_cap: float | None = 0.05
    per_user_daily_cap: float | None = 1.0
    # Secrets
    secrets_in_environment: bool = True
    secrets_in_image: bool = False
    secrets_in_repository: bool = False
    # Data handling
    trace_retention_days: int | None = 30
    traces_in_erasure_path: bool = True
    redacts_before_storage: bool = True
    # Supply chain
    image_pinned_by_digest: bool = True
    dependencies_locked: bool = True


# Tool scopes that can change or destroy state, and so should not be granted
# without an explicit confirmation step.
DESTRUCTIVE_SCOPES = ("write:", "delete:", "admin:", "exec:", "payments:")


@dataclass
class Finding:
    check: str
    severity: Severity
    detail: str
    remediation: str = ""

    def line(self) -> str:
        base = f"  {self.severity.value.upper():<7} {self.check}: {self.detail}"
        return f"{base}\n          fix: {self.remediation}" if self.remediation else base


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    @property
    def worst(self) -> Severity:
        return max((f.severity for f in self.findings), key=lambda s: ORDER[s], default=Severity.OK)

    def at_least(self, severity: Severity) -> list[Finding]:
        return [f for f in self.findings if ORDER[f.severity] >= ORDER[severity]]

    def names(self) -> set[str]:
        return {f.check for f in self.findings if f.severity is not Severity.OK}

    def summary(self) -> str:
        counts = {s: 0 for s in Severity}
        for f in self.findings:
            counts[f.severity] += 1
        verdict = "PASS" if self.worst in (Severity.OK, Severity.LOW) else "FAIL"
        return (
            f"{verdict} high={counts[Severity.HIGH]} medium={counts[Severity.MEDIUM]} "
            f"low={counts[Severity.LOW]}"
        )


# ------------------------------------------------------------------ checks


def check_untrusted_content_boundary(p: Posture) -> Finding:
    if p.marks_untrusted_content:
        return Finding("untrusted_content_boundary", Severity.OK, "retrieved content is marked untrusted")
    return Finding(
        "untrusted_content_boundary",
        Severity.HIGH,
        "retrieved and user content is concatenated into the prompt without a boundary",
        "keep instructions and untrusted content in separate, clearly delimited sections, "
        "and treat retrieved text as data the model may summarise but must not obey",
    )


def check_output_handling(p: Posture) -> Finding:
    if p.executes_model_output:
        return Finding(
            "output_handling",
            Severity.HIGH,
            "model output is executed",
            "never execute generated code or queries directly; run them in a sandbox with no "
            "credentials, or require a human to approve",
        )
    if not p.escapes_output:
        return Finding(
            "output_handling",
            Severity.HIGH,
            "model output is rendered without escaping",
            "escape on every append; a tag split across two streamed tokens is not a tag in "
            "either half, so a whole-document sanitiser will miss it",
        )
    return Finding("output_handling", Severity.OK, "output is escaped and never executed")


def check_tool_permissions(p: Posture) -> Finding:
    risky = [s for s in p.tool_scopes if s.startswith(DESTRUCTIVE_SCOPES)]
    unguarded = [s for s in risky if s not in p.tools_require_confirmation]
    if unguarded:
        return Finding(
            "tool_permissions",
            Severity.HIGH,
            f"state-changing scopes granted without confirmation: {', '.join(unguarded)}",
            "grant the narrowest scope the task needs, and require explicit confirmation for "
            "anything that writes, deletes or spends",
        )
    if risky:
        return Finding(
            "tool_permissions",
            Severity.LOW,
            f"state-changing scopes present but confirmed: {', '.join(risky)}",
        )
    return Finding("tool_permissions", Severity.OK, "read-only scopes only")


def check_spend_bounds(p: Posture) -> Finding:
    missing = [
        name
        for name, value in (("per-request", p.per_request_cap), ("per-user daily", p.per_user_daily_cap))
        if value is None
    ]
    if missing:
        return Finding(
            "spend_bounds",
            Severity.HIGH if len(missing) == 2 else Severity.MEDIUM,
            f"no {' and no '.join(missing)} cap",
            "cap before the call, not after; anything a user can trigger an attacker can "
            "trigger repeatedly, and unbounded spend is an availability risk",
        )
    return Finding("spend_bounds", Severity.OK, "per-request and per-user caps present")


def check_secret_handling(p: Posture) -> Finding:
    if p.secrets_in_repository:
        return Finding(
            "secret_handling",
            Severity.HIGH,
            "credentials are committed to the repository",
            "rotate them first -- history is not erased by deleting the file -- then move them "
            "to the environment",
        )
    if p.secrets_in_image:
        return Finding(
            "secret_handling",
            Severity.HIGH,
            "credentials are baked into the container image",
            "an image is a distributable artefact and a later RUN rm does not remove a layer; "
            "supply secrets through the environment at run time",
        )
    if not p.secrets_in_environment:
        return Finding("secret_handling", Severity.MEDIUM, "no declared source of credentials")
    return Finding("secret_handling", Severity.OK, "credentials come from the environment")


def check_data_retention(p: Posture) -> Finding:
    problems: list[str] = []
    if p.trace_retention_days is None:
        problems.append("traces are retained indefinitely")
    if not p.traces_in_erasure_path:
        problems.append("traces are not covered by deletion")
    if not p.redacts_before_storage:
        problems.append("content is stored before redaction")
    if problems:
        return Finding(
            "data_retention",
            Severity.HIGH if len(problems) > 1 else Severity.MEDIUM,
            "; ".join(problems),
            "traces hold full prompts and completions -- give them a retention period, include "
            "them in the erasure path, and redact before writing",
        )
    return Finding("data_retention", Severity.OK, "traces are bounded, deletable and redacted")


def check_dependency_pinning(p: Posture) -> Finding:
    problems: list[str] = []
    if not p.image_pinned_by_digest:
        problems.append("image referenced by mutable tag")
    if not p.dependencies_locked:
        problems.append("dependencies unlocked")
    if problems:
        return Finding(
            "dependency_pinning",
            Severity.MEDIUM,
            "; ".join(problems),
            "pin the image by digest and commit a lockfile, so what you deploy is provably what "
            "you tested",
        )
    return Finding("dependency_pinning", Severity.OK, "image and dependencies are pinned")


CHECKS = (
    check_untrusted_content_boundary,
    check_output_handling,
    check_tool_permissions,
    check_spend_bounds,
    check_secret_handling,
    check_data_retention,
    check_dependency_pinning,
)


def review(posture: Posture) -> Report:
    """Run every check against one posture."""
    return Report(findings=[check(posture) for check in CHECKS])


# ------------------------------------------------- two postures to review


SOUND = Posture()

WEAK = Posture(
    marks_untrusted_content=False,
    escapes_output=False,
    tool_scopes=("read:docs", "write:tickets", "delete:records"),
    tools_require_confirmation=(),
    per_request_cap=None,
    per_user_daily_cap=None,
    secrets_in_environment=False,
    secrets_in_image=True,
    trace_retention_days=None,
    traces_in_erasure_path=False,
    redacts_before_storage=False,
    image_pinned_by_digest=False,
    dependencies_locked=False,
)
