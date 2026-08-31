"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import re
import math
import random
from typing import Dict, Any, Tuple, List

class DifferentialPrivacyEngine:

    @staticmethod
    def laplace_mechanism(true_value: float, sensitivity: float, epsilon: float) -> float:
        raise NotImplementedError('TASK 1: implement laplace_mechanism.')

class PIITokenVault:

    def __init__(self):
        self.forward_map: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
        self.entity_counters: Dict[str, int] = {'PERSON': 0, 'SSN': 0, 'EMAIL': 0, 'CREDIT_CARD': 0}
        self.ssn_pattern = re.compile('\\b\\d{3}-\\d{2}-\\d{4}\\b')
        self.email_pattern = re.compile('\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b')
        self.cc_pattern = re.compile('\\b(?:\\d{4}-){3}\\d{4}\\b')

    def tokenize_text(self, text: str) -> str:
        raise NotImplementedError('TASK 2: implement tokenize_text.')

    def detokenize_text(self, text: str) -> str:
        raise NotImplementedError('TASK 3: implement detokenize_text.')

    def forget_user_pii(self, raw_pii_value: str) -> bool:
        raise NotImplementedError('TASK 4: implement forget_user_pii.')
if __name__ == '__main__':
    v = PIITokenVault()
    print(v.tokenize_text('Test email is test@domain.com'))
