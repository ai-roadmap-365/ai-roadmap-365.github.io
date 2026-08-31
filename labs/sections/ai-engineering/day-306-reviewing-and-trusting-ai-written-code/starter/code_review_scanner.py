"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import ast
from typing import Dict, Any, List

class AICodeReviewScanner:

    def __init__(self, approved_packages: List[str]):
        self.approved_packages = set(approved_packages)

    def scan_code(self, source_code: str, filename: str='<string>') -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement scan_code.')
if __name__ == '__main__':
    scanner = AICodeReviewScanner(['os', 'sys', 'math', 'pytest'])
    sample = "import os\nos.system('ls')"
    print(scanner.scan_code(sample))
