"""The reference suite: every claim the worked study and the harness make.

Run from the lab directory:

    .venv/bin/pytest examples -q

Nothing here asserts on a timing. Everything asserts on a shape, an exact
value the arithmetic fixes, or a measured value against a stated tolerance.
"""

from __future__ import annotations

import hashlib
import json

import pytest

import acceptance
import dataset as ds
import fixtures as fx
import study


# ---------------------------------------------------------------------------
# One worked study, built once for the whole session
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def workspace(tmp_path_factory):
    return tmp_path_factory.mktemp("day140")


@pytest.fixture(scope="session")
def good(workspace):
    return fx.worked_study(workspace, name="worked")


@pytest.fixture(scope="session")
def summary(workspace):
    return study.build_study(workspace / "summary-run")


# ---------------------------------------------------------------------------
# The dataset shipped with the lab
# ---------------------------------------------------------------------------


def test_committed_csv_matches_its_generator(tmp_path):
    """The committed file and the generator can never drift apart silently."""
    regenerated = ds.write_source_csv(tmp_path / "observations.csv")
    assert regenerated.read_bytes() == ds.SOURCE_CSV.read_bytes()


def test_dataset_carries_its_four_defects():
    frame = ds.load_source_csv()
    assert len(frame) == 264
    assert len(frame) - frame["reading_id"].nunique() == 8
    assert (frame["pm25_ug_m3"] == "-1.0").sum() == 6
    assert (frame["pm25_ug_m3"] == "").sum() == 5
    assert frame["station_type"].nunique() == 8


def test_dataset_plants_a_real_effect(summary):
    """The measured difference is an estimate of a difference the generator
    really planted, so the interval has a right answer to contain."""
    assert ds.TRUE_DIFFERENCE == 6.0
    assert summary["ci_low"] < ds.TRUE_DIFFERENCE < summary["ci_high"]


# ---------------------------------------------------------------------------
# The statistics, checked against a hand computation
# ---------------------------------------------------------------------------


def test_phi_of_zero_is_one_half():
    assert study.phi(0.0) == pytest.approx(0.5)


def test_z_critical_for_95_percent():
    # The textbook value for a two-sided 95% interval.
    assert study.z_critical_two_sided(0.05) == pytest.approx(1.959964, abs=1e-5)


def test_difference_in_means_matches_hand_computation():
    import math
    import statistics

    a = [12.0, 14.0, 11.0, 15.0, 13.0, 12.5, 14.5, 13.5]
    b = [9.0, 10.0, 8.5, 11.0, 9.5, 10.5, 8.0, 9.0]
    est = study.difference_in_means(a, b)
    se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
    diff = statistics.mean(a) - statistics.mean(b)
    assert est.difference == pytest.approx(diff, abs=1e-12)
    assert est.standard_error == pytest.approx(se, abs=1e-12)
    assert est.low == pytest.approx(diff - 1.959964 * se, abs=1e-5)
    assert est.high == pytest.approx(diff + 1.959964 * se, abs=1e-5)


def test_the_interval_is_symmetric_about_the_estimate(summary):
    midpoint = (summary["ci_low"] + summary["ci_high"]) / 2.0
    assert midpoint == pytest.approx(summary["difference"], abs=1e-9)


# ---------------------------------------------------------------------------
# The arc, stage by stage
# ---------------------------------------------------------------------------


def test_ingest_reports_the_grain_violation_on_arrival():
    raw = ds.load_source_csv()
    result = study.ingest(raw)
    assert result.grain == ("reading_id",)
    assert result.grain_verified is False
    assert result.grain_violations == 8


def test_cleaning_resolves_the_grain_and_measures_every_step():
    raw = ds.load_source_csv()
    cleaned, steps = study.clean(study.ingest(raw).frame)
    assert study.ingest(cleaned).grain_verified is True
    assert [s.name for s in steps] == [
        "normalise station_type casing",
        "drop duplicate reading_id rows",
        "drop sensor fault sentinel readings",
        "drop rows with no pm25 reading",
    ]
    assert [(s.before, s.after) for s in steps] == [
        (8, 2), (264, 256), (6, 0), (5, 0),
    ]
    assert len(cleaned) == 245
    assert sorted(cleaned["station_type"].unique()) == ["park", "roadside"]


def test_the_split_is_disjoint_and_covers_everything():
    raw = ds.load_source_csv()
    cleaned, _ = study.clean(study.ingest(raw).frame)
    exploration, confirmation = study.split_exploration_confirmation(cleaned)
    assert len(exploration) + len(confirmation) == len(cleaned)
    ids = set(exploration["reading_id"]) & set(confirmation["reading_id"])
    assert ids == set()


def test_the_split_is_the_same_every_time():
    raw = ds.load_source_csv()
    cleaned, _ = study.clean(study.ingest(raw).frame)
    first, _ = study.split_exploration_confirmation(cleaned)
    second, _ = study.split_exploration_confirmation(cleaned)
    assert list(first["reading_id"]) == list(second["reading_id"])


def test_the_comparison_count_is_the_research_log_length(good, summary):
    rows = acceptance.research_log_rows((good / "RESEARCH_LOG.md").read_text())
    exploration_rows = [r for r in rows if r["split"] == "exploration"]
    assert len(exploration_rows) == summary["comparison_count"] == 4


def test_the_report_states_the_interval_and_the_comparison_count(good, summary):
    # The report is wrapped, so flatten the whitespace before matching phrases
    # that may straddle a line break.
    text = " ".join((good / "REPORT.md").read_text().split())
    assert f"{summary['difference']:.2f} ug/m3 higher" in text
    assert f"95% CI {summary['ci_low']:.2f} to {summary['ci_high']:.2f}" in text
    assert f"declared: {summary['comparison_count']}." in text


def test_the_report_names_what_it_cannot_do(good):
    text = (good / "REPORT.md").read_text()
    assert "does not establish" in text
    assert "proxy" in text
    assert "Who is missing" in text
    assert "would establish causation" in text


def test_the_study_writes_every_expected_file(good):
    names = {p.relative_to(good).as_posix() for p in good.rglob("*") if p.is_file()}
    assert names == {
        "QUESTION.md",
        "SOURCE.json",
        "INGEST.json",
        "CLEANING.md",
        "RESEARCH_LOG.md",
        "FIGURES.json",
        "REPORT.md",
        "MANIFEST.json",
        "data/observations.csv",
        "figures/fig-01-pm25-by-station-type.png",
        "figures/fig-02-pm25-distribution.png",
    }


def test_the_figures_are_real_png_files(good):
    for record in json.loads((good / "FIGURES.json").read_text()):
        data = (good / record["file"]).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(data) > 5_000


def test_the_manifest_covers_every_generated_file(good):
    manifest = json.loads((good / "MANIFEST.json").read_text())
    on_disk = {
        p.relative_to(good).as_posix()
        for p in good.rglob("*")
        if p.is_file() and p.name != "MANIFEST.json"
    }
    assert set(manifest["files"]) == on_disk
    for rel, digest in manifest["files"].items():
        assert hashlib.sha256((good / rel).read_bytes()).hexdigest() == digest


# ---------------------------------------------------------------------------
# The harness: the worked study passes
# ---------------------------------------------------------------------------


def test_every_gate_passes_on_the_worked_study(good):
    verdict = acceptance.check_study(good)
    assert verdict.ok, verdict.findings
    assert verdict.findings == ()
    assert tuple(g.name for g in verdict.gates) == acceptance.GATE_NAMES


def test_gate_names_match_the_gate_functions():
    assert len(acceptance.GATES) == len(acceptance.GATE_NAMES) == 8
    assert tuple(g.__name__ for g in acceptance.GATES) == tuple(
        f"gate_{name}" for name in acceptance.GATE_NAMES
    )


def test_a_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        acceptance.check_study(tmp_path / "nowhere")


def test_an_empty_directory_fails_every_gate(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    verdict = acceptance.check_study(empty)
    assert verdict.failed_gates == acceptance.GATE_NAMES


def test_a_failing_gate_always_carries_a_finding(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    for gate in acceptance.check_study(empty).gates:
        assert gate.findings, gate.name


# ---------------------------------------------------------------------------
# The harness: one defect at a time, one gate at a time
# ---------------------------------------------------------------------------


DEFECTS = [
    ("question_recorded", fx.break_missing_question, "QUESTION.md is missing"),
    ("question_recorded", fx.break_empty_question, "QUESTION.md is empty"),
    ("question_recorded", fx.break_question_without_a_question,
     "records no question sentence"),
    ("provenance_complete", fx.break_provenance, "is missing: checksum_sha256"),
    ("provenance_complete", fx.break_provenance_checksum, "does not match"),
    ("grain_asserted", fx.break_grain, "declares no row grain"),
    ("grain_asserted", fx.break_grain_unverified, "never checked against the data"),
    ("damage_report_quantified", fx.break_damage_report,
     "changelog entry, not a damage report"),
    ("confirmation_untouched", fx.break_confirmation_peeked,
     "before the hypothesis was declared"),
    ("uncertainty_reported", fx.break_uncertainty,
     "estimate reported without an interval"),
    ("figures_documented", fx.break_figure_label, "carries no claim"),
    ("figures_documented", fx.break_figure_undocumented, "undocumented"),
]


@pytest.mark.parametrize(
    "gate_name,mutator,expected",
    DEFECTS,
    ids=[f"{name}-{mutator.__name__}" for name, mutator, _ in DEFECTS],
)
def test_one_defect_fails_exactly_one_gate(good, tmp_path, gate_name, mutator, expected):
    broken = fx.variant(good, tmp_path / "broken", mutator)
    verdict = acceptance.check_study(broken)
    assert verdict.failed_gates == (gate_name,), verdict.findings
    gate = verdict.gate(gate_name)
    assert any(expected in finding for finding in gate.findings), gate.findings


def test_provenance_names_each_missing_field_individually(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_provenance)
    findings = acceptance.check_study(broken).gate("provenance_complete").findings
    assert set(findings) == {
        "SOURCE.json is missing: url",
        "SOURCE.json is missing: retrieved",
        "SOURCE.json is missing: checksum_sha256",
    }


def test_the_uncertainty_finding_quotes_the_sentence(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_uncertainty)
    findings = acceptance.check_study(broken).gate("uncertainty_reported").findings
    assert len(findings) == 1
    assert "5.50 ug/m3 higher than park stations" in findings[0]


INTERVAL_FORMS = [
    "The mean difference was 5.50 ug/m3 (95% CI 3.80 to 7.21).",
    "The mean difference was 5.50 ug/m3 (confidence interval 3.80, 7.21).",
    "The mean difference was 5.50 ug/m3 ±1.70.",
    "The mean difference was 5.50 ug/m3, interval [3.80, 7.21].",
    "The mean difference was anywhere between 3.80 and 7.21 ug/m3.",
    "The estimated mean difference was 3.80 to 7.21 ug/m3.",
]


@pytest.mark.parametrize("sentence", INTERVAL_FORMS)
def test_interval_evidence_is_recognised(good, tmp_path, sentence):
    def rewrite(study_dir):
        path = study_dir / "REPORT.md"
        lines = path.read_text().splitlines()
        start = lines.index("## Findings")
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
        body = ["## Findings", "", sentence, ""]
        path.write_text("\n".join(lines[:start] + body + lines[end:]) + "\n")

    probe = fx.variant(good, tmp_path / "probe", rewrite)
    assert acceptance.check_study(probe).gate("uncertainty_reported").ok


def test_a_findings_section_with_no_estimate_fails(good, tmp_path):
    def rewrite(study_dir):
        path = study_dir / "REPORT.md"
        lines = path.read_text().splitlines()
        start = lines.index("## Findings")
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
        body = ["## Findings", "", "The effect was clear and worth acting on.", ""]
        path.write_text("\n".join(lines[:start] + body + lines[end:]) + "\n")

    probe = fx.variant(good, tmp_path / "probe", rewrite)
    findings = acceptance.check_study(probe).gate("uncertainty_reported").findings
    assert any("reports no numeric estimate" in f for f in findings), findings


def test_a_confirmation_set_never_used_is_caught(good, tmp_path):
    def strip(study_dir):
        path = study_dir / "RESEARCH_LOG.md"
        kept = [
            line for line in path.read_text().splitlines()
            if "| confirmation |" not in line
        ]
        path.write_text("\n".join(kept) + "\n")

    probe = fx.variant(good, tmp_path / "probe", strip)
    findings = acceptance.check_study(probe).gate("confirmation_untouched").findings
    assert any("never used" in f for f in findings), findings


def test_a_peeked_study_looks_identical_everywhere_except_the_log(good, tmp_path):
    """The reason this gate has to read the log: nothing else changes."""
    peeked = fx.variant(good, tmp_path / "peeked", fx.break_confirmation_peeked)
    for name in ("REPORT.md", "FIGURES.json", "CLEANING.md", "SOURCE.json"):
        assert (good / name).read_bytes() == (peeked / name).read_bytes()
    assert acceptance.check_study(peeked).failed_gates == ("confirmation_untouched",)


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------


def test_two_builds_produce_identical_markdown(workspace):
    first = study.build_study(workspace / "repro-a") and workspace / "repro-a"
    study.build_study(workspace / "repro-b")
    second = workspace / "repro-b"
    for name in ("REPORT.md", "CLEANING.md", "QUESTION.md", "RESEARCH_LOG.md"):
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_two_builds_produce_identical_figures(workspace):
    first, second = workspace / "repro-a", workspace / "repro-b"
    for name in ("fig-01-pm25-by-station-type.png", "fig-02-pm25-distribution.png"):
        assert (first / "figures" / name).read_bytes() == (
            second / "figures" / name
        ).read_bytes(), name


def test_the_harness_detects_output_that_changed_after_the_manifest(good, tmp_path):
    drifted = fx.variant(
        good, tmp_path / "drifted", fx.break_reproducibility, rewrite_manifest=False
    )
    findings = acceptance.check_study(drifted).gate("outputs_reproducible").findings
    assert len(findings) == 1
    assert "REPORT.md" in findings[0]
    assert "changed since the manifest was written" in findings[0]


def test_the_harness_detects_an_untracked_output(good, tmp_path):
    def add(study_dir):
        (study_dir / "scratch.md").write_text("# scratch\n")

    probe = fx.variant(good, tmp_path / "untracked", add, rewrite_manifest=False)
    findings = acceptance.check_study(probe).gate("outputs_reproducible").findings
    assert findings == ("scratch.md exists but is not covered by MANIFEST.json",)


def test_the_harness_detects_a_manifest_entry_with_no_file(good, tmp_path):
    def remove(study_dir):
        (study_dir / "figures" / "fig-02-pm25-distribution.png").unlink()

    probe = fx.variant(good, tmp_path / "gone", remove, rewrite_manifest=False)
    findings = acceptance.check_study(probe).gate("outputs_reproducible").findings
    assert any("which does not exist" in f for f in findings), findings


# ---------------------------------------------------------------------------
# The whole harness, end to end
# ---------------------------------------------------------------------------


def test_removing_one_required_element_fails_exactly_one_gate(good, tmp_path):
    def remove_checksum(study_dir):
        path = study_dir / "SOURCE.json"
        payload = json.loads(path.read_text())
        del payload["checksum_sha256"]
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    broken = fx.variant(good, tmp_path / "one-gone", remove_checksum)
    verdict = acceptance.check_study(broken)
    assert verdict.failed_gates == ("provenance_complete",)
    assert verdict.findings == ("SOURCE.json is missing: checksum_sha256",)


def test_three_defects_produce_three_failed_gates(good, tmp_path):
    def three(study_dir):
        fx.break_missing_question(study_dir)
        fx.break_grain(study_dir)
        fx.break_figure_label(study_dir, index=1, key="claim")

    broken = fx.variant(good, tmp_path / "three", three)
    verdict = acceptance.check_study(broken)
    assert set(verdict.failed_gates) == {
        "question_recorded", "grain_asserted", "figures_documented"
    }


def test_the_verdict_summary_reads_as_a_task_list(good, tmp_path):
    broken = fx.variant(good, tmp_path / "summary", fx.break_missing_question)
    summary_text = acceptance.check_study(broken).summary()
    assert summary_text.startswith("NOT ACCEPTED:")
    assert "[FAIL] question_recorded" in summary_text
    assert "QUESTION.md is missing" in summary_text
    assert summary_text.count("[PASS]") == 7


def test_gate_lookup_rejects_an_unknown_name(good):
    with pytest.raises(KeyError):
        acceptance.check_study(good).gate("no_such_gate")
