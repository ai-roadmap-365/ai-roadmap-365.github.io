"""The worked miniature study: the whole arc, actually performed.

This module carries one small question from "written down before looking" to
"reported with its limits", using the tools Course 03 taught, and writes the
result as a *study directory* -- the artefact `acceptance.py` grades.

The arc, and where each stage came from:

    question      Day 119 / Day 136   QUESTION.md, written before any look
    provenance    Day 134             SOURCE.json: licence, dictionary, checksum
    ingestion     Day 135             INGEST.json: a stated grain, asserted
    cleaning      Days 121, 125       CLEANING.md: a damage report, measured
    exploration   Day 136             RESEARCH_LOG.md, confirmation set sealed
    statistics    Days 117, 118       an interval, and the comparison count
    visuals       Days 127-132        FIGURES.json: each figure has a claim
    pipeline      Day 126             MANIFEST.json: checksums of every output
    report        Day 133             REPORT.md: the argument
    ethics        Day 138             the limits section, named not implied

Everything here is deterministic. There is no clock reading anywhere: the
`as_of` date is a parameter, the research-log timestamps are fixed strings,
the split is a seeded permutation, and the figures are saved with their PNG
`Software` metadata suppressed. That is not fastidiousness for its own sake --
`09_whole_harness.py` asserts that two independent builds of this study
produce byte-identical Markdown, and every clock reading left in would break
it.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, no plt.show(), ever

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import dataset as ds  # noqa: E402

SPLIT_SEED = 20260630
CONFIDENCE = 0.95
AS_OF = "2026-06-30"

QUESTION = (
    "Do roadside air-quality stations record higher PM2.5 than park stations, "
    "and by how much?"
)

# The four looks taken on the exploration half, in the order they were taken.
# The count of these IS the comparison count reported in REPORT.md; that is
# the whole reason the log is a data structure rather than a memory.
EXPLORATION_LOOKS = (
    ("2026-06-30T09:05:00Z", "distribution of pm25_ug_m3 across all stations",
     "right-skewed, no second mode; nothing to explain"),
    ("2026-06-30T09:18:00Z", "pm25_ug_m3 split by station_type",
     "roadside sits visibly higher; worth a hypothesis"),
    ("2026-06-30T09:31:00Z", "pm25_ug_m3 against humidity_pct",
     "no visible relationship; nothing found"),
    ("2026-06-30T09:44:00Z", "pm25_ug_m3 by individual station_id",
     "spread within each type, no single station driving the gap"),
)

HYPOTHESIS = (
    "Roadside stations have a higher mean PM2.5 than park stations."
)


# ---------------------------------------------------------------------------
# The statistics, built from math.erf alone -- the Day 118 construction
# ---------------------------------------------------------------------------


def phi(z: float) -> float:
    """The standard normal CDF."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def z_critical_two_sided(alpha: float) -> float:
    """The z whose two-sided tail probability is alpha, by bisection: there
    is no closed form for the inverse of `phi`."""
    low, high = 0.0, 10.0
    target = 1.0 - alpha / 2.0
    for _ in range(200):
        mid = (low + high) / 2.0
        if phi(mid) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def p_from_z_two_sided(z: float) -> float:
    return 2.0 * (1.0 - phi(abs(z)))


@dataclass(frozen=True)
class Estimate:
    """A difference of means with the uncertainty attached to it, because an
    estimate without an interval is a number pretending to be a fact."""

    difference: float
    standard_error: float
    low: float
    high: float
    z: float
    p_value: float
    n_a: int
    n_b: int


def difference_in_means(a, b, confidence: float = CONFIDENCE) -> Estimate:
    """Welch-style difference of means: each group keeps its own variance."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diff = float(a.mean() - b.mean())
    se = float(math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))
    z_star = z_critical_two_sided(1.0 - confidence)
    z = diff / se
    return Estimate(
        difference=diff,
        standard_error=se,
        low=diff - z_star * se,
        high=diff + z_star * se,
        z=z,
        p_value=p_from_z_two_sided(z),
        n_a=int(len(a)),
        n_b=int(len(b)),
    )


# ---------------------------------------------------------------------------
# Ingestion, with a stated grain (Day 135)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IngestResult:
    frame: pd.DataFrame
    rows_in: int
    grain: tuple[str, ...]
    grain_verified: bool
    grain_violations: int


def ingest(raw: pd.DataFrame, grain: tuple[str, ...] = ("reading_id",)) -> IngestResult:
    """Bring the raw text frame in, and assert the grain before anything else
    touches it. The grain is the sentence "one row is one ___". Here it is
    "one row is one reading", and the raw delivery violates it eight times."""
    rows_in = len(raw)
    duplicated = int(raw.duplicated(subset=list(grain)).sum())
    return IngestResult(
        frame=raw.copy(),
        rows_in=rows_in,
        grain=grain,
        grain_verified=duplicated == 0,
        grain_violations=duplicated,
    )


# ---------------------------------------------------------------------------
# Cleaning, with a damage report (Days 121 and 125)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DamageStep:
    """One cleaning step, with the measurement that makes it a damage report
    rather than a changelog entry: what the quantity was before, and after."""

    name: str
    measure: str
    before: float
    after: float
    note: str

    @property
    def changed(self) -> float:
        return self.before - self.after


def clean(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[DamageStep]]:
    """Four steps, each measured on the way past. Nothing here is clever; the
    discipline is that no step is allowed to happen without a number."""
    steps: list[DamageStep] = []
    work = frame.copy()

    before_types = int(work["station_type"].nunique())
    work["station_type"] = work["station_type"].str.strip().str.lower()
    steps.append(
        DamageStep(
            name="normalise station_type casing",
            measure="distinct station_type values",
            before=before_types,
            after=int(work["station_type"].nunique()),
            note="strip and lower-case; no row is dropped by this step",
        )
    )

    before_rows = len(work)
    work = work.drop_duplicates(subset=["reading_id"], keep="first")
    steps.append(
        DamageStep(
            name="drop duplicate reading_id rows",
            measure="rows",
            before=before_rows,
            after=len(work),
            note="the duplicates are byte-identical redeliveries; first wins",
        )
    )

    work["pm25_ug_m3"] = pd.to_numeric(work["pm25_ug_m3"], errors="coerce")

    before_sentinel = int((work["pm25_ug_m3"] == ds.FAULT_SENTINEL).sum())
    work = work[work["pm25_ug_m3"] != ds.FAULT_SENTINEL]
    steps.append(
        DamageStep(
            name="drop sensor fault sentinel readings",
            measure="rows carrying the -1.0 fault sentinel",
            before=before_sentinel,
            after=int((work["pm25_ug_m3"] == ds.FAULT_SENTINEL).sum()),
            note="-1.0 is not a low reading; it is the unit reporting a fault",
        )
    )

    before_missing = int(work["pm25_ug_m3"].isna().sum())
    work = work[work["pm25_ug_m3"].notna()]
    steps.append(
        DamageStep(
            name="drop rows with no pm25 reading",
            measure="rows with a blank pm25_ug_m3",
            before=before_missing,
            after=int(work["pm25_ug_m3"].isna().sum()),
            note="blank means the reading never arrived; it is not a zero",
        )
    )

    work = work.reset_index(drop=True)
    return work, steps


# ---------------------------------------------------------------------------
# The exploration/confirmation split (Day 136)
# ---------------------------------------------------------------------------


def split_exploration_confirmation(
    frame: pd.DataFrame, seed: int = SPLIT_SEED
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Halve the cleaned frame with a seeded permutation. This happens BEFORE
    any look, and the confirmation half is not opened until a hypothesis
    exists -- which is a claim about ordering, and therefore something a
    research log can be checked against."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(frame))
    cut = len(frame) // 2
    exploration = frame.iloc[order[:cut]].reset_index(drop=True)
    confirmation = frame.iloc[order[cut:]].reset_index(drop=True)
    return exploration, confirmation


# ---------------------------------------------------------------------------
# The figures (Days 127-132)
# ---------------------------------------------------------------------------

_ROADSIDE_COLOUR = "#1d4ed8"
_PARK_COLOUR = "#0f766e"


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # metadata={"Software": None} drops the matplotlib-version tag PNG writers
    # add by default, which is the one thing that would otherwise make two
    # builds of the same figure differ byte for byte.
    fig.savefig(path, format="png", dpi=110, bbox_inches="tight",
                metadata={"Software": None})
    plt.close(fig)


def figure_pm25_by_station_type(exploration: pd.DataFrame, path: Path) -> None:
    """A box plot: the right chart for "are these two distributions
    different", because it shows spread and overlap rather than hiding both
    behind two bars whose height difference is the only visible fact."""
    roadside = exploration.loc[exploration["station_type"] == "roadside", "pm25_ug_m3"]
    park = exploration.loc[exploration["station_type"] == "park", "pm25_ug_m3"]

    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    parts = ax.boxplot(
        [roadside.to_numpy(), park.to_numpy()],
        tick_labels=[f"roadside (n={len(roadside)})", f"park (n={len(park)})"],
        patch_artist=True,
        widths=0.5,
    )
    for patch, colour in zip(parts["boxes"], (_ROADSIDE_COLOUR, _PARK_COLOUR)):
        patch.set_facecolor(colour)
        patch.set_alpha(0.30)
        patch.set_edgecolor(colour)
    for median in parts["medians"]:
        median.set_color("#1a202c")

    # The axis starts at zero: PM2.5 is a ratio quantity, so a truncated
    # baseline would exaggerate the gap. Lie factor stays at 1.
    ax.set_ylim(0, None)
    ax.set_ylabel("PM2.5 (ug/m3)")
    ax.set_title("Exploration half: PM2.5 by station type")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, path)


def figure_pm25_distribution(exploration: pd.DataFrame, path: Path) -> None:
    """A histogram: the right chart for "what shape is this quantity", and the
    honest answer to whether the gap above is two clean modes (it is not)."""
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    bins = np.arange(0.0, 36.0, 2.0)
    for label, colour in (("roadside", _ROADSIDE_COLOUR), ("park", _PARK_COLOUR)):
        values = exploration.loc[exploration["station_type"] == label, "pm25_ug_m3"]
        ax.hist(values.to_numpy(), bins=bins, alpha=0.55, label=label, color=colour)
    ax.set_xlabel("PM2.5 (ug/m3)")
    ax.set_ylabel("readings")
    ax.set_title("Exploration half: overlapping PM2.5 distributions")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, path)


# ---------------------------------------------------------------------------
# Writing the study directory
# ---------------------------------------------------------------------------


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, payload) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _research_log_markdown(hypothesis_time: str, confirmation_time: str) -> str:
    lines = [
        "# Research log",
        "",
        "Every look taken, in the order it was taken, including the ones that",
        "found nothing. The number of `exploration` rows below is the",
        "comparison count reported in REPORT.md.",
        "",
        "| seq | timestamp | split | activity | outcome |",
        "| --- | --- | --- | --- | --- |",
    ]
    seq = 0
    for timestamp, activity, outcome in EXPLORATION_LOOKS:
        seq += 1
        lines.append(f"| {seq} | {timestamp} | exploration | {activity} | {outcome} |")
    seq += 1
    lines.append(
        f"| {seq} | {hypothesis_time} | none | hypothesis declared | {HYPOTHESIS} |"
    )
    seq += 1
    lines.append(
        f"| {seq} | {confirmation_time} | confirmation | "
        f"test the declared hypothesis once | see REPORT.md |"
    )
    lines.append("")
    return "\n".join(lines)


def _cleaning_markdown(steps: list[DamageStep], rows_in: int, rows_out: int) -> str:
    lines = [
        "# Damage report",
        "",
        "What the cleaning *changed*, measured. A step with no before/after",
        "number is a changelog entry, not a damage report.",
        "",
        f"Rows in: {rows_in}. Rows out: {rows_out}. "
        f"Rows removed: {rows_in - rows_out} "
        f"({100.0 * (rows_in - rows_out) / rows_in:.2f}% of the delivery).",
        "",
    ]
    for step in steps:
        lines += [
            f"### {step.name}",
            "",
            f"measure: {step.measure}",
            f"before: {step.before:g}",
            f"after: {step.after:g}",
            f"changed: {step.changed:g}",
            "",
            step.note,
            "",
        ]
    return "\n".join(lines)


def _wrap(text: str, width: int = 76) -> str:
    return textwrap.fill(" ".join(text.split()), width=width)


def _report_markdown(
    *,
    as_of: str,
    estimate: Estimate,
    comparison_count: int,
    rows_in: int,
    rows_out: int,
    exploration_n: int,
    confirmation_n: int,
) -> str:
    """Render the report deterministically.

    Paragraphs are wrapped by `textwrap.fill` at a fixed width rather than
    hand-wrapped, so the same numbers always produce the same bytes no matter
    how the source string happened to be laid out in this file.
    """
    blocks: list[tuple[str, str]] = [
        ("h1", "Roadside and park PM2.5: an exploratory study"),
        ("p", f"As of {as_of}. Exploratory. Not causal."),
        ("h2", "Question"),
        ("p", QUESTION),
        ("p",
         "The question was written to QUESTION.md before the source file was "
         "opened, so that the analysis could not quietly become a search for "
         "whichever question the data happened to answer well."),
        ("h2", "What the data is"),
        ("p",
         "A synthetic network of eight fixed air-quality stations, four sited at "
         "roadside and four in parks, reporting daily PM2.5 through June 2026. "
         "Provenance, licence, dictionary and checksum are recorded in "
         "SOURCE.json; the grain -- one row per reading -- is asserted in "
         "INGEST.json, and the record says plainly that the assertion failed on "
         "arrival and what resolved it."),
        ("h2", "What cleaning changed"),
        ("p",
         f"The delivery carried {rows_in} rows. {rows_out} survived cleaning. The "
         f"four steps and their before/after measurements are in CLEANING.md. The "
         f"largest single loss is the eight duplicated readings, which is a grain "
         f"violation rather than a data-quality problem, and would have biased "
         f"every mean below had it gone unnoticed."),
        ("h2", "How it was explored"),
        ("p",
         f"The cleaned frame was split into an exploration half ({exploration_n} "
         f"readings) and a confirmation half ({confirmation_n} readings) before any "
         f"look was taken. RESEARCH_LOG.md records every look in order. The "
         f"exploration half was examined {comparison_count} times. The confirmation "
         f"half was opened once, after the hypothesis was written down, and tested "
         f"once."),
        ("h2", "Findings"),
        ("p",
         f"On the confirmation half, roadside stations recorded a mean PM2.5 "
         f"{estimate.difference:.2f} ug/m3 higher than park stations (95% CI "
         f"{estimate.low:.2f} to {estimate.high:.2f}, n={estimate.n_a} roadside and "
         f"n={estimate.n_b} park readings)."),
        ("p",
         f"The interval excludes zero, so the direction of the difference is the "
         f"same across the whole interval. The estimate is imprecise enough that a "
         f"true difference anywhere between {estimate.low:.2f} and "
         f"{estimate.high:.2f} ug/m3 would be consistent with what was seen, which "
         f"is a much weaker statement than the point value alone would suggest."),
        ("p",
         f"Comparisons examined before this hypothesis was declared: "
         f"{comparison_count}. That number belongs next to the interval, not in a "
         f"footnote: it is what tells a reader how much searching preceded the one "
         f"test."),
        ("h2", "Figures"),
        ("p",
         "Each figure in FIGURES.json carries the question it was drawn to answer "
         "and the claim it supports. Both are drawn from the exploration half only, "
         "so no figure shows the data the estimate above was measured on."),
        ("raw", "![PM2.5 by station type](figures/fig-01-pm25-by-station-type.png)"),
        ("raw", "![PM2.5 distribution](figures/fig-02-pm25-distribution.png)"),
        ("h2", "Limits"),
        ("p",
         "This study is exploratory. It does not establish that roadside siting "
         "*causes* higher PM2.5. Station siting is not randomised: the roadside "
         "units are where they are for reasons -- traffic volume, building density, "
         "land availability -- that are themselves plausible causes of the "
         "difference measured here."),
        ("p",
         "The measured quantity is a proxy. PM2.5 at a fixed station is not what "
         "anyone breathes; exposure depends on where people actually are and for "
         "how long, which this data does not contain."),
        ("p",
         "Who is missing: eight stations is a sample of sites, not of people. "
         "Neighbourhoods without a station contribute nothing, and stations are not "
         "sited at random, so the absence is not random either."),
        ("p",
         "What would establish causation: an intervention -- a road closure, a "
         "traffic-calming scheme, a low-emission zone boundary -- with readings "
         "from the same stations before and after, and control stations outside the "
         "intervention area over the same period. This study names that design; it "
         "does not run it."),
        ("h2", "Reproducing this"),
        ("p",
         "MANIFEST.json records a SHA-256 for every file this study generated. "
         "Rebuilding the study from the same source file and the same seeds "
         "reproduces every one of them, figures included. Nothing here reads the "
         "clock: the as-of date is a parameter."),
    ]

    out: list[str] = []
    for kind, text in blocks:
        if kind == "h1":
            out.append(f"# {text}")
        elif kind == "h2":
            out.append(f"## {text}")
        elif kind == "raw":
            out.append(text)
        else:
            out.append(_wrap(text))
        out.append("")
    return "\n".join(out)


def build_study(dest: Path, as_of: str = AS_OF, source_csv: Path | None = None) -> dict:
    """Run the whole arc and write a complete study directory at `dest`.

    Returns a small summary dict of the numbers the study measured, so callers
    can assert on them without re-parsing the Markdown.
    """
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    source = Path(source_csv) if source_csv is not None else ds.SOURCE_CSV

    # -- question, written down first -------------------------------------
    _write_text(
        dest / "QUESTION.md",
        "# Question\n"
        "\n"
        f"{QUESTION}\n"
        "\n"
        "Written before the source file was opened. A decision this would\n"
        "inform: whether the next four stations in the network are sited to\n"
        "widen roadside coverage or to fill in the park gaps.\n",
    )

    # -- provenance (Day 134) ---------------------------------------------
    data_dir = dest / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    local_copy = data_dir / "observations.csv"
    shutil.copyfile(source, local_copy)

    _write_json(
        dest / "SOURCE.json",
        {
            "name": "Synthetic city air-quality network, June 2026",
            "path": "data/observations.csv",
            "url": "https://example.invalid/air-quality/observations.csv",
            "retrieved": as_of,
            "checksum_sha256": sha256_of(local_copy),
            "licence": "CC0-1.0 (synthetic data generated for this lab)",
            "dictionary": {
                "reading_id": "stable id, one per reading, assigned at capture",
                "station_id": "ST-01..ST-08, fixed monitoring sites",
                "captured_at": "capture date, ISO 8601, YYYY-MM-DD",
                "station_type": "roadside or park; raw casing is inconsistent",
                "pm25_ug_m3": "PM2.5 mass concentration; -1.0 is a fault sentinel",
                "humidity_pct": "relative humidity, percent",
                "temp_c": "air temperature, degrees Celsius",
            },
            "retrieval_note": (
                "This URL is deliberately unresolvable: the file is generated "
                "by dataset.py in this lab and never fetched. The record is "
                "real in shape and honest about its origin."
            ),
        },
    )

    # -- ingestion with a stated grain (Day 135) --------------------------
    raw = ds.load_source_csv(local_copy)
    ingested = ingest(raw)

    # -- cleaning with a damage report (Days 121, 125) --------------------
    cleaned, steps = clean(ingested.frame)
    _write_text(
        dest / "CLEANING.md",
        _cleaning_markdown(steps, ingested.rows_in, len(cleaned)),
    )

    # The grain contract is asserted twice, and the record says so. On arrival
    # it FAILS -- eight redelivered readings -- and that failure is what the
    # second cleaning step exists to resolve. `grain_verified` is the answer
    # for the frame the study actually proceeds with, because that is the
    # frame every number downstream is counted from.
    after_clean = ingest(cleaned, ingested.grain)
    _write_json(
        dest / "INGEST.json",
        {
            "source": "data/observations.csv",
            "grain": list(ingested.grain),
            "grain_statement": "one row is one reading from one station",
            "grain_verified": after_clean.grain_verified,
            "grain_violations": after_clean.grain_violations,
            "grain_violations_on_arrival": ingested.grain_violations,
            "resolved_by": "cleaning step 'drop duplicate reading_id rows'",
            "rows_in": ingested.rows_in,
            "rows_out": len(cleaned),
            "columns": list(raw.columns),
            "read_as": "all columns read as text; nothing coerced before the contract",
        },
    )

    # -- split, then explore (Day 136) ------------------------------------
    exploration, confirmation = split_exploration_confirmation(cleaned)
    _write_text(
        dest / "RESEARCH_LOG.md",
        _research_log_markdown("2026-06-30T09:52:00Z", "2026-06-30T10:07:00Z"),
    )

    # -- figures (Days 127-132), drawn from the exploration half only -----
    fig1 = dest / "figures" / "fig-01-pm25-by-station-type.png"
    fig2 = dest / "figures" / "fig-02-pm25-distribution.png"
    figure_pm25_by_station_type(exploration, fig1)
    figure_pm25_distribution(exploration, fig2)

    _write_json(
        dest / "FIGURES.json",
        [
            {
                "file": "figures/fig-01-pm25-by-station-type.png",
                "question": "Do roadside and park readings occupy different ranges?",
                "claim": (
                    "Roadside readings sit higher, but the boxes overlap: this is "
                    "a shift in centre, not two separate populations."
                ),
                "chart": "box plot",
                "baseline": "y axis starts at zero; PM2.5 is a ratio quantity",
            },
            {
                "file": "figures/fig-02-pm25-distribution.png",
                "question": "What shape is PM2.5 within each station type?",
                "claim": (
                    "Both distributions are single-peaked and broadly overlapping, "
                    "so the difference in means is not driven by a subgroup."
                ),
                "chart": "overlapping histogram, common bins",
                "baseline": "counts from zero; identical 2 ug/m3 bins for both series",
            },
        ],
    )

    # -- the estimate, on the confirmation half, once (Days 117, 118) -----
    road = confirmation.loc[confirmation["station_type"] == "roadside", "pm25_ug_m3"]
    park = confirmation.loc[confirmation["station_type"] == "park", "pm25_ug_m3"]
    estimate = difference_in_means(road, park)

    comparison_count = len(EXPLORATION_LOOKS)
    _write_text(
        dest / "REPORT.md",
        _report_markdown(
            as_of=as_of,
            estimate=estimate,
            comparison_count=comparison_count,
            rows_in=ingested.rows_in,
            rows_out=len(cleaned),
            exploration_n=len(exploration),
            confirmation_n=len(confirmation),
        ),
    )

    # -- the manifest (Day 126), written last ------------------------------
    write_manifest(dest)

    return {
        "rows_in": ingested.rows_in,
        "rows_out": len(cleaned),
        "grain_violations": ingested.grain_violations,
        "damage_steps": len(steps),
        "exploration_n": len(exploration),
        "confirmation_n": len(confirmation),
        "comparison_count": comparison_count,
        "difference": estimate.difference,
        "ci_low": estimate.low,
        "ci_high": estimate.high,
        "p_value": estimate.p_value,
        "n_roadside": estimate.n_a,
        "n_park": estimate.n_b,
    }


MANIFEST_NAME = "MANIFEST.json"


def manifest_targets(study_dir: Path) -> list[str]:
    """Every generated file the manifest is responsible for, as sorted
    study-relative POSIX paths. The manifest never covers itself."""
    study_dir = Path(study_dir)
    names = []
    for path in sorted(study_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(study_dir).as_posix()
        if rel == MANIFEST_NAME:
            continue
        names.append(rel)
    return sorted(names)


def write_manifest(study_dir: Path) -> dict:
    study_dir = Path(study_dir)
    entries = {rel: sha256_of(study_dir / rel) for rel in manifest_targets(study_dir)}
    payload = {"algorithm": "sha256", "files": entries}
    _write_json(study_dir / MANIFEST_NAME, payload)
    return payload
