# Starter: Ollama Client and Modelfile Generator
from typing import Dict, List, Any, Optional

class ModelfileGenerator:
    @staticmethod
    def build_modelfile(
        from_model: str,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        return f"FROM {from_model}\n"

class MockOllamaServer:
    def handle_tags_request(self) -> Dict[str, Any]:
        return {"models": []}

class OllamaClient:
    def __init__(self, server: MockOllamaServer):
        self.server = server

    def list_models(self) -> List[str]:
        return []

    def generate(self, model: str, prompt: str) -> Dict[str, Any]:
        return {"response": "", "eval_count": 0, "total_duration_ms": 0.0}
