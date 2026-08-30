import pytest
import time
from examples.audit import Milestone1AuditSuite

def test_latency_profiling_compliance():
    auditor = Milestone1AuditSuite(max_latency_ms=1500.0)
    def fast_pipeline():
        return {"retrieval": 10.0, "llm": 20.0}, {"schema_valid": True}
    
    profile = auditor.profile_vertical_slice(fast_pipeline)
    assert profile["latency_compliant"] is True
    assert profile["total_latency_ms"] < 1500.0
    assert "retrieval" in profile["component_breakdown_ms"]

def test_milestone_approval_on_healthy_system():
    auditor = Milestone1AuditSuite()
    def healthy_pipe():
        return {"all": 15.0}, {"schema_valid": True, "answer": "OK"}
    
    report = auditor.audit_milestone(healthy_pipe, {"faithfulness": 0.95, "recall": 0.90})
    assert report["overall_status"] == "APPROVED"
    assert report["checks"]["latency_budget"] == "PASS"
    assert report["checks"]["faithfulness_accuracy"] == "PASS"
    assert report["checks"]["schema_integrity"] == "PASS"

def test_milestone_rejection_on_low_accuracy():
    auditor = Milestone1AuditSuite(min_faithfulness=0.90)
    def healthy_pipe():
        return {"all": 15.0}, {"schema_valid": True}
    
    report = auditor.audit_milestone(healthy_pipe, {"faithfulness": 0.75})
    assert report["overall_status"] == "REJECTED"
    assert report["checks"]["faithfulness_accuracy"] == "FAIL"

def test_milestone_rejection_on_schema_invalid():
    auditor = Milestone1AuditSuite()
    def broken_schema_pipe():
        return {"all": 10.0}, {"schema_valid": False}
    
    report = auditor.audit_milestone(broken_schema_pipe, {"faithfulness": 0.95})
    assert report["overall_status"] == "REJECTED"
    assert report["checks"]["schema_integrity"] == "FAIL"

def test_milestone_rejection_on_latency_exceeded():
    auditor = Milestone1AuditSuite(max_latency_ms=1.0)
    def slow_pipe():
        time.sleep(0.01) # 10ms > 1.0ms budget
        return {}, {"schema_valid": True}
    
    report = auditor.audit_milestone(slow_pipe, {"faithfulness": 0.95})
    assert report["checks"]["latency_budget"] == "FAIL"
    assert report["overall_status"] == "REJECTED"
