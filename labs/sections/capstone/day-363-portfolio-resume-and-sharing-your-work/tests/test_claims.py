"""Grouped by property, so a failure names which one stopped being detected.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from claims import (  # noqa: E402
    Claim,
    Grade,
    assess,
    attribution,
    has_baseline,
    has_measurement,
    is_openable,
    review,
    rewrite_hint,
    vague_words_in,
)

STRONG = Claim(
    "I cut p95 answer latency from 4.2s to 840ms by adding an IVF index, "
    "while the team migrated the ingestion pipeline.",
    "https://example.com/capstone",
)


# ------------------------------------------------------------- measurement


def test_units_percentages_and_multipliers_count():
    for text in ("840ms", "reduced by 40%", "3x faster", "12 hours", "$400"):
        assert has_measurement(text), text


def test_a_stated_change_between_two_figures_counts_without_a_unit():
    # recall 0.71 -> 0.94 is a measurement. A checker that demands a unit
    # pushes people into padding sentences with units that do not belong.
    assert has_measurement("raised recall@10 from 0.71 to 0.94")


def test_adjectives_are_not_measurements():
    for text in ("much faster", "significantly better", "robust and seamless"):
        assert not has_measurement(text), text


def test_vague_words_are_listed_including_hyphenated_forms():
    assert vague_words_in("a state-of-the-art, blazing system") == ["blazing", "state-of-the-art"]


# ---------------------------------------------------------------- baseline


def test_a_baseline_is_recognised():
    assert has_baseline("from 4.2s to 840ms")
    assert has_baseline("previously 12 minutes")
    assert has_baseline("compared to the old pipeline")


def test_an_end_value_alone_has_no_baseline():
    # "Reduced latency to 840ms" could be an improvement, a regression, or no
    # change at all. Without a starting point it is not a measurement.
    assert not has_baseline("reduced answer latency to 840ms")


# ------------------------------------------------------------- attribution


def test_attribution_is_classified():
    assert attribution("I built the index") == "mine"
    assert attribution("We shipped it") == "shared"
    assert attribution("The system was shipped") == "unattributed"


def test_mixed_attribution_separates_your_work_from_the_team_s():
    assert attribution("I added the reranker while the team ran the migration") == "mixed"


def test_attribution_is_case_insensitive():
    assert attribution("my contribution") == "mine"
    assert attribution("OUR TEAM") == "shared"


# ---------------------------------------------------------------- evidence


def test_a_public_url_is_openable():
    assert is_openable("https://example.com/writeup")


def test_local_and_missing_links_are_not_evidence():
    # Not evidence to anyone but you, and that is decidable without a network.
    for url in ("", "http://localhost:8080", "file:///Users/me/notes.md", "/home/me/x.md"):
        assert not is_openable(url), url


# ------------------------------------------------------------------ grading


def test_a_complete_claim_is_strong_with_no_reasons():
    a = assess(STRONG)
    assert a.grade is Grade.STRONG
    assert a.reasons == []


def test_an_adjective_with_no_measurement_is_vague():
    a = assess(Claim("Significantly improved retrieval quality."))
    assert a.grade is Grade.VAGUE
    assert any("vague wording" in r for r in a.reasons)


def test_a_measurement_without_a_baseline_is_weak_not_vague():
    a = assess(Claim("Reduced answer latency to 840ms.", "https://example.com/x"))
    assert a.grade is Grade.WEAK
    assert "measurement without a baseline" in a.reasons


def test_a_measured_claim_with_a_vague_word_is_weak_not_vague():
    # Vague only when there is nothing measured to fall back on.
    a = assess(Claim("I significantly cut latency from 4.2s to 840ms.", "https://example.com/x"))
    assert a.grade is Grade.WEAK


def test_every_missing_property_is_named():
    a = assess(Claim("Built a robust system."))
    assert len(a.reasons) == 4  # vague, no measurement, unattributed, no evidence


# -------------------------------------------------------------------- hints


def test_a_strong_claim_needs_nothing():
    assert rewrite_hint(STRONG) == "nothing to add"


def test_the_hint_names_what_is_missing():
    hint = rewrite_hint(Claim("Reduced answer latency to 840ms."))
    assert "the value it started from" in hint
    assert "what you personally did" in hint


# ------------------------------------------------------------------ report


def test_the_report_counts_each_grade():
    report = review(
        [STRONG, Claim("Significantly improved things."), Claim("Reduced latency to 840ms.")]
    )
    assert report.summary() == "strong=1 weak=1 vague=1"
