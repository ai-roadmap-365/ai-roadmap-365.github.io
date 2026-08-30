from typing import Dict, Any, List, Tuple, Optional

class SpeculativeDecodingEngine:
    def __init__(self, acceptance_probability_bias: float = 0.80):
        self.alpha_bias = float(acceptance_probability_bias)
        self.prefix_cache: Dict[str, str] = {}
        
    def register_prefix_cache(self, prefix_key: str, cached_kv_id: str):
        self.prefix_cache[prefix_key] = cached_kv_id

    def lookup_prefix(self, prompt: str) -> Tuple[bool, str]:
        for k, v in self.prefix_cache.items():
            if prompt.startswith(k):
                return True, v
        return False, "CACHE_MISS"

    def execute_speculative_step(
        self,
        draft_tokens: List[str],
        target_ground_truth: List[str]
    ) -> Dict[str, Any]:
        accepted = []
        rejected_at_index = None
        
        for i, token in enumerate(draft_tokens):
            if i < len(target_ground_truth) and token == target_ground_truth[i]:
                accepted.append(token)
            else:
                rejected_at_index = i
                replacement = target_ground_truth[i] if i < len(target_ground_truth) else "<EOS>"
                accepted.append(replacement)
                break
                
        accepted_draft_count = len(draft_tokens) if rejected_at_index is None else rejected_at_index
        
        if rejected_at_index is None and len(accepted) < len(target_ground_truth):
            bonus_token = target_ground_truth[len(accepted)]
            accepted.append(bonus_token)
            
        total_yield = len(accepted)
        speedup = round(total_yield / 1.0, 2)
        
        return {
            "draft_tokens": draft_tokens,
            "emitted_tokens": accepted,
            "accepted_count": accepted_draft_count,
            "speedup_factor": speedup,
            "rejected_index": rejected_at_index
        }

if __name__ == "__main__":
    eng = SpeculativeDecodingEngine()
    eng.register_prefix_cache("System Prompt", "kv_0")
    print(eng.lookup_prefix("System Prompt: do task"))
    print(eng.execute_speculative_step(["a", "b"], ["a", "b", "c"]))
