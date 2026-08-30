import time
from typing import Dict, Any, List, Optional

class VendorFallbackRouter:
    def __init__(self):
        self.providers: Dict[str, Dict[str, Any]] = {
            "anthropic": {"name": "Anthropic Claude 3.5", "healthy": True, "consecutive_fails": 0},
            "openai": {"name": "OpenAI GPT-4o", "healthy": True, "consecutive_fails": 0},
            "vllm_local": {"name": "Self-Hosted Llama 3.3", "healthy": True, "consecutive_fails": 0}
        }
        self.priority_order = ["anthropic", "openai", "vllm_local"]
        
    def set_provider_health(self, provider_id: str, healthy: bool):
        if provider_id in self.providers:
            self.providers[provider_id]["healthy"] = bool(healthy)
            
    def call_model_with_fallback(self, prompt: str, simulated_failing_providers: Optional[List[str]] = None) -> Dict[str, Any]:
        failing = set(simulated_failing_providers or [])
        attempted_providers = []
        
        for provider_id in self.priority_order:
            provider = self.providers[provider_id]
            attempted_providers.append(provider_id)
            
            if not provider["healthy"] or provider_id in failing:
                provider["consecutive_fails"] += 1
                continue
                
            provider["consecutive_fails"] = 0
            return {
                "status": "SUCCESS",
                "resolved_provider": provider_id,
                "provider_name": provider["name"],
                "response": f"[{provider['name']}] Completed: {prompt}",
                "attempted_providers": attempted_providers,
                "fallback_occurred": len(attempted_providers) > 1
            }
            
        return {
            "status": "ALL_PROVIDERS_FAILED",
            "attempted_providers": attempted_providers,
            "error": "503 All upstream model providers are unavailable"
        }

if __name__ == "__main__":
    router = VendorFallbackRouter()
    print("Normal:", router.call_model_with_fallback("Hello"))
