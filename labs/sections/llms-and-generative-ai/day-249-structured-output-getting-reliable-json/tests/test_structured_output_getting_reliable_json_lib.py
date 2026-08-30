import pytest
from examples.structured_output_getting_reliable_json_lib import JSONExtractorEngine

def test_json_markdown_cleaning():
    raw = "Sure! Here is the output:\n```json\n{\"status\": \"OK\", \"code\": 200,}\n```"
    data = JSONExtractorEngine.parse_and_validate(raw, required_keys=["status", "code"])

    assert data["status"] == "OK"
    assert data["code"] == 200

def test_auto_closing_truncated_payload():
    raw = "{\"status\": \"PENDING\""
    cleaned = JSONExtractorEngine.clean_json_string(raw)
    assert cleaned.endswith("}")

def test_missing_required_keys():
    raw = "{\"status\": \"OK\"}"
    with pytest.raises(KeyError):
        JSONExtractorEngine.parse_and_validate(raw, required_keys=["status", "missing_field"])
