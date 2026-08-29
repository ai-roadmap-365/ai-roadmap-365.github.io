"""The acceptance harness -- YOUR skeleton.

Read `00_brief.md` first, then fill these in one at a time. Check yourself as
you go:

    .venv/bin/pytest starter -q

Unattempted gates raise `NotImplementedError`, which the test suite reports as
SKIPPED, not failed. A skip means "not attempted yet"; a failure means
"attempted and wrong", and the message shows your answer next to the correct
one.

Everything above the exercises is GIVEN: the verdict types, the small file
readers, and the four parsers that turn the study's Markdown into data. The
parsing is plumbing. The nine exercises are the judgment.

The rules every gate follows, and the tests enforce:

  * return `_passed(name)` when the gate is satisfied;
  * return `_failed(name, findings)` otherwise, with at least one finding;
  * every finding NAMES something -- the file, the field, the step, the
    sentence. "Provenance incomplete" is not a finding. "SOURCE.json is
    missing: checksum_sha256" is.
  * collect every problem rather than returning on the first one. A verdict is
    a task list, not an exception.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# ===========================================================================
# GIVEN -- the verdict types
# ===========================================================================


@dataclass(frozen=True)
class GateResult:
    """One gate's outcome. A passing gate carries no findings; a failing gate
    carries at least one, and each finding names what is wrong and where."""

    name: str
    ok: bool
    findings: tuple[str, ...] = ()

    def __str__(self) -> str:  # pragma: no cover - convenience only
        mark = "PASS" if self.ok else "FAIL"
        if self.ok:
            return f"[{mark}] {self.name}"
        joined = "\n".join(f"        - {f}" for f in self.findings)
        return f"[{mark}] {self.name}\n{joined}"


@dataclass(frozen=True)
class StudyVerdict:
    """The whole harness's answer about one study directory."""

    path: str
    gates: tuple[GateResult, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return all(gate.ok for gate in self.gates)

    @property
    def failed_gates(self) -> tuple[str, ...]:
        return tuple(gate.name for gate in self.gates if not gate.ok)

    @property
    def findings(self) -> tuple[str, ...]:
        return tuple(f for gate in self.gates for f in gate.findings)

    def gate(self, name: str) -> GateResult:
        for gate in self.gates:
            if gate.name == name:
                return gate
        raise KeyError(f"no such gate: {name!r} (have {[g.name for g in self.gates]})")

    def summary(self) -> str:
        head = "ACCEPTED" if self.ok else "NOT ACCEPTED"
        lines = [f"{head}: {self.path}"]
        lines += [str(gate) for gate in self.gates]
        return "\n".join(lines)


def _passed(name: str) -> GateResult:
    return GateResult(name=name, ok=True, findings=())


def _failed(name: str, findings) -> GateResult:
    findings = tuple(findings)
    if not findings:  # a failing gate with nothing to say is a bug
        raise ValueError(f"gate {name!r} failed without a finding")
    return GateResult(name=name, ok=False, findings=findings)


# ===========================================================================
# GIVEN -- small readers
# ===========================================================================


def _read_text(study_dir: Path, name: str) -> str | None:
    path = Path(study_dir) / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _read_json(study_dir: Path, name: str):
    """Return (payload, error). Exactly one of the two is None."""
    raw = _read_text(study_dir, name)
    if raw is None:
        return None, f"{name} is missing"
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as exc:
        return None, f"{name} is not valid JSON: {exc}"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ===========================================================================
# GIVEN -- the file names, the patterns, and the four parsers
# ===========================================================================


QUESTION_FILE = "QUESTION.md"


SOURCE_FILE = "SOURCE.json"


REQUIRED_SOURCE_FIELDS = ("url", "retrieved", "checksum_sha256", "licence")


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


INGEST_FILE = "INGEST.json"


CLEANING_FILE = "CLEANING.md"


_STEP_RE = re.compile(r"^###\s+(?P<title>.+?)\s*$")


_MEASURE_RE = re.compile(r"^(?P<key>before|after)\s*:\s*(?P<value>-?[\d.]+)\s*$", re.I)


def cleaning_steps(text: str) -> list[tuple[str, dict[str, float]]]:
    """Split CLEANING.md into (step title, measurements) pairs."""
    steps: list[tuple[str, dict[str, float]]] = []
    current: str | None = None
    values: dict[str, float] = {}
    for line in text.splitlines():
        header = _STEP_RE.match(line)
        if header:
            if current is not None:
                steps.append((current, values))
            current = header.group("title")
            values = {}
            continue
        if current is None:
            continue
        measure = _MEASURE_RE.match(line.strip())
        if measure:
            values[measure.group("key").lower()] = float(measure.group("value"))
    if current is not None:
        steps.append((current, values))
    return steps


LOG_FILE = "RESEARCH_LOG.md"


_ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")


def research_log_rows(text: str) -> list[dict[str, str]]:
    """Read the research log's Markdown table into ordered dicts."""
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        match = _ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if header is None:
            header = [cell.lower() for cell in cells]
            continue
        if all(set(cell) <= {"-", ":"} and cell for cell in cells):
            continue  # the ---|--- separator row
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


REPORT_FILE = "REPORT.md"


FINDINGS_HEADING = "## Findings"


ESTIMATE_WORDS = (
    "mean",
    "average",
    "median",
    "difference",
    "rate",
    "estimate",
    "higher",
    "lower",
    "increase",
    "decrease",
    "proportion",
)


_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


_INTERVAL_RES = (
    re.compile(r"\bci\b", re.I),
    re.compile(r"confidence interval", re.I),
    re.compile(r"credible interval", re.I),
    re.compile(r"\binterval\b", re.I),
    re.compile(r"±"),
    re.compile(r"\+/-"),
    re.compile(r"-?\d+(?:\.\d+)?\s+to\s+-?\d+(?:\.\d+)?"),
    # "anywhere between 3.80 and 7.21" states an interval in words. This
    # pattern was added because the harness flagged exactly that sentence in
    # its own worked report -- a real false positive, fixed in the checker
    # rather than papered over by rewording the report.
    re.compile(r"between\s+-?\d+(?:\.\d+)?\s+and\s+-?\d+(?:\.\d+)?", re.I),
    re.compile(r"\[\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\]"),
)


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def findings_section(text: str) -> str | None:
    """The report's findings section only. The gate is deliberately scoped:
    a methods paragraph mentioning a row count is not a claim, and flagging
    it would train the reader to ignore the harness."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == FINDINGS_HEADING.lower():
            start = index + 1
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def sentences_of(block: str) -> list[str]:
    paragraphs = [p for p in block.split("\n\n") if p.strip()]
    sentences = []
    for paragraph in paragraphs:
        flat = " ".join(paragraph.split())
        if flat.startswith(("!", "|", "#", "-", "*")):
            continue  # images, tables, headings and bullets are not prose
        sentences.extend(s.strip() for s in _SENTENCE_SPLIT.split(flat) if s.strip())
    return sentences


FIGURES_FILE = "FIGURES.json"


FIGURES_DIR = "figures"


FIGURE_SUFFIXES = (".png", ".svg", ".jpg", ".jpeg", ".pdf")


MANIFEST_FILE = "MANIFEST.json"


_MANIFEST_EXCLUDE = {MANIFEST_FILE}


# ===========================================================================
# YOUR WORK -- nine exercises
# ===========================================================================


def gate_question_recorded(study_dir: Path) -> GateResult:
    """Exercise 1. Fail a study whose question file is missing or empty, and
    name the file.

    Pass when QUESTION.md exists, has non-heading body text, and at least one
    of those body lines ends in a question mark. Fail otherwise, with one of:

        "QUESTION.md is missing"
        "QUESTION.md is empty"
        "QUESTION.md contains only headings, no question text"
        "QUESTION.md records no question sentence (no non-heading line ends in
         a question mark)"

    Use `_read_text(study_dir, QUESTION_FILE)`, which returns None when the
    file is absent.
    """
    raise NotImplementedError


def gate_provenance_complete(study_dir: Path) -> GateResult:
    """Exercise 2. Fail a source record missing a URL, retrieval date or
    checksum, and name which one.

    Read SOURCE.json with `_read_json`. For every key in
    REQUIRED_SOURCE_FIELDS that is absent, None or blank, add the finding
    "SOURCE.json is missing: <key>" -- one per key, so three missing fields
    give three findings.

    Two extras that make the gate worth running:
      * if `retrieved` is present but does not match `_DATE_RE`, say so;
      * if the record carries a `path`, recompute `sha256_of` that file and
        compare it with `checksum_sha256`. A checksum nobody verifies is a
        decoration.
    """
    raise NotImplementedError


def gate_grain_asserted(study_dir: Path) -> GateResult:
    """Exercise 3. Fail a study whose ingestion has no row-grain assertion;
    pass one that has it.

    Read INGEST.json. Require a non-empty `grain` list, a `grain_verified`
    key that is exactly True, and a `rows_in` count. A grain declared but
    never verified is a hope with a schema, so say that plainly when
    `grain_verified` is absent, and report `grain_violations` when it is
    present and false.
    """
    raise NotImplementedError


def gate_damage_report_quantified(study_dir: Path) -> GateResult:
    """Exercise 4. Fail a cleaning step documented without a before/after
    measurement -- a changelog is not a damage report.

    `cleaning_steps(text)` gives you (title, {"before": x, "after": y}) pairs.
    Fail when a step is missing either measurement, naming the step, and fail
    when before equals after -- a step that changed nothing measurable either
    did not need doing or measured the wrong thing.
    """
    raise NotImplementedError


def gate_confirmation_untouched(study_dir: Path) -> GateResult:
    """Exercise 5. Detect a study whose confirmation split was used during
    exploration, by checking the research log's ordering against the split's
    first use.

    `research_log_rows(text)` gives you the log as ordered dicts with `seq`,
    `timestamp`, `split`, `activity` and `outcome`. Find the index of the
    first row whose `activity` contains "hypothesis declared", and the index
    of the first row whose `split` is "confirmation". Fail when the second
    index is less than or equal to the first, and say which entries.

    Also fail when either is missing, and when the confirmation split is used
    more than once.
    """
    raise NotImplementedError


def gate_uncertainty_reported(study_dir: Path) -> GateResult:
    """Exercise 6. Fail a reported estimate with no interval, and name the
    sentence.

    Take `findings_section(text)`, then `sentences_of(block)`. A sentence is
    an estimate if it contains a number (`_NUMBER_RE`) AND one of
    ESTIMATE_WORDS. An estimate sentence must also match one of
    `_INTERVAL_RES`. Quote the offending sentence in the finding, truncated
    to about 160 characters, because on a twelve-page report the sentence is
    the fix and the filename is a re-read.

    Fail too when the findings section reports no numeric estimate at all.
    """
    raise NotImplementedError


def gate_figures_documented(study_dir: Path) -> GateResult:
    """Exercise 7. Fail an unlabelled figure and pass a documented one.

    FIGURES.json is a list of records. Each needs a `file` that exists under
    the study directory, a non-empty `question` and a non-empty `claim`.
    Then check the other direction: every file under `figures/` with a
    FIGURE_SUFFIXES extension must appear in FIGURES.json, or it is a chart
    that survived three drafts because nobody remembered what it was for.
    """
    raise NotImplementedError


def gate_outputs_reproducible(study_dir: Path) -> GateResult:
    """Exercise 8. Detect a study whose output changed between runs.

    MANIFEST.json holds {"algorithm": "sha256", "files": {path: digest}}.
    Recompute each digest. Report a file that no longer matches, a manifest
    entry with no file, a file on disk the manifest never mentions, and a
    manifest that does not cover REPORT.md at all.
    """
    raise NotImplementedError


GATES = (
    gate_question_recorded,
    gate_provenance_complete,
    gate_grain_asserted,
    gate_damage_report_quantified,
    gate_confirmation_untouched,
    gate_uncertainty_reported,
    gate_figures_documented,
    gate_outputs_reproducible,
)

GATE_NAMES = (
    "question_recorded",
    "provenance_complete",
    "grain_asserted",
    "damage_report_quantified",
    "confirmation_untouched",
    "uncertainty_reported",
    "figures_documented",
    "outputs_reproducible",
)


def check_study(path) -> StudyVerdict:
    """Exercise 9. Run every gate and return the verdict.

    Raise `FileNotFoundError` when `path` is not a directory. Otherwise run
    ALL eight gates -- never stop at the first failure -- and return a
    `StudyVerdict` carrying the directory path and the eight results in
    GATE_NAMES order.
    """
    raise NotImplementedError
