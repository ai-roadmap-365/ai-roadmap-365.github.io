"""Grouped by concern, so a failure names what is broken.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from corpus import build_corpus  # noqa: E402
from process import (  # noqa: E402
    Document,
    detect,
    format_line,
    process_all,
    process_one,
    score,
)


def by_name(report, name):
    return next(r for r in report.results if r.name == name)


# ------------------------------------------------------------------ detect


def test_detection_reads_content_not_the_extension():
    # Named .scan and .slow -- formats that do not exist. Detection must not
    # care about the name.
    corpus = {d.name: d for d in build_corpus()}
    assert detect(corpus["doc-03.scan"]) == "pdf-scan"
    assert detect(corpus["doc-06.slow"]) == "pathological"
    # A .txt name over undecodable bytes is still unknown.
    assert detect(Document("innocent.txt", bytes([0xFF, 0xFE, 0x00]))) == "unknown"


def test_scan_and_born_digital_pdf_are_distinguished():
    born = Document("a.pdf", b"%PDF-1.7 /Font\nhello world")
    scan = Document("b.pdf", b"%PDF-1.4\n" + b"\x00" * 100)
    assert detect(born) == "pdf"
    assert detect(scan) == "pdf-scan"


# ---------------------------------------------------------------- dispatch


def test_unknown_format_is_dead_lettered_not_raised():
    result = process_one(Document("x.xyz", bytes([0xFF, 0xFE, 0x00, 0x01] * 10)))
    assert result.outcome == "dead"
    assert "no extractor" in result.detail


# ------------------------------------------------------------------ budget


def test_pathological_document_times_out_and_does_not_hang():
    doc = Document("slow.bin", b"SLOW:" + b"x" * 10)
    started = time.monotonic()
    result = process_one(doc, budget_s=0.5)
    elapsed = time.monotonic() - started

    assert result.outcome == "dead"
    assert "timeout" in result.detail
    # The extractor sleeps for 30s; the harness must give up long before.
    assert elapsed < 5.0, f"budget not enforced, took {elapsed:.1f}s"


def test_budget_does_not_stop_the_rest_of_the_run():
    report = process_all(build_corpus(), budget_s=0.3)
    assert by_name(report, "doc-06.slow").outcome == "dead"
    # Everything after the pathological document still processed.
    assert by_name(report, "doc-08.pdf").outcome == "accepted"


# ------------------------------------------------------------------- score


def test_scores_handle_empty_text_without_dividing_by_zero():
    s = score(Document("e.txt", b"abc"), "")
    assert s.text_yield == 0.0
    assert s.alpha_ratio == 0.0
    assert s.mean_word_len == 0.0


def test_yield_is_a_ratio_not_a_length():
    # A genuinely short document is fine; a failed extraction of a big one is
    # not. Only the ratio tells them apart.
    short = score(Document("s.txt", b"hi"), "hi")
    failed = score(Document("b.txt", b"x" * 1000), "hi")
    assert short.text_yield > failed.text_yield
    assert short.text_yield >= 0.9
    assert failed.text_yield < 0.1


def test_alphabetic_ratio_counts_only_letters():
    s = score(Document("m.txt", b"=?#" * 10), "=?#" * 10)
    assert s.alpha_ratio == 0.0


# -------------------------------------------------------------------- gate


def test_scan_is_flagged_by_low_yield_not_by_alphabetic_ratio():
    report = process_all(build_corpus(), budget_s=0.3)
    scan = by_name(report, "doc-03.scan")
    assert scan.outcome == "flagged"
    assert scan.detail == "low text yield"
    # Its letters ARE letters -- only the yield reveals the failure.
    assert scan.scores.alpha_ratio > 0.5


def test_mojibake_is_flagged_by_alphabetic_ratio_not_by_yield():
    report = process_all(build_corpus(), budget_s=0.3)
    junk = by_name(report, "doc-04.bin")
    assert junk.outcome == "flagged"
    assert junk.detail == "low alphabetic ratio"
    # Every byte decoded, so yield is perfect. The mirror image of the scan.
    assert junk.scores.text_yield >= 0.99


def test_flagged_documents_still_carry_their_text():
    # Flagged is not rejected: partial text usually beats none.
    report = process_all(build_corpus(), budget_s=0.3)
    for name in ("doc-03.scan", "doc-04.bin"):
        assert by_name(report, name).text != ""


def test_summary_counts_all_three_outcomes():
    report = process_all(build_corpus(), budget_s=0.3)
    assert report.summary() == "summary: accepted=4 flagged=2 dead=2"
    assert len(report.results) == 8


def test_healthy_documents_are_accepted():
    report = process_all(build_corpus(), budget_s=0.3)
    for name in ("doc-01.txt", "doc-02.pdf", "doc-05.html", "doc-08.pdf"):
        assert by_name(report, name).outcome == "accepted"


def test_format_line_is_stable_for_dead_and_scored_results():
    report = process_all(build_corpus(), budget_s=0.3)
    assert "timeout" in format_line(by_name(report, "doc-06.slow"))
    assert "yield=" in format_line(by_name(report, "doc-01.txt"))
