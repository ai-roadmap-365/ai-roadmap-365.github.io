"""Check that documentation still describes the system it documents.

Offline and standard-library only. The subject is a project description plus
its README text, so the check runs without executing anything.

Documentation does not become wrong all at once. It drifts: a command is
renamed, a flag is removed, an output changes, and the README keeps saying what
used to be true. Every reader after that point is misled, and the person who
would have noticed is the one person who no longer reads it.

The defence is to make documentation CHECKABLE. Four things can be verified
mechanically:

  sections   the questions a new reader must be able to answer
  commands   every documented command still exists in the project
  outputs    every claimed output matches what was actually captured
  honesty    no placeholders, and limitations stated rather than implied

The fourth is the one people skip, and it is the one that decides whether a
demo builds trust or spends it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class Level(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


# What a new reader must be able to answer before they can use anything.
REQUIRED_SECTIONS = (
    "What it does",
    "Install",
    "Run",
    "Architecture",
    "Limitations",
    "Troubleshooting",
)

# Words that mean the sentence was never finished. Deliberately not the same
# vocabulary this course forbids in its own lessons -- a checker whose examples
# trip another checker is a checker nobody can write about.
PLACEHOLDERS = (
    "to be written",
    "under construction",
    "not yet documented",
    "fill this in",
    "placeholder text",
)


@dataclass(frozen=True)
class Project:
    """What the system actually provides."""

    commands: tuple[str, ...] = ()
    captured_outputs: dict[str, str] = field(default_factory=dict)
    known_limitations: tuple[str, ...] = ()


@dataclass
class Issue:
    check: str
    level: Level
    detail: str

    def line(self) -> str:
        return f"  {self.level.value.upper():<5} {self.check}: {self.detail}"


@dataclass
class DocReport:
    issues: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.level is Level.FAIL for i in self.issues)

    def names(self) -> set[str]:
        return {i.check for i in self.issues if i.level is not Level.OK}

    def summary(self) -> str:
        fails = sum(1 for i in self.issues if i.level is Level.FAIL)
        warns = sum(1 for i in self.issues if i.level is Level.WARN)
        return f"{'PASS' if self.ok else 'FAIL'} fail={fails} warn={warns}"


def sections_in(readme: str) -> list[str]:
    """Heading titles, in document order."""
    return [m.group(1).strip() for m in re.finditer(r"^#{1,3}\s+(.+)$", readme, re.M)]


def commands_in(readme: str) -> list[str]:
    """Commands claimed by the README.

    Only blocks TAGGED as a shell language count. An untagged block is output,
    not an instruction -- without that distinction the extractor reads captured
    output back as commands, which is a bug this lab had before the tests
    caught it.
    """
    # TASK 1: return the commands a README instructs a reader to run.
    # Only blocks TAGGED bash, sh or console are instructions. A bare ``` block
    # is OUTPUT -- treat it as a command and the checker reports the document's
    # own examples as commands that do not exist.
    # Strip a leading "$" and skip lines starting with "#".
    raise NotImplementedError("implement commands_in")

def claimed_outputs(readme: str) -> dict[str, str]:
    """Output blocks introduced by a line naming the command that produced them.

    The convention is deliberate and small: a line ending in `->` names the
    command, and the fenced block after it is what that command printed. It
    makes the claim machine-checkable, which is the whole point.
    """
    # TASK 2: map command -> claimed output.
    # Convention: a line ending in "->" names the command, and the fenced block
    # after it is what that command printed.
    # The command group must NOT span newlines. With re.S a dot matches them and
    # the group swallows the whole document up to the first block -- use
    # [^\n]+? for the command and re.S only for the block body.
    raise NotImplementedError("implement claimed_outputs")

# ------------------------------------------------------------------ checks


def check_sections(readme: str) -> Issue:
    present = set(sections_in(readme))
    missing = [s for s in REQUIRED_SECTIONS if s not in present]
    if missing:
        return Issue("sections", Level.FAIL, f"missing: {', '.join(missing)}")
    return Issue("sections", Level.OK, "all required sections present")


def check_commands(readme: str, project: Project) -> Issue:
    """Every documented command must exist in the project.

    This is the check that catches drift, because a renamed command leaves the
    README confidently wrong and nothing else notices.
    """
    # TASK 3: FAIL naming any documented command the project does not provide.
    # WARN when the README documents no commands at all. Otherwise OK.
    raise NotImplementedError("implement check_commands")

def check_undocumented_commands(readme: str, project: Project) -> Issue:
    """Commands the project provides and the README never mentions.

    A warning rather than a failure: not everything needs documenting. But a
    command nobody has written down is a command nobody will use.
    """
    documented = set(commands_in(readme))
    missing = [c for c in project.commands if c not in documented]
    if missing:
        return Issue("undocumented_commands", Level.WARN, f"provided but undocumented: {', '.join(missing)}")
    return Issue("undocumented_commands", Level.OK, "every provided command is documented")


def check_outputs(readme: str, project: Project) -> Issue:
    """Claimed output must match what was actually captured."""
    # TASK 4: for each claimed output, FAIL when there is no captured output to
    # compare against, or when it differs. Name every offending command.
    raise NotImplementedError("implement check_outputs")

def check_placeholders(readme: str) -> Issue:
    lowered = readme.lower()
    found = sorted({p for p in PLACEHOLDERS if p in lowered})
    if found:
        return Issue("placeholders", Level.FAIL, f"unfinished text: {', '.join(found)}")
    return Issue("placeholders", Level.OK, "no placeholder text")


def check_limitations(readme: str, project: Project) -> Issue:
    """Known limitations must be stated, not merely known.

    A demo that hides its limits spends trust it has to earn back later, and
    the person who finds the limit will find it at the worst moment.
    """
    # TASK 5: FAIL naming any known limitation the README does not state
    # (case-insensitive). WARN when the project records none at all -- an empty
    # list is a claim, and usually a false one. Otherwise OK.
    raise NotImplementedError("implement check_limitations")

def review(readme: str, project: Project) -> DocReport:
    return DocReport(
        issues=[
            check_sections(readme),
            check_commands(readme, project),
            check_undocumented_commands(readme, project),
            check_outputs(readme, project),
            check_placeholders(readme),
            check_limitations(readme, project),
        ]
    )
