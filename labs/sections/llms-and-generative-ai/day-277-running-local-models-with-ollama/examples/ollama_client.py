# Ollama Client, Modelfile Generator, and Local Mock REST Server
import json
from typing import Dict, List, Any, Optional, Iterator

class ModelfileGenerator:
    """Generates and validates declarative Ollama Modelfiles."""

    @staticmethod
    def build_modelfile(
        from_model: str,
        system_prompt: Optional[str] = None,
        template: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        lines = [f"FROM {from_model}"]

        if parameters:
            for key, val in sorted(parameters.items()):
                lines.append(f"PARAMETER {key} {val}")

        if system_prompt:
            cleaned = system_prompt.strip()
            lines.append(f'SYSTEM """{cleaned}"""')

        if template:
            cleaned_tpl = template.strip()
            lines.append(f'TEMPLATE """{cleaned_tpl}"""')

        return "\n".join(lines) + "\n"

    @staticmethod
    def parse_modelfile(content: str) -> Dict[str, Any]:
        """Parses a Modelfile string into structured configuration."""
        config: Dict[str, Any] = {"parameters": {}}
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if line.startswith("FROM "):
                config["from"] = line[5:].strip()
            elif line.startswith("PARAMETER "):
                parts = line[10:].split(maxsplit=1)
                if len(parts) == 2:
                    k, v = parts
                    # Cast types
                    if v.isdigit(): config["parameters"][k] = int(v)
                    else:
                        try: config["parameters"][k] = float(v)
                        except ValueError: config["parameters"][k] = v
            elif line.startswith("SYSTEM "):
                config["system"] = line[7:].strip('"')
            elif line.startswith("TEMPLATE "):
                config["template"] = line[9:].strip('"')

        return config

class MockOllamaServer:
    """Simulates Ollama HTTP REST API streaming responses locally."""

    def __init__(self):
        self.registered_models = {
            "llama3:8b": {"size": 4700000000, "family": "llama"},
            "custom-sql:latest": {"size": 4900000000, "family": "llama"}
        }

    def handle_tags_request(self) -> Dict[str, Any]:
        """Simulates GET /api/tags"""
        models = []
        for name, meta in self.registered_models.items():
            models.append({
                "name": name,
                "size": meta["size"],
                "details": {"family": meta["family"], "parameter_size": "8B", "quantization_level": "Q4_0"}
            })
        return {"models": models}

    def handle_generate_stream(self, model: str, prompt: str) -> Iterator[str]:
        """Simulates POST /api/generate NDJSON streaming."""
        if model not in self.registered_models:
            yield json.dumps({"error": f"model '{model}' not found"}) + "\n"
            return

        mock_words = f"Response to '{prompt[:20]}': SELECT * FROM database;".split()
        for word in mock_words:
            chunk = {
                "model": model,
                "response": word + " ",
                "done": False
            }
            yield json.dumps(chunk) + "\n"

        # Final chunk
        final_chunk = {
            "model": model,
            "response": "",
            "done": True,
            "total_duration": 120000000,
            "eval_count": len(mock_words),
            "eval_duration": 100000000
        }
        yield json.dumps(final_chunk) + "\n"

class OllamaClient:
    """Client library for communicating with Ollama REST API."""

    def __init__(self, server: MockOllamaServer):
        self.server = server

    def list_models(self) -> List[str]:
        data = self.server.handle_tags_request()
        return [m["name"] for m in data["models"]]

    def generate(self, model: str, prompt: str) -> Dict[str, Any]:
        full_text = []
        eval_count = 0
        total_duration = 0

        for line in self.server.handle_generate_stream(model, prompt):
            chunk = json.loads(line.strip())
            if "error" in chunk:
                raise ValueError(chunk["error"])
            full_text.append(chunk.get("response", ""))
            if chunk.get("done", False):
                eval_count = chunk.get("eval_count", 0)
                total_duration = chunk.get("total_duration", 0)

        return {
            "response": "".join(full_text).strip(),
            "eval_count": eval_count,
            "total_duration_ms": total_duration / 1_000_000.0
        }
