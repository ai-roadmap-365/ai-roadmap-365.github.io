"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
import re
import uuid
import hashlib
from typing import Dict, Any, List, Tuple, Optional

class UnifiedAISecurityPlatform:

    def __init__(self, canary_token: Optional[str]=None):
        self.canary_token = canary_token or f'CANARY_{uuid.uuid4().hex[:12].upper()}'
        self.forward_pii_map: Dict[str, str] = {}
        self.reverse_pii_map: Dict[str, str] = {}
        self.pii_counter: int = 0
        self.ssn_re = re.compile('\\b\\d{3}-\\d{2}-\\d{4}\\b')
        self.email_re = re.compile('\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b')
        self.injection_patterns = [re.compile('ignore\\s+(all\\s+)?(previous|prior)\\s+instructions', re.IGNORECASE), re.compile('you\\s+are\\s+now\\s+in\\s+dan\\s+mode', re.IGNORECASE), re.compile('reveal\\s+your\\s+system\\s+prompt', re.IGNORECASE)]

    def sanitize_pii(self, text: str) -> str:
        raise NotImplementedError('TASK 1: implement sanitize_pii.')

    def detokenize_pii(self, text: str) -> str:
        raise NotImplementedError('TASK 2: implement detokenize_pii.')

    def process_ingress_prompt(self, raw_input: str) -> Tuple[bool, str, str]:
        raise NotImplementedError('TASK 3: implement process_ingress_prompt.')

    def process_egress_response(self, raw_response: str) -> Tuple[bool, str]:
        raise NotImplementedError('TASK 4: implement process_egress_response.')

    def verify_model_directory(self, dir_path: str) -> Tuple[bool, List[str]]:
        raise NotImplementedError('TASK 5: implement verify_model_directory.')

    def generate_executive_security_report(self, app_name: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 6: implement generate_executive_security_report.')
if __name__ == '__main__':
    p = UnifiedAISecurityPlatform()
    print(p.generate_executive_security_report('Customer Copilot'))
