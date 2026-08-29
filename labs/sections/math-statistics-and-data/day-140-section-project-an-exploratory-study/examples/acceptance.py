"""The acceptance harness: `check_study(path)` grades a study directory.

This is the day's deliverable. It reads a directory laid out the way
`study.py` writes one and returns a structured verdict: eight gates, each
either passing or carrying a list of findings that name the file, the field
or the sentence at fault.

The eight gates, and the seam each one guards:

    question_recorded        a question written down before the looking
    provenance_complete      url, retrieval date, checksum, licence
    grain_asserted           "one row is one ___", checked not assumed
    damage_report_quantified every cleaning step measured before and after
    confirmation_untouched   the split's first use comes after the hypothesis
    uncertainty_reported     every estimate in the findings carries an interval
    figures_documented       every figure carries a question and a claim
    outputs_reproducible     every output still matches its manifest checksum

Two design decisions worth stating plainly, because they are the difference
between a harness that helps and one that is decorative.

**It reads the artefacts, not the intent.** No gate asks whether the analysis
was good. `uncertainty_reported` cannot tell whether an interval is correctly
computed; it can tell whether one is there. That is a much smaller claim, and
it is a claim a machine can actually make.

**Its findings name things.** "Provenance incomplete" is useless at 23:00 the
night before a deadline. "SOURCE.json is missing: checksum_sha256" is a task.

The machine-readable files are JSON rather than YAML for one reason: JSON is
in the standard library and YAML is not, so the harness has no dependency
beyond what the study itself needs. The same eight gates apply unchanged to a
YAML study directory if you swap `json.loads` for a YAML parser.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# The verdict types
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Small readers, shared by the gates
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Gate 1 -- the question was recorded before the analysis
# ---------------------------------------------------------------------------

QUESTION_FILE = "QUESTION.md"


def gate_question_recorded(study_dir: Path) -> GateResult:
    """A study with no written question is a search for whichever question the
    data happens to answer well. The gate cannot prove the question came
    first; it can insist that it exists, is not empty, and is a question."""
    name = "question_recorded"
    text = _read_text(study_dir, QUESTION_FILE)
    if text is None:
        return _failed(name, [f"{QUESTION_FILE} is missing"])
    if not text.strip():
        return _failed(name, [f"{QUESTION_FILE} is empty"])

    body = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not body:
        return _failed(
            name, [f"{QUESTION_FILE} contains only headings, no question text"]
        )
    if not any(line.endswith("?") for line in body):
        return _failed(
            name,
            [
                f"{QUESTION_FILE} records no question sentence "
                f"(no non-heading line ends in a question mark)"
            ],
        )
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 2 -- provenance is complete (Day 134)
# ---------------------------------------------------------------------------

SOURCE_FILE = "SOURCE.json"
REQUIRED_SOURCE_FIELDS = ("url", "retrieved", "checksum_sha256", "licence")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def gate_provenance_complete(study_dir: Path) -> GateResult:
    """Where the data came from, when it was taken, under what licence, and
    what it hashed to on arrival. Any one of those missing and the study
    cannot be re-obtained by anyone, including its own author in six months."""
    name = "provenance_complete"
    study_dir = Path(study_dir)
    payload, error = _read_json(study_dir, SOURCE_FILE)
    if error is not None:
        return _failed(name, [error])
    if not isinstance(payload, dict):
        return _failed(name, [f"{SOURCE_FILE} must be a JSON object"])

    findings = []
    for key in REQUIRED_SOURCE_FIELDS:
        value = payload.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            findings.append(f"{SOURCE_FILE} is missing: {key}")

    retrieved = payload.get("retrieved")
    if isinstance(retrieved, str) and retrieved.strip():
        if not _DATE_RE.match(retrieved.strip()):
            findings.append(
                f"{SOURCE_FILE}: retrieved is not an ISO date "
                f"(got {retrieved.strip()!r})"
            )

    # If the record names the local copy, the checksum is checkable, so check
    # it. A checksum nobody verifies is a decoration.
    recorded = payload.get("checksum_sha256")
    local = payload.get("path")
    if isinstance(local, str) and local.strip() and isinstance(recorded, str):
        local_path = study_dir / local.strip()
        if not local_path.is_file():
            findings.append(f"{SOURCE_FILE}: path {local.strip()} does not exist")
        elif sha256_of(local_path) != recorded.strip():
            findings.append(
                f"{SOURCE_FILE}: checksum_sha256 does not match {local.strip()} "
                f"(recorded {recorded.strip()[:12]}..., "
                f"actual {sha256_of(local_path)[:12]}...)"
            )

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 3 -- the ingestion asserts a row grain (Day 135)
# ---------------------------------------------------------------------------

INGEST_FILE = "INGEST.json"


def gate_grain_asserted(study_dir: Path) -> GateResult:
    """"One row is one ___" is the sentence every downstream count depends on.
    The gate wants the sentence written down AND checked -- a declared grain
    that was never verified is a hope."""
    name = "grain_asserted"
    payload, error = _read_json(study_dir, INGEST_FILE)
    if error is not None:
        return _failed(name, [error])
    if not isinstance(payload, dict):
        return _failed(name, [f"{INGEST_FILE} must be a JSON object"])

    findings = []
    grain = payload.get("grain")
    has_grain = isinstance(grain, list) and bool(grain)
    if not has_grain:
        findings.append(
            f"{INGEST_FILE} declares no row grain: expected a non-empty "
            f"'grain' list of key columns"
        )
    if "grain_verified" not in payload:
        stated = "declares a grain but records" if has_grain else "records"
        findings.append(
            f"{INGEST_FILE} {stated} no 'grain_verified' result: "
            f"the grain was never checked against the data"
        )
    elif payload.get("grain_verified") is not True:
        violations = payload.get("grain_violations", "an unrecorded number of")
        findings.append(
            f"{INGEST_FILE}: grain_verified is not true "
            f"({violations} rows violate the declared grain)"
        )
    if "rows_in" not in payload:
        findings.append(f"{INGEST_FILE} records no 'rows_in' count")

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 4 -- the cleaning carries a damage report (Days 121, 125)
# ---------------------------------------------------------------------------

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


def gate_damage_report_quantified(study_dir: Path) -> GateResult:
    """A changelog says what you did. A damage report says what it cost. The
    gate insists on a before and an after number for every step, and refuses
    a step whose before and after are identical -- a step that changed
    nothing measurable did not need doing, or measured the wrong thing."""
    name = "damage_report_quantified"
    text = _read_text(study_dir, CLEANING_FILE)
    if text is None:
        return _failed(name, [f"{CLEANING_FILE} is missing"])

    steps = cleaning_steps(text)
    if not steps:
        return _failed(
            name,
            [
                f"{CLEANING_FILE} lists no cleaning steps "
                f"(expected one '### <step name>' heading per step)"
            ],
        )

    findings = []
    for title, values in steps:
        missing = [k for k in ("before", "after") if k not in values]
        if missing:
            findings.append(
                f"{CLEANING_FILE}: cleaning step '{title}' is a changelog "
                f"entry, not a damage report: no "
                f"{' or '.join(missing)} measurement"
            )
        elif values["before"] == values["after"]:
            findings.append(
                f"{CLEANING_FILE}: cleaning step '{title}' reports "
                f"before == after ({values['before']:g}); nothing was measured "
                f"to change"
            )

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 5 -- the confirmation set was untouched during exploration (Day 136)
# ---------------------------------------------------------------------------

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


def gate_confirmation_untouched(study_dir: Path) -> GateResult:
    """The confirmation half only means anything if it was opened once, after
    the hypothesis existed. That is a claim about ORDER, and the research log
    is the only record of order the study has -- so the gate reads the log's
    own sequence and compares the hypothesis row against the first
    confirmation row."""
    name = "confirmation_untouched"
    text = _read_text(study_dir, LOG_FILE)
    if text is None:
        return _failed(name, [f"{LOG_FILE} is missing"])

    rows = research_log_rows(text)
    if not rows:
        return _failed(
            name,
            [
                f"{LOG_FILE} contains no log entries "
                f"(expected a Markdown table with seq, timestamp, split, "
                f"activity and outcome columns)"
            ],
        )
    if "split" not in rows[0]:
        return _failed(name, [f"{LOG_FILE} has no 'split' column"])
    if "activity" not in rows[0]:
        return _failed(name, [f"{LOG_FILE} has no 'activity' column"])

    findings = []
    hypothesis_at = None
    confirmation_at = None
    for index, row in enumerate(rows):
        activity = row.get("activity", "").lower()
        split = row.get("split", "").lower()
        if hypothesis_at is None and "hypothesis declared" in activity:
            hypothesis_at = index
        if confirmation_at is None and split == "confirmation":
            confirmation_at = index

    if hypothesis_at is None:
        findings.append(
            f"{LOG_FILE} records no 'hypothesis declared' entry, so there is "
            f"nothing the confirmation set can be said to come after"
        )
    if confirmation_at is None:
        findings.append(
            f"{LOG_FILE} records no entry against the confirmation split: the "
            f"held-out half was never used, so nothing was confirmed"
        )
    if hypothesis_at is not None and confirmation_at is not None:
        if confirmation_at <= hypothesis_at:
            first = rows[confirmation_at]
            findings.append(
                f"{LOG_FILE}: the confirmation split was first used at entry "
                f"{first.get('seq', confirmation_at + 1)} "
                f"({first.get('activity', 'unnamed activity')}), before the "
                f"hypothesis was declared at entry "
                f"{rows[hypothesis_at].get('seq', hypothesis_at + 1)} -- the "
                f"held-out half was part of the exploration"
            )
        confirmation_uses = sum(
            1 for row in rows if row.get("split", "").lower() == "confirmation"
        )
        if confirmation_uses > 1:
            findings.append(
                f"{LOG_FILE}: the confirmation split is used {confirmation_uses} "
                f"times; a confirmation set tested more than once is an "
                f"exploration set with a better name"
            )

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 6 -- the reported estimates carry uncertainty (Days 117, 118)
# ---------------------------------------------------------------------------

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


def gate_uncertainty_reported(study_dir: Path) -> GateResult:
    """An estimate with no interval is a number wearing the costume of a
    fact. The gate is a heuristic and says so: a findings sentence that
    carries a number AND an estimate word must also carry interval evidence
    -- a CI, a plus-or-minus, a bracketed range, or a "x to y" pair."""
    name = "uncertainty_reported"
    text = _read_text(study_dir, REPORT_FILE)
    if text is None:
        return _failed(name, [f"{REPORT_FILE} is missing"])

    block = findings_section(text)
    if block is None:
        return _failed(
            name, [f"{REPORT_FILE} has no '{FINDINGS_HEADING}' section to check"]
        )

    sentences = sentences_of(block)
    if not sentences:
        return _failed(
            name, [f"{REPORT_FILE}: the findings section contains no prose"]
        )

    estimatesentences_of = [
        sentence
        for sentence in sentences
        if _NUMBER_RE.search(sentence)
        and any(word in sentence.lower() for word in ESTIMATE_WORDS)
    ]
    if not estimatesentences_of:
        return _failed(
            name,
            [
                f"{REPORT_FILE}: the findings section reports no numeric "
                f"estimate at all, so there is nothing for a reader to act on"
            ],
        )

    findings = []
    for sentence in estimatesentences_of:
        if not any(pattern.search(sentence) for pattern in _INTERVAL_RES):
            shown = sentence if len(sentence) <= 160 else sentence[:157] + "..."
            findings.append(
                f'{REPORT_FILE}: estimate reported without an interval -- "{shown}"'
            )

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 7 -- every figure carries a question and a claim (Day 133)
# ---------------------------------------------------------------------------

FIGURES_FILE = "FIGURES.json"
FIGURES_DIR = "figures"
FIGURE_SUFFIXES = (".png", ".svg", ".jpg", ".jpeg", ".pdf")


def gate_figures_documented(study_dir: Path) -> GateResult:
    """Day 133's rule, mechanised: a figure exists to answer a question and to
    support a claim. A figure with neither is decoration, and decoration in a
    report is where a reader's attention goes to die."""
    name = "figures_documented"
    study_dir = Path(study_dir)
    payload, error = _read_json(study_dir, FIGURES_FILE)
    if error is not None:
        return _failed(name, [error])
    if not isinstance(payload, list):
        return _failed(
            name, [f"{FIGURES_FILE} must be a JSON list of figure records"]
        )

    findings = []
    documented = set()
    for index, entry in enumerate(payload):
        label = f"{FIGURES_FILE}[{index}]"
        if not isinstance(entry, dict):
            findings.append(f"{label} is not an object")
            continue
        file_name = entry.get("file")
        if not isinstance(file_name, str) or not file_name.strip():
            findings.append(f"{label} names no file")
        else:
            documented.add(file_name.strip())
            if not (study_dir / file_name.strip()).is_file():
                findings.append(f"{label}: {file_name.strip()} does not exist")
        for key in ("question", "claim"):
            value = entry.get(key)
            if not isinstance(value, str) or not value.strip():
                shown = file_name if isinstance(file_name, str) else label
                findings.append(
                    f"{FIGURES_FILE}: figure {shown} carries no {key}"
                )

    figures_dir = study_dir / FIGURES_DIR
    if figures_dir.is_dir():
        for path in sorted(figures_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in FIGURE_SUFFIXES:
                continue
            rel = path.relative_to(study_dir).as_posix()
            if rel not in documented:
                findings.append(
                    f"{rel} is present but undocumented: no entry in "
                    f"{FIGURES_FILE}"
                )

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# Gate 8 -- the outputs still match their manifest (Day 126)
# ---------------------------------------------------------------------------

MANIFEST_FILE = "MANIFEST.json"
_MANIFEST_EXCLUDE = {MANIFEST_FILE}


def gate_outputs_reproducible(study_dir: Path) -> GateResult:
    """A manifest of SHA-256 digests turns "it reproduces" from a belief into
    a check. Rebuild the study, rerun this gate: if any digest moved, the
    pipeline is not deterministic and the report is not reproducible, whatever
    its methods section claims."""
    name = "outputs_reproducible"
    study_dir = Path(study_dir)
    payload, error = _read_json(study_dir, MANIFEST_FILE)
    if error is not None:
        return _failed(name, [error])
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), dict):
        return _failed(
            name,
            [f"{MANIFEST_FILE} must be an object with a 'files' map of path to digest"],
        )

    entries: dict[str, str] = payload["files"]
    if not entries:
        return _failed(name, [f"{MANIFEST_FILE} records no files"])

    findings = []
    for rel in sorted(entries):
        target = study_dir / rel
        if not target.is_file():
            findings.append(f"{MANIFEST_FILE} lists {rel}, which does not exist")
            continue
        actual = sha256_of(target)
        if actual != entries[rel]:
            findings.append(
                f"{rel} does not match its manifest checksum "
                f"(manifest {entries[rel][:12]}..., actual {actual[:12]}...): "
                f"the output changed since the manifest was written"
            )

    on_disk = set()
    for path in sorted(study_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(study_dir).as_posix()
            if rel not in _MANIFEST_EXCLUDE:
                on_disk.add(rel)
    for rel in sorted(on_disk - set(entries)):
        findings.append(f"{rel} exists but is not covered by {MANIFEST_FILE}")

    for required in (REPORT_FILE,):
        if required not in entries:
            findings.append(f"{MANIFEST_FILE} does not cover {required}")

    if findings:
        return _failed(name, findings)
    return _passed(name)


# ---------------------------------------------------------------------------
# The harness
# ---------------------------------------------------------------------------

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
    """Run every gate against a study directory and return the verdict.

    Gates run independently and all of them always run: a study missing its
    question file should still be told about its missing checksum, because
    the point is a task list, not the first thing that went wrong.
    """
    study_dir = Path(path)
    if not study_dir.is_dir():
        raise FileNotFoundError(f"not a study directory: {study_dir}")
    return StudyVerdict(
        path=str(study_dir),
        gates=tuple(gate(study_dir) for gate in GATES),
    )
