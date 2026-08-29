"""Your running score. Unattempted work SKIPS; wrong work FAILS with values.

Run from the lab directory:

    .venv/bin/pytest starter -q

On an untouched checkout this reports one pass and everything else skipped.
A skip means "not attempted". A failure means "attempted and wrong", and the
message shows your answer next to the real one so you can see the gap rather
than guess at it.
"""

from __future__ import annotations

import json

import pytest

import acceptance as ex
import fixtures as fx


def attempt(fn, what):
    """Call something that may not be written yet, and skip if it is not."""
    try:
        result = fn()
    except NotImplementedError:
        pytest.skip(f"not attempted yet: {what}")
    if result is None:
        pytest.skip(f"not attempted yet: {what}")
    return result


@pytest.fixture(scope="session")
def workspace(tmp_path_factory):
    return tmp_path_factory.mktemp("day140-starter")


@pytest.fixture(scope="session")
def good(workspace):
    """A complete, passing study directory, built by the given `study.py`."""
    return fx.worked_study(workspace, name="worked")


def test_the_suite_itself_runs():
    """One test that always passes, so a green run is distinguishable from a
    collection error that quietly ran nothing at all."""
    assert ex.REQUIRED_SOURCE_FIELDS == (
        "url",
        "retrieved",
        "checksum_sha256",
        "licence",
    )


# ---------------------------------------------------------------------------
# Exercise 1 -- question recorded before analysis
# ---------------------------------------------------------------------------


def test_question_gate_passes_the_worked_study(good):
    gate = attempt(lambda: ex.gate_question_recorded(good), "gate_question_recorded")
    assert gate.ok, f"the worked study has a real question file, but: {gate.findings}"
    assert gate.name == "question_recorded", f"gate name was {gate.name!r}"


@pytest.mark.parametrize(
    "mutator,expected",
    [
        (fx.break_missing_question, "QUESTION.md is missing"),
        (fx.break_empty_question, "QUESTION.md is empty"),
        (fx.break_question_without_a_question, "records no question sentence"),
    ],
    ids=["missing", "empty", "not-a-question"],
)
def test_question_gate_fails_and_names_the_file(good, tmp_path, mutator, expected):
    broken = fx.variant(good, tmp_path / "broken", mutator)
    gate = attempt(lambda: ex.gate_question_recorded(broken), "gate_question_recorded")
    assert not gate.ok, f"{mutator.__name__} should have failed the gate"
    assert gate.findings, "a failing gate must carry at least one finding"
    assert any(expected in f for f in gate.findings), (
        f"expected a finding containing {expected!r}, got {gate.findings}"
    )
    assert all("QUESTION.md" in f for f in gate.findings), (
        f"every finding must name the file; got {gate.findings}"
    )


# ---------------------------------------------------------------------------
# Exercise 2 -- provenance complete
# ---------------------------------------------------------------------------


def test_provenance_gate_passes_the_worked_study(good):
    gate = attempt(lambda: ex.gate_provenance_complete(good), "gate_provenance_complete")
    assert gate.ok, f"the worked study's SOURCE.json is complete, but: {gate.findings}"


def test_provenance_gate_names_every_missing_field(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_provenance)
    gate = attempt(
        lambda: ex.gate_provenance_complete(broken), "gate_provenance_complete"
    )
    assert not gate.ok
    expected = {
        "SOURCE.json is missing: url",
        "SOURCE.json is missing: retrieved",
        "SOURCE.json is missing: checksum_sha256",
    }
    assert set(gate.findings) == expected, (
        f"expected one finding per missing field:\n  wanted {sorted(expected)}\n"
        f"  got    {sorted(gate.findings)}"
    )


def test_provenance_gate_verifies_the_checksum(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_provenance_checksum)
    gate = attempt(
        lambda: ex.gate_provenance_complete(broken), "gate_provenance_complete"
    )
    assert not gate.ok, (
        "SOURCE.json still lists a checksum, but it no longer matches the file; "
        "the gate must recompute it"
    )
    assert any("does not match" in f for f in gate.findings), gate.findings


# ---------------------------------------------------------------------------
# Exercise 3 -- grain asserted
# ---------------------------------------------------------------------------


def test_grain_gate_passes_a_stated_and_checked_grain(good):
    gate = attempt(lambda: ex.gate_grain_asserted(good), "gate_grain_asserted")
    assert gate.ok, f"INGEST.json states and verifies its grain, but: {gate.findings}"


def test_grain_gate_fails_an_ingestion_with_no_grain(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_grain)
    gate = attempt(lambda: ex.gate_grain_asserted(broken), "gate_grain_asserted")
    assert not gate.ok
    assert any("grain" in f for f in gate.findings), gate.findings
    assert all("INGEST.json" in f for f in gate.findings), gate.findings


def test_grain_gate_fails_a_grain_that_was_never_verified(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_grain_unverified)
    gate = attempt(lambda: ex.gate_grain_asserted(broken), "gate_grain_asserted")
    assert not gate.ok, (
        "the grain is declared but no verification result is recorded; a grain "
        "nobody checked is a hope with a schema"
    )


# ---------------------------------------------------------------------------
# Exercise 4 -- damage report, not changelog
# ---------------------------------------------------------------------------


def test_damage_gate_passes_four_measured_steps(good):
    gate = attempt(
        lambda: ex.gate_damage_report_quantified(good), "gate_damage_report_quantified"
    )
    assert gate.ok, f"all four cleaning steps carry before/after, but: {gate.findings}"


def test_damage_gate_names_the_step_that_is_only_a_changelog(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_damage_report)
    gate = attempt(
        lambda: ex.gate_damage_report_quantified(broken),
        "gate_damage_report_quantified",
    )
    assert not gate.ok
    assert len(gate.findings) == 1, (
        f"only one of the four steps lost its measurement, so expected one "
        f"finding; got {gate.findings}"
    )
    assert fx.CHANGELOG_STEP in gate.findings[0], (
        f"the finding must name the step {fx.CHANGELOG_STEP!r}; got "
        f"{gate.findings[0]!r}"
    )


# ---------------------------------------------------------------------------
# Exercise 5 -- confirmation set untouched
# ---------------------------------------------------------------------------


def test_confirmation_gate_passes_a_correctly_ordered_log(good):
    gate = attempt(
        lambda: ex.gate_confirmation_untouched(good), "gate_confirmation_untouched"
    )
    assert gate.ok, f"the log opens the confirmation half last, but: {gate.findings}"


def test_confirmation_gate_detects_a_peek(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_confirmation_peeked)
    gate = attempt(
        lambda: ex.gate_confirmation_untouched(broken), "gate_confirmation_untouched"
    )
    assert not gate.ok, (
        "the log shows the confirmation split used at entry 2, before the "
        "hypothesis was declared at entry 4"
    )
    assert any("hypothesis" in f for f in gate.findings), gate.findings


def test_confirmation_gate_reads_only_the_log(good, tmp_path):
    """The peeked study's report and figures are byte-identical to the good
    one. If your gate passes it, you are reading the wrong file."""
    broken = fx.variant(good, tmp_path / "broken", fx.break_confirmation_peeked)
    for name in ("REPORT.md", "FIGURES.json"):
        assert (good / name).read_bytes() == (broken / name).read_bytes()
    gate = attempt(
        lambda: ex.gate_confirmation_untouched(broken), "gate_confirmation_untouched"
    )
    assert not gate.ok


# ---------------------------------------------------------------------------
# Exercise 6 -- uncertainty in the prose
# ---------------------------------------------------------------------------


def test_uncertainty_gate_passes_a_report_with_an_interval(good):
    gate = attempt(
        lambda: ex.gate_uncertainty_reported(good), "gate_uncertainty_reported"
    )
    assert gate.ok, f"the findings carry a 95% CI, but: {gate.findings}"


def test_uncertainty_gate_names_the_sentence(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_uncertainty)
    gate = attempt(
        lambda: ex.gate_uncertainty_reported(broken), "gate_uncertainty_reported"
    )
    assert not gate.ok
    assert len(gate.findings) == 1, gate.findings
    assert "5.50 ug/m3 higher than park stations" in gate.findings[0], (
        f"the finding must quote the offending sentence; got {gate.findings[0]!r}"
    )


@pytest.mark.parametrize(
    "sentence",
    [
        "The mean difference was 5.50 ug/m3 (95% CI 3.80 to 7.21).",
        "The mean difference was 5.50 ug/m3 ±1.70.",
        "The mean difference was 5.50 ug/m3, interval [3.80, 7.21].",
        "The mean difference was anywhere between 3.80 and 7.21 ug/m3.",
    ],
    ids=["ci", "plus-minus", "brackets", "between"],
)
def test_uncertainty_gate_accepts_each_form_of_interval(good, tmp_path, sentence):
    def rewrite(study_dir):
        path = study_dir / "REPORT.md"
        lines = path.read_text().splitlines()
        start = lines.index("## Findings")
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
        body = ["## Findings", "", sentence, ""]
        path.write_text("\n".join(lines[:start] + body + lines[end:]) + "\n")

    probe = fx.variant(good, tmp_path / "probe", rewrite)
    gate = attempt(
        lambda: ex.gate_uncertainty_reported(probe), "gate_uncertainty_reported"
    )
    assert gate.ok, f"this sentence does carry an interval: {sentence!r}"


# ---------------------------------------------------------------------------
# Exercise 7 -- figures carry questions and claims
# ---------------------------------------------------------------------------


def test_figures_gate_passes_two_documented_figures(good):
    gate = attempt(lambda: ex.gate_figures_documented(good), "gate_figures_documented")
    assert gate.ok, f"both figures carry a question and a claim, but: {gate.findings}"


@pytest.mark.parametrize("key", ["claim", "question"])
def test_figures_gate_fails_an_unlabelled_figure(good, tmp_path, key):
    broken = fx.variant(
        good, tmp_path / "broken", lambda d: fx.break_figure_label(d, 0, key)
    )
    gate = attempt(
        lambda: ex.gate_figures_documented(broken), "gate_figures_documented"
    )
    assert not gate.ok
    assert len(gate.findings) == 1, gate.findings
    assert "fig-01-pm25-by-station-type.png" in gate.findings[0], gate.findings
    assert key in gate.findings[0], gate.findings


def test_figures_gate_catches_an_undocumented_file(good, tmp_path):
    broken = fx.variant(good, tmp_path / "broken", fx.break_figure_undocumented)
    gate = attempt(
        lambda: ex.gate_figures_documented(broken), "gate_figures_documented"
    )
    assert not gate.ok, "a figure file with no record is still an undocumented figure"
    assert any("fig-99-leftover.png" in f for f in gate.findings), gate.findings


# ---------------------------------------------------------------------------
# Exercise 8 -- reproducibility
# ---------------------------------------------------------------------------


def test_reproducibility_gate_passes_a_fresh_build(good):
    gate = attempt(
        lambda: ex.gate_outputs_reproducible(good), "gate_outputs_reproducible"
    )
    assert gate.ok, f"every output matches its manifest, but: {gate.findings}"


def test_reproducibility_gate_detects_a_changed_output(good, tmp_path):
    broken = fx.variant(
        good, tmp_path / "broken", fx.break_reproducibility, rewrite_manifest=False
    )
    gate = attempt(
        lambda: ex.gate_outputs_reproducible(broken), "gate_outputs_reproducible"
    )
    assert not gate.ok, "REPORT.md changed after the manifest was written"
    assert any("REPORT.md" in f for f in gate.findings), gate.findings


def test_reproducibility_gate_detects_an_untracked_output(good, tmp_path):
    def add(study_dir):
        (study_dir / "scratch.md").write_text("# scratch\n")

    broken = fx.variant(good, tmp_path / "broken", add, rewrite_manifest=False)
    gate = attempt(
        lambda: ex.gate_outputs_reproducible(broken), "gate_outputs_reproducible"
    )
    assert not gate.ok, "scratch.md is on disk and in no manifest"
    assert any("scratch.md" in f for f in gate.findings), gate.findings


# ---------------------------------------------------------------------------
# Exercise 9 -- the whole harness
# ---------------------------------------------------------------------------


def test_check_study_accepts_the_worked_study(good):
    verdict = attempt(lambda: ex.check_study(good), "check_study")
    assert verdict.ok, f"the worked study should pass every gate: {verdict.findings}"
    assert tuple(g.name for g in verdict.gates) == ex.GATE_NAMES, (
        f"expected the eight gates in order; got "
        f"{tuple(g.name for g in verdict.gates)}"
    )


def test_check_study_raises_on_a_missing_directory(tmp_path):
    try:
        ex.check_study(tmp_path / "nowhere")
    except NotImplementedError:
        pytest.skip("not attempted yet: check_study")
    except FileNotFoundError:
        return
    pytest.fail("check_study must raise FileNotFoundError for a missing directory")


def test_check_study_fails_exactly_one_gate_for_one_missing_element(good, tmp_path):
    def remove_checksum(study_dir):
        path = study_dir / "SOURCE.json"
        payload = json.loads(path.read_text())
        del payload["checksum_sha256"]
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    broken = fx.variant(good, tmp_path / "broken", remove_checksum)
    verdict = attempt(lambda: ex.check_study(broken), "check_study")
    assert verdict.failed_gates == ("provenance_complete",), (
        f"one deleted field should fail one gate; got {verdict.failed_gates}"
    )
    assert verdict.findings == ("SOURCE.json is missing: checksum_sha256",), (
        f"got {verdict.findings}"
    )


def test_check_study_runs_every_gate_rather_than_stopping_at_the_first(good, tmp_path):
    def three(study_dir):
        fx.break_missing_question(study_dir)
        fx.break_grain(study_dir)
        fx.break_figure_label(study_dir, index=1, key="claim")

    broken = fx.variant(good, tmp_path / "broken", three)
    verdict = attempt(lambda: ex.check_study(broken), "check_study")
    assert set(verdict.failed_gates) == {
        "question_recorded",
        "grain_asserted",
        "figures_documented",
    }, f"expected three failed gates; got {verdict.failed_gates}"
