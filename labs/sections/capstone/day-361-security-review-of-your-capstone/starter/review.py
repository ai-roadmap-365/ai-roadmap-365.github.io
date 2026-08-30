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
    # TASK 1: HIGH when marks_untrusted_content is False, with a remediation
    # saying to delimit untrusted content and treat it as data to summarise
    # rather than instructions to obey. Otherwise OK.
    raise NotImplementedError("implement check_untrusted_content_boundary")

def check_output_handling(p: Posture) -> Finding:
    # TASK 2: HIGH if executes_model_output, else HIGH if not escapes_output,
    # else OK. Executing is the worse of the two, so check it first.
    raise NotImplementedError("implement check_output_handling")

def check_tool_permissions(p: Posture) -> Finding:
    # TASK 3: find scopes starting with any DESTRUCTIVE_SCOPES prefix.
    #   any not in tools_require_confirmation -> HIGH, naming them
    #   all confirmed                          -> LOW
    #   none present                           -> OK
    # Use a PREFIX test, not a substring one, or "read:docs" matches.
    raise NotImplementedError("implement check_tool_permissions")

def check_spend_bounds(p: Posture) -> Finding:
    # TASK 4: both caps missing -> HIGH, one missing -> MEDIUM, none -> OK.
    # Severity accumulates because the consequence does.
    raise NotImplementedError("implement check_spend_bounds")

def check_secret_handling(p: Posture) -> Finding:
    # TASK 5: in the repository -> HIGH, and the remediation must say ROTATE
    # first: deleting the file does not remove it from history. In the image ->
    # HIGH. No declared source -> MEDIUM. Otherwise OK.
    raise NotImplementedError("implement check_secret_handling")

def check_data_retention(p: Posture) -> Finding:
    # TASK 6: collect the problems -- no retention period, not in the erasure
    # path, not redacted before storage. More than one -> HIGH, exactly one ->
    # MEDIUM, none -> OK.
    raise NotImplementedError("implement check_data_retention")

def check_dependency_pinning(p: Posture) -> Finding:
    # TASK 7: an unpinned image or unlocked dependencies -> MEDIUM, naming
    # both when both apply. Otherwise OK.
    raise NotImplementedError("implement check_dependency_pinning")

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
