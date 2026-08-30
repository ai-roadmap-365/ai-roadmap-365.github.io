import json
import re
from typing import Dict, Any, Optional

class JSONExtractorEngine:
    @staticmethod
    def clean_json_string(raw_text: str) -> str:
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        first_brace = cleaned.find("{")
        first_bracket = cleaned.find("[")

        if first_brace == -1 and first_bracket == -1:
            raise ValueError("No JSON object or array delimiter found in response.")

        if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
            start_idx = first_brace
            end_idx = cleaned.rfind("}")
            if end_idx != -1:
                cleaned = cleaned[start_idx:end_idx + 1]
            else:
                cleaned = cleaned[start_idx:] + "}"
        else:
            start_idx = first_bracket
            end_idx = cleaned.rfind("]")
            if end_idx != -1:
                cleaned = cleaned[start_idx:end_idx + 1]
            else:
                cleaned = cleaned[start_idx:] + "]"

        cleaned = re.sub(r",\s*([\}\]])", r"\1", cleaned)
        return cleaned.strip()

    @classmethod
    def parse_and_validate(cls, raw_text: str, required_keys: Optional[list] = None) -> Dict[str, Any]:
        cleaned = cls.clean_json_string(raw_text)
        data = json.loads(cleaned)

        if required_keys and isinstance(data, dict):
            missing = [k for k in required_keys if k not in data]
            if missing:
                raise KeyError(f"Missing required schema keys: {missing}")

        return data

def run_json_demo():
    raw_payload = "Sure! Here is the data: ```json\n{\"incident_id\": \"INC-101\", \"severity\": \"HIGH\",}\n```"
    result = JSONExtractorEngine.parse_and_validate(raw_payload, required_keys=["incident_id", "severity"])

    print("JSON Demo Extracted Successfully:", result["incident_id"])
    return result

if __name__ == "__main__":
    run_json_demo()
