from typing import Dict, Any, List, Set, Tuple

class GraphRAGEngine:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, str]] = []
        self.community_summaries: Dict[str, Dict[str, str]] = {}
        
    def add_entity(self, entity_id: str, entity_type: str, description: str):
        self.nodes[entity_id] = {
            "type": entity_type,
            "description": description
        }
        
    def add_relationship(self, source: str, relation: str, target: str):
        self.edges.append({
            "source": source,
            "relation": relation,
            "target": target
        })
        
    def register_community_summary(self, community_id: str, title: str, summary_text: str):
        self.community_summaries[community_id] = {
            "title": title,
            "summary": summary_text
        }

    def local_search_multi_hop(self, start_entity: str, max_hops: int = 2) -> Dict[str, Any]:
        if start_entity not in self.nodes:
            return {"status": "ENTITY_NOT_FOUND", "connected_entities": [], "traversed_paths": []}
            
        visited_nodes: Set[str] = {start_entity}
        discovered_paths: List[str] = []
        
        for _ in range(max_hops):
            new_additions = False
            for edge in self.edges:
                if edge["source"] in visited_nodes and edge["target"] not in visited_nodes:
                    path_str = f"{edge['source']} -[{edge['relation']}]-> {edge['target']}"
                    if path_str not in discovered_paths:
                        discovered_paths.append(path_str)
                    visited_nodes.add(edge["target"])
                    new_additions = True
            if not new_additions:
                break
                
        return {
            "status": "SUCCESS",
            "start_entity": start_entity,
            "connected_entities": sorted(list(visited_nodes)),
            "traversed_paths": discovered_paths
        }

    def global_search_communities(self, query: str) -> List[Dict[str, Any]]:
        q_words = set(query.lower().split())
        matched = []
        for c_id, data in self.community_summaries.items():
            words = set(data["summary"].lower().split())
            overlap = len(q_words.intersection(words))
            if overlap > 0:
                matched.append({
                    "community_id": c_id,
                    "title": data["title"],
                    "summary": data["summary"],
                    "relevance_score": overlap
                })
        matched.sort(key=lambda x: x["relevance_score"], reverse=True)
        return matched

if __name__ == "__main__":
    kg = GraphRAGEngine()
    kg.add_entity("A", "Node", "Start")
    kg.add_entity("B", "Node", "Middle")
    kg.add_relationship("A", "LINKS", "B")
    print(kg.local_search_multi_hop("A"))
