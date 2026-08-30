from typing import Dict, Any, Callable, List, Optional, Tuple

class StateGraphEngine:
    def __init__(self):
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Tuple[Callable[[Dict[str, Any]], str], Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None
        self.checkpoints: List[Dict[str, Any]] = []
        
    def add_node(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.nodes[name] = func
        
    def set_entry_point(self, name: str):
        self.entry_point = name
        
    def add_edge(self, start_node: str, end_node: str):
        self.edges[start_node] = end_node
        
    def add_conditional_edges(self, source_node: str, router_fn: Callable[[Dict[str, Any]], str], route_map: Dict[str, str]):
        self.conditional_edges[source_node] = (router_fn, route_map)
        
    def run(self, initial_state: Dict[str, Any], max_steps: int = 10) -> Dict[str, Any]:
        state = dict(initial_state)
        current_node = self.entry_point
        step = 0
        
        while current_node and current_node != "END":
            step += 1
            if step > max_steps:
                state["error"] = "Max graph execution steps exceeded."
                break
                
            node_fn = self.nodes[current_node]
            update = node_fn(state)
            state.update(update)
            
            # Save checkpoint snapshot
            self.checkpoints.append({
                "step": step,
                "node": current_node,
                "state_snapshot": dict(state)
            })
            
            # Human approval check
            if state.get("requires_human_approval", False) and not state.get("is_approved", False):
                state["status"] = "PAUSED_FOR_HUMAN_APPROVAL"
                state["paused_at_node"] = current_node
                break
                
            # Routing
            if current_node in self.conditional_edges:
                router, rmap = self.conditional_edges[current_node]
                decision = router(state)
                current_node = rmap.get(decision, "END")
            elif current_node in self.edges:
                current_node = self.edges[current_node]
            else:
                current_node = "END"
                
        return state
