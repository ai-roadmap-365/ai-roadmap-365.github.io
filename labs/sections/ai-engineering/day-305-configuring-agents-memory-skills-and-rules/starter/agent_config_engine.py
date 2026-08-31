"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
import re
from typing import Dict, Any, List, Optional

class AgentConfigEngine:

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)
        self.skills_dir = os.path.join(self.workspace_root, '.agents', 'skills')
        self.agents_md_path = os.path.join(self.workspace_root, 'AGENTS.md')

    def load_project_rules(self) -> str:
        raise NotImplementedError('TASK 1: implement load_project_rules.')

    def _parse_simple_yaml(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement _parse_simple_yaml.')

    def discover_skills(self) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 3: implement discover_skills.')

    def match_skill(self, user_intent: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError('TASK 4: implement match_skill.')

    def read_skill_content(self, skill_path: str) -> str:
        raise NotImplementedError('TASK 5: implement read_skill_content.')
if __name__ == '__main__':
    engine = AgentConfigEngine('.')
    print('Project Rules Status:', engine.load_project_rules()[:60])
