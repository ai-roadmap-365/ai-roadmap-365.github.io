import re
from typing import Dict, Any, Tuple

class GuardrailEngine:
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    CREDIT_CARD_PATTERN = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    
    INJECTION_KEYWORDS = [
        "ignore previous instructions",
        "ignore all previous rules",
        "system prompt",
        "you are now dan",
        "bypass security",
        "print your prompt"
    ]
    
    @classmethod
    def redact_pii(cls, text: str) -> Tuple[str, Dict[str, int]]:
        redacted = text
        counts = {"ssn": 0, "email": 0, "credit_card": 0}
        
        ssn_matches = re.findall(cls.SSN_PATTERN, redacted)
        if ssn_matches:
            counts["ssn"] = len(ssn_matches)
            redacted = re.sub(cls.SSN_PATTERN, "[REDACTED_SSN]", redacted)
            
        email_matches = re.findall(cls.EMAIL_PATTERN, redacted)
        if email_matches:
            counts["email"] = len(email_matches)
            redacted = re.sub(cls.EMAIL_PATTERN, "[REDACTED_EMAIL]", redacted)
            
        cc_matches = re.findall(cls.CREDIT_CARD_PATTERN, redacted)
        if cc_matches:
            counts["credit_card"] = len(cc_matches)
            redacted = re.sub(cls.CREDIT_CARD_PATTERN, "[REDACTED_CREDIT_CARD]", redacted)
            
        return redacted, counts

    @classmethod
    def detect_prompt_injection(cls, text: str) -> bool:
        norm_text = text.lower()
        for kw in cls.INJECTION_KEYWORDS:
            if kw in norm_text:
                return True
        return False

    @classmethod
    def process_input(cls, user_text: str) -> Dict[str, Any]:
        if not user_text or not user_text.strip():
            return {
                "allowed": False,
                "sanitized_text": "",
                "reason": "EMPTY_INPUT",
                "fallback_response": "Input text cannot be empty."
            }
            
        if cls.detect_prompt_injection(user_text):
            return {
                "allowed": False,
                "sanitized_text": "",
                "reason": "PROMPT_INJECTION_DETECTED",
                "fallback_response": "I cannot fulfill this request as it violates safety guidelines."
            }
            
        sanitized, pii_counts = cls.redact_pii(user_text)
        return {
            "allowed": True,
            "sanitized_text": sanitized,
            "pii_redacted": pii_counts,
            "reason": "PASSED_GUARDRAILS",
            "fallback_response": None
        }

if __name__ == "__main__":
    guard = GuardrailEngine()
    print("Test:", guard.process_input("My SSN is 000-11-2222."))
