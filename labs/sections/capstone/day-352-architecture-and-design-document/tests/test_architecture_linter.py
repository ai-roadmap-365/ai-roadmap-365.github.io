import pytest
from examples.architecture_linter import ArchitectureLinter

def test_linter_approves_complete_add():
    linter = ArchitectureLinter()
    complete_doc = (
        "1. System Overview & Problem Statement\n"
        "2. High-Level Component Topology\n"
        "3. Data Flow & Sequence Diagrams\n"
        "4. Data Schemas & Storage Design\n"
        "5. Latency & Resource Budgets\n"
        "6. Failure Mode & Resilience Strategies\n"
        "7. Security & Compliance Architecture\n"
        "The system enforces a circuit breaker with secondary fallback models.\n"
        "The p95 latency budget is 525ms total."
    )
    result = linter.lint_add_document(complete_doc)
    assert result["status"] == "APPROVED"
    assert result["score"] == 100
    assert len(result["errors"]) == 0

def test_missing_sections_rejection():
    linter = ArchitectureLinter()
    incomplete = "1. System Overview & Problem Statement\ncircuit breaker\np95 latency budget"
    result = linter.lint_add_document(incomplete)
    assert result["status"] == "REJECTED"
    assert len(result["missing_sections"]) == 6

def test_missing_circuit_breaker_detection():
    linter = ArchitectureLinter()
    doc_no_cb = (
        "1. System Overview & Problem Statement\n"
        "2. High-Level Component Topology\n"
        "3. Data Flow & Sequence Diagrams\n"
        "4. Data Schemas & Storage Design\n"
        "5. Latency & Resource Budgets\n"
        "6. Failure Mode & Resilience Strategies\n"
        "7. Security & Compliance Architecture\n"
        "p95 latency budget is 500ms."
    )
    result = linter.lint_add_document(doc_no_cb)
    assert any("circuit breaker" in e.lower() for e in result["errors"])
