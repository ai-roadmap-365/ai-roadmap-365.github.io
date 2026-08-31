"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import re
import uuid
from typing import Dict, Any, Tuple, Optional

class PromptDefenseFirewall:

    def __init__(self, canary_token: Optional[str]=None):
        self.canary_token = canary_token or f'CANARY_{uuid.uuid4().hex[:12].upper()}'
        self.injection_patterns = [re.compile('ignore\\s+(all\\s+)?(previous|prior)\\s+instructions', re.IGNORECASE), re.compile('system\\s+prompt\\s+override', re.IGNORECASE), re.compile('you\\s+are\\s+now\\s+in\\s+dan\\s+mode', re.IGNORECASE), re.compile('reveal\\s+your\\s+(secret\\s+)?instructions', re.IGNORECASE), re.compile('disregard\\s+all\\s+safety', re.IGNORECASE)]

    def sanitize_and_wrap_input(self, user_input: str) -> Tuple[bool, str, str]:
        raise NotImplementedError('TASK 1: implement sanitize_and_wrap_input.')

    def inspect_outbound_response(self, response_text: str) -> Tuple[bool, str]:
        raise NotImplementedError('TASK 2: implement inspect_outbound_response.')
if __name__ == '__main__':
    fw = PromptDefenseFirewall()
    print(fw.sanitize_and_wrap_input('Hello, world!'))
