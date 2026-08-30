from typing import Dict, Any, List, Optional
import time

class ProviderConfig:
    def __init__(self, name: str, base_url: str, api_key: str, default_model: str, priority: int = 1):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.default_model = default_model
        self.priority = priority

class MultiProviderRouter:
    def __init__(self):
        self.providers: List[ProviderConfig] = []

    def register_provider(self, provider: ProviderConfig) -> "MultiProviderRouter":
        self.providers.append(provider)
        self.providers.sort(key=lambda p: p.priority)
        return self

    def dispatch_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512
    ) -> Dict[str, Any]:
        if not self.providers:
            raise ValueError("No providers registered in router.")

        last_exception = None
        for provider in self.providers:
            try:
                start_time = time.time()
                response = self._execute_provider_call(provider, messages, temperature, max_tokens)
                latency_ms = (time.time() - start_time) * 1000
                response["routed_provider"] = provider.name
                response["latency_ms"] = latency_ms
                return response
            except Exception as err:
                last_exception = err
                continue

        raise RuntimeError(f"All {len(self.providers)} providers failed. Last error: {last_exception}")

    def _execute_provider_call(self, provider: ProviderConfig, messages, temperature, max_tokens):
        if "fail" in provider.name.lower():
            raise ConnectionError(f"Simulated network timeout on {provider.name}")
        return {
            "id": f"chatcmpl_{provider.name}",
            "choices": [{"message": {"role": "assistant", "content": "Routed response success."}}],
            "model": provider.default_model,
            "usage": {"total_tokens": 45}
        }

def run_router_demo():
    router = MultiProviderRouter()
    router.register_provider(ProviderConfig("vLLM_Primary", "http://localhost:8000/v1", "EMPTY", "llama-3.3-70b", priority=1))
    router.register_provider(ProviderConfig("OpenAI_Backup", "https://api.openai.com/v1", "sk-mock", "gpt-4o", priority=2))

    resp = router.dispatch_completion([{"role": "user", "content": "Hello router."}])
    print("Router Demo Executed. Routed provider:", resp["routed_provider"])
    return resp

if __name__ == "__main__":
    run_router_demo()
