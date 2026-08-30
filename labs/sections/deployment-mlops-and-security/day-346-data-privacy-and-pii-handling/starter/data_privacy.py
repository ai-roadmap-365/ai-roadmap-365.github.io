import re
import math
import random
from typing import Dict, Any, Tuple, List

class DifferentialPrivacyEngine:
    @staticmethod
    def laplace_mechanism(true_value: float, sensitivity: float, epsilon: float) -> float:
        if epsilon <= 0:
            raise ValueError("Epsilon privacy budget must be strictly positive.")
        scale = sensitivity / epsilon
        u = random.random() - 0.5
        noise = -scale * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))
        return round(true_value + noise, 4)

class PIITokenVault:
    def __init__(self):
        self.forward_map: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
        self.entity_counters: Dict[str, int] = {"PERSON": 0, "SSN": 0, "EMAIL": 0, "CREDIT_CARD": 0}
        
        self.ssn_pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.cc_pattern = re.compile(r"\b(?:\d{4}-){3}\d{4}\b")

    def tokenize_text(self, text: str) -> str:
        tokenized = text

        for match in self.ssn_pattern.findall(text):
            if match not in self.forward_map:
                self.entity_counters["SSN"] += 1
                token = f"<SSN_{self.entity_counters['SSN']}>"
                self.forward_map[match] = token
                self.reverse_map[token] = match
            tokenized = tokenized.replace(match, self.forward_map[match])

        for match in self.email_pattern.findall(text):
            if match not in self.forward_map:
                self.entity_counters["EMAIL"] += 1
                token = f"<EMAIL_{self.entity_counters['EMAIL']}>"
                self.forward_map[match] = token
                self.reverse_map[token] = match
            tokenized = tokenized.replace(match, self.forward_map[match])

        for match in self.cc_pattern.findall(text):
            if match not in self.forward_map:
                self.entity_counters["CREDIT_CARD"] += 1
                token = f"<CREDIT_CARD_{self.entity_counters['CREDIT_CARD']}>"
                self.forward_map[match] = token
                self.reverse_map[token] = match
            tokenized = tokenized.replace(match, self.forward_map[match])

        return tokenized

    def detokenize_text(self, text: str) -> str:
        detokenized = text
        for token, raw_val in self.reverse_map.items():
            detokenized = detokenized.replace(token, raw_val)
        return detokenized

    def forget_user_pii(self, raw_pii_value: str) -> bool:
        if raw_pii_value in self.forward_map:
            token = self.forward_map[raw_pii_value]
            del self.forward_map[raw_pii_value]
            del self.reverse_map[token]
            return True
        return False

if __name__ == "__main__":
    v = PIITokenVault()
    print(v.tokenize_text("Test email is test@domain.com"))
