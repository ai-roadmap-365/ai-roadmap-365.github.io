import numpy as np
import heapq
from typing import List, Dict, Any, Tuple, Set

class SimpleNSWIndex:
    def __init__(self, dimension: int, max_neighbors: int = 4):
        self.dimension = dimension
        self.max_neighbors = max_neighbors
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict[str, Any]] = []
        self.graph: Dict[int, List[int]] = {}
        self.entry_node: int = 0

    def add_document(self, vector: np.ndarray, meta: Dict[str, Any]) -> int:
        norm = np.linalg.norm(vector)
        unit_vec = vector / (norm if norm > 0 else 1.0)
        node_id = len(self.vectors)
        self.vectors.append(unit_vec)
        self.metadata.append(meta)
        self.graph[node_id] = []

        if node_id == 0:
            self.entry_node = 0
            return node_id

        # Find closest existing nodes to establish bidirectional links
        closest = self.search(unit_vec, top_k=self.max_neighbors, ef_search=max(self.max_neighbors, 8))
        for target_meta, _ in closest:
            target_id = target_meta["id"]
            if target_id not in self.graph[node_id]:
                self.graph[node_id].append(target_id)
            if len(self.graph[target_id]) < self.max_neighbors * 2 and node_id not in self.graph[target_id]:
                self.graph[target_id].append(node_id)
        return node_id

    def search(self, query_vec: np.ndarray, top_k: int = 3, ef_search: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        if not self.vectors:
            return []
        
        q_norm = np.linalg.norm(query_vec)
        q_unit = query_vec / (q_norm if q_norm > 0 else 1.0)

        visited: Set[int] = {self.entry_node}
        candidates = [(-float(np.dot(self.vectors[self.entry_node], q_unit)), self.entry_node)]
        best_results = [(-candidates[0][0], self.entry_node)]

        while candidates:
            dist, curr = heapq.heappop(candidates)
            curr_sim = -dist
            if curr_sim < best_results[-1][0] and len(best_results) >= ef_search:
                break
            
            for neighbor in self.graph.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    sim = float(np.dot(self.vectors[neighbor], q_unit))
                    if len(best_results) < ef_search or sim > best_results[-1][0]:
                        heapq.heappush(candidates, (-sim, neighbor))
                        best_results.append((sim, neighbor))
                        best_results.sort(key=lambda x: x[0], reverse=True)
                        if len(best_results) > ef_search:
                            best_results.pop()

        return [(self.metadata[node_id], sim) for sim, node_id in best_results[:top_k]]

def run_nsw_demo():
    index = SimpleNSWIndex(dimension=3, max_neighbors=2)
    v0 = np.array([1.0, 0.0, 0.0])
    v1 = np.array([0.9, 0.1, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    index.add_document(v0, {"id": 0, "title": "Doc 0"})
    index.add_document(v1, {"id": 1, "title": "Doc 1"})
    index.add_document(v2, {"id": 2, "title": "Doc 2"})

    query = np.array([1.0, 0.0, 0.0])
    results = index.search(query, top_k=2)
    print(f"NSW Demo Executed. Top Match: {results[0][0]['title']} with score {results[0][1]:.4f}")
    return results

if __name__ == "__main__":
    run_nsw_demo()
