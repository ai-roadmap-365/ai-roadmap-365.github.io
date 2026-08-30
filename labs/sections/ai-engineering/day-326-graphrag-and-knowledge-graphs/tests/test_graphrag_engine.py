import pytest
from examples.graphrag_engine import GraphRAGEngine

def test_add_entities_and_relationships():
    kg = GraphRAGEngine()
    kg.add_entity("PostgreSQL", "Database", "Relational database")
    kg.add_entity("WAL", "Buffer", "Write ahead log")
    kg.add_relationship("PostgreSQL", "WRITES_TO", "WAL")
    
    assert "PostgreSQL" in kg.nodes
    assert len(kg.edges) == 1
    assert kg.edges[0]["relation"] == "WRITES_TO"

def test_local_multi_hop_traversal():
    kg = GraphRAGEngine()
    kg.add_entity("ServiceA", "Microservice", "Frontend API")
    kg.add_entity("ServiceB", "Microservice", "Billing API")
    kg.add_entity("DatabaseC", "Storage", "PostgreSQL DB")
    
    kg.add_relationship("ServiceA", "CALLS", "ServiceB")
    kg.add_relationship("ServiceB", "QUERIES", "DatabaseC")
    
    res = kg.local_search_multi_hop("ServiceA", max_hops=2)
    assert res["status"] == "SUCCESS"
    assert "DatabaseC" in res["connected_entities"]
    assert len(res["traversed_paths"]) == 2
    assert "ServiceA -[CALLS]-> ServiceB" in res["traversed_paths"]

def test_unknown_start_entity():
    kg = GraphRAGEngine()
    res = kg.local_search_multi_hop("NonExistentEntity")
    assert res["status"] == "ENTITY_NOT_FOUND"
    assert res["connected_entities"] == []

def test_global_community_search():
    kg = GraphRAGEngine()
    kg.register_community_summary("C0", "Infrastructure", "Kubernetes cluster orchestration and pod scheduling policies.")
    kg.register_community_summary("C1", "Billing", "Stripe metered billing credit accounting system.")
    
    res = kg.global_search_communities("Kubernetes pod scheduling")
    assert len(res) >= 1
    assert res[0]["community_id"] == "C0"
    assert res[0]["title"] == "Infrastructure"

def test_global_search_no_match():
    kg = GraphRAGEngine()
    kg.register_community_summary("C0", "Title", "Some summary text")
    res = kg.global_search_communities("completely unrelated aerospace terms")
    assert res == []
