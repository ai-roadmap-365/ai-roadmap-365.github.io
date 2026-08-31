"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Optional

class NoteStore:

    def __init__(self):
        self.notes: List[Dict[str, Any]] = []

    def add_note(self, claim: str, source_title: str, url: str) -> int:
        raise NotImplementedError('TASK 1: implement add_note.')

    def get_all(self) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 2: implement get_all.')

class AutonomousResearchAgent:

    def __init__(self, search_kb: Optional[Dict[str, List[Dict[str, str]]]]=None):
        self.note_store = NoteStore()
        self.kb = search_kb or {'solid state energy density': [{'title': 'Nature Energy 2025', 'url': 'https://nature.com/art1', 'snippet': 'Prototypes achieved 450 Wh/kg gravimetric density.'}, {'title': 'Battery Journal', 'url': 'https://batteryj.org/art2', 'snippet': 'Cycle life reached 1200 cycles at C/3 charge rate.'}], 'solid state manufacturing cost': [{'title': 'BloombergNEF EV Report', 'url': 'https://bnef.com/ev2025', 'snippet': 'Cell-level costs projected at $95/kWh by 2028.'}]}

    def decompose_query(self, topic: str) -> List[str]:
        raise NotImplementedError('TASK 3: implement decompose_query.')

    def search_and_extract(self, query: str):
        raise NotImplementedError('TASK 4: implement search_and_extract.')

    def synthesize_brief(self, topic: str) -> str:
        raise NotImplementedError('TASK 5: implement synthesize_brief.')

    def execute_research(self, topic: str) -> str:
        raise NotImplementedError('TASK 6: implement execute_research.')
if __name__ == '__main__':
    agent = AutonomousResearchAgent()
    brief = agent.execute_research('Solid-State Batteries')
    print(brief)
