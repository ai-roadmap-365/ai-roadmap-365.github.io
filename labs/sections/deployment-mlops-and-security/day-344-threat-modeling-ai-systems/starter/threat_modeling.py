"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Optional

class AIThreatModelScorer:

    def __init__(self):
        self.identified_threats: List[Dict[str, Any]] = []

    def add_threat(self, threat_id: str, title: str, category_stride: str, owasp_id: str, damage: int, reproducibility: int, exploitability: int, affected_users: int, discoverability: int, description: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement add_threat.')

    def get_prioritized_remediation_plan(self) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 2: implement get_prioritized_remediation_plan.')
if __name__ == '__main__':
    s = AIThreatModelScorer()
    print(s.add_threat('T1', 'Prompt Injection', 'Elevation', 'LLM01', 9, 8, 8, 9, 8, 'Test'))
