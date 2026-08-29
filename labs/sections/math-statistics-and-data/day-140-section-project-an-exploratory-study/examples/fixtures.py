"""Deliberately broken copies of the worked study, one defect at a time.

A harness that has only ever been run on a good study is an untested harness.
Each function here takes a complete, passing study directory and removes or
corrupts exactly one thing, so that a test can assert which gate fires and
what the finding says.

Every mutator rewrites MANIFEST.json afterwards by default. That is not
cosmetic: without it, deleting QUESTION.md would fail BOTH the question gate
and the reproducibility gate, and a test asserting "one gate fired" would be
asserting something untrue. The one exception is `break_reproducibility`,
whose whole point is to leave the manifest stale.

Nothing here writes outside the directory it is handed.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import study


def worked_study(root: Path, name: str = "study", as_of: str = study.AS_OF) -> Path:
    """Build a complete, passing study directory under `root`."""
    dest = Path(root) / name
    study.build_study(dest, as_of=as_of)
    return dest


def copy_of(source: Path, dest: Path) -> Path:
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(Path(source), dest)
    return dest


def variant(source: Path, dest: Path, mutator, *, rewrite_manifest: bool = True) -> Path:
    """Copy `source` to `dest`, apply one defect, and refresh the manifest so
    that exactly the intended gate fails."""
    target = copy_of(source, dest)
    mutator(target)
    if rewrite_manifest:
        study.write_manifest(target)
    return target


# ---------------------------------------------------------------------------
# The defects
# ---------------------------------------------------------------------------


def break_missing_question(study_dir: Path) -> None:
    (Path(study_dir) / "QUESTION.md").unlink()


def break_empty_question(study_dir: Path) -> None:
    (Path(study_dir) / "QUESTION.md").write_text("   \n\n", encoding="utf-8")


def break_question_without_a_question(study_dir: Path) -> None:
    """The commonest real version: a heading and a topic, not a question."""
    (Path(study_dir) / "QUESTION.md").write_text(
        "# Question\n\nAir quality in the city network.\n", encoding="utf-8"
    )


def break_provenance(
    study_dir: Path, drop: tuple[str, ...] = ("url", "retrieved", "checksum_sha256")
) -> None:
    path = Path(study_dir) / "SOURCE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for key in drop:
        payload.pop(key, None)
    payload.pop("path", None)  # nothing left to verify a checksum against
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def break_provenance_checksum(study_dir: Path) -> None:
    """The record keeps its checksum, but the file it describes has moved on."""
    path = Path(study_dir) / "SOURCE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["checksum_sha256"] = "0" * 64
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def break_grain(study_dir: Path) -> None:
    """An ingestion that reads the file and never says what a row is."""
    path = Path(study_dir) / "INGEST.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for key in ("grain", "grain_statement", "grain_verified", "grain_violations"):
        payload.pop(key, None)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def break_grain_unverified(study_dir: Path) -> None:
    """The grain is declared but never checked -- a hope with a schema."""
    path = Path(study_dir) / "INGEST.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("grain_verified", None)
    payload.pop("grain_violations", None)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


CHANGELOG_STEP = "drop sensor fault sentinel readings"


def break_damage_report(study_dir: Path, step: str = CHANGELOG_STEP) -> None:
    """Turn one damage-report entry back into a changelog entry: it still says
    what was done, it no longer says what it cost."""
    path = Path(study_dir) / "CLEANING.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("### "):
            inside = line[4:].strip() == step
            out.append(line)
            continue
        if inside and re.match(r"^(measure|before|after|changed)\s*:", line.strip(), re.I):
            if line.strip().lower().startswith("measure"):
                out.append("removed the readings that carried the fault sentinel.")
            continue
        out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


PEEKED_LOG = """# Research log

Every look taken, in the order it was taken.

| seq | timestamp | split | activity | outcome |
| --- | --- | --- | --- | --- |
| 1 | 2026-06-30T09:05:00Z | exploration | distribution of pm25_ug_m3 across all stations | right-skewed, nothing to explain |
| 2 | 2026-06-30T09:18:00Z | confirmation | check whether the gap also shows up in the held-out half | it does, encouraging |
| 3 | 2026-06-30T09:31:00Z | exploration | pm25_ug_m3 split by station_type | roadside sits higher |
| 4 | 2026-06-30T09:52:00Z | none | hypothesis declared | Roadside stations have a higher mean PM2.5 than park stations. |
| 5 | 2026-06-30T10:07:00Z | confirmation | test the declared hypothesis once | see REPORT.md |
"""


def break_confirmation_peeked(study_dir: Path) -> None:
    """The single most common capstone failure, and the hardest to see from
    the finished report: the held-out half was looked at during exploration,
    so its p-value means nothing. Only the log's ORDER reveals it."""
    (Path(study_dir) / "RESEARCH_LOG.md").write_text(PEEKED_LOG, encoding="utf-8")


BARE_FINDINGS = """
Roadside stations recorded a mean PM2.5 5.50 ug/m3 higher than park stations.

The difference is clear and consistent with what the figures show.

Comparisons examined before this hypothesis was declared: 4.
"""


def break_uncertainty(study_dir: Path) -> None:
    """Strip the interval out of the findings and leave the point estimate
    standing on its own, which is how most first drafts actually read."""
    path = Path(study_dir) / "REPORT.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "## Findings")
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    replacement = ["## Findings"] + BARE_FINDINGS.strip("\n").splitlines() + [""]
    path.write_text("\n".join(lines[:start] + replacement + lines[end:]) + "\n",
                    encoding="utf-8")


def break_figure_label(study_dir: Path, index: int = 0, key: str = "claim") -> None:
    """A figure that answers no stated question and supports no stated claim."""
    path = Path(study_dir) / "FIGURES.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[index].pop(key, None)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def break_figure_undocumented(study_dir: Path) -> None:
    """A figure in the folder that no record mentions -- the one that survived
    three drafts because nobody remembered what it was for."""
    figures = Path(study_dir) / "figures"
    source = figures / "fig-01-pm25-by-station-type.png"
    shutil.copyfile(source, figures / "fig-99-leftover.png")


def break_reproducibility(study_dir: Path) -> None:
    """The output moved after the manifest was written. Called through
    `variant(..., rewrite_manifest=False)`, this is what a non-deterministic
    pipeline looks like from the outside: a second run, different bytes."""
    path = Path(study_dir) / "REPORT.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text + "\nRegenerated at 2026-07-01T14:22:07Z by run 8814.\n",
        encoding="utf-8",
    )
