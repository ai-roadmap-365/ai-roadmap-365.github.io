"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import re
from typing import Dict, Any, Tuple

class GuardrailEngine:
    SSN_PATTERN = '\\b\\d{3}-\\d{2}-\\d{4}\\b'
    EMAIL_PATTERN = '\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
    CREDIT_CARD_PATTERN = '\\b(?:\\d{4}[-\\s]?){3}\\d{4}\\b'
    INJECTION_KEYWORDS = ['ignore previous instructions', 'ignore all previous rules', 'system prompt', 'you are now dan', 'bypass security', 'print your prompt']

    @classmethod
    def redact_pii(cls, text: str) -> Tuple[str, Dict[str, int]]:
        raise NotImplementedError('TASK 1: implement redact_pii.')

    @classmethod
    def detect_prompt_injection(cls, text: str) -> bool:
        raise NotImplementedError('TASK 2: implement detect_prompt_injection.')

    @classmethod
    def process_input(cls, user_text: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement process_input.')
if __name__ == '__main__':
    guard = GuardrailEngine()
    print('Test:', guard.process_input('My SSN is 000-11-2222.'))
