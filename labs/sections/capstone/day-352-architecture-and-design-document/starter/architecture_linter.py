"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import Dict, Any, List

class ArchitectureLinter:

    def __init__(self):
        self.required_sections = ['1. System Overview & Problem Statement', '2. High-Level Component Topology', '3. Data Flow & Sequence Diagrams', '4. Data Schemas & Storage Design', '5. Latency & Resource Budgets', '6. Failure Mode & Resilience Strategies', '7. Security & Compliance Architecture']

    def lint_add_document(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement lint_add_document.')
if __name__ == '__main__':
    linter = ArchitectureLinter()
    print(linter.lint_add_document('Sample ADD text'))
