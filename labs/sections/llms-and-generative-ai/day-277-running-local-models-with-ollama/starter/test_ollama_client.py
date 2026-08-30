import pytest
import json
from ollama_client import ModelfileGenerator, MockOllamaServer, OllamaClient

def test_modelfile_builder_and_parser():
    modelfile = ModelfileGenerator.build_modelfile(
        from_model="./custom_model.gguf",
        system_prompt="You are a SQL expert.",
        parameters={"temperature": 0.2, "num_ctx": 4096}
    )
    assert "FROM ./custom_model.gguf" in modelfile
    assert "PARAMETER num_ctx 4096" in modelfile
    assert 'SYSTEM """You are a SQL expert."""' in modelfile

    parsed = ModelfileGenerator.parse_modelfile(modelfile)
    assert parsed["from"] == "./custom_model.gguf"
    assert parsed["parameters"]["temperature"] == 0.2
    assert parsed["parameters"]["num_ctx"] == 4096

def test_mock_server_tags_endpoint():
    server = MockOllamaServer()
    tags = server.handle_tags_request()
    model_names = [m["name"] for m in tags["models"]]
    assert "llama3:8b" in model_names
    assert "custom-sql:latest" in model_names

def test_streaming_generation():
    server = MockOllamaServer()
    client = OllamaClient(server)
    
    res = client.generate("llama3:8b", "Write a query")
    assert "SELECT * FROM database;" in res["response"]
    assert res["eval_count"] > 0
    assert res["total_duration_ms"] == 120.0

def test_model_not_found_error():
    server = MockOllamaServer()
    client = OllamaClient(server)
    with pytest.raises(ValueError, match="not found"):
        client.generate("non-existent-model", "Hello")

def test_client_list_models():
    server = MockOllamaServer()
    client = OllamaClient(server)
    models = client.list_models()
    assert len(models) >= 2
    assert "llama3:8b" in models
