from typing import Dict, Any, List, Optional

class NoteStore:
    def __init__(self):
        self.notes: List[Dict[str, Any]] = []
        
    def add_note(self, claim: str, source_title: str, url: str) -> int:
        for n in self.notes:
            if n["claim"] == claim and n["url"] == url:
                return n["id"]
        note_id = len(self.notes) + 1
        self.notes.append({
            "id": note_id,
            "claim": claim,
            "title": source_title,
            "url": url
        })
        return note_id
        
    def get_all(self) -> List[Dict[str, Any]]:
        return self.notes

class AutonomousResearchAgent:
    def __init__(self, search_kb: Optional[Dict[str, List[Dict[str, str]]]] = None):
        self.note_store = NoteStore()
        self.kb = search_kb or {
            "solid state energy density": [
                {"title": "Nature Energy 2025", "url": "https://nature.com/art1", "snippet": "Prototypes achieved 450 Wh/kg gravimetric density."},
                {"title": "Battery Journal", "url": "https://batteryj.org/art2", "snippet": "Cycle life reached 1200 cycles at C/3 charge rate."}
            ],
            "solid state manufacturing cost": [
                {"title": "BloombergNEF EV Report", "url": "https://bnef.com/ev2025", "snippet": "Cell-level costs projected at $95/kWh by 2028."}
            ]
        }
        
    def decompose_query(self, topic: str) -> List[str]:
        topic_lower = topic.lower()
        if "battery" in topic_lower or "solid-state" in topic_lower or "solid state" in topic_lower:
            return ["solid state energy density", "solid state manufacturing cost"]
        return [topic]
        
    def search_and_extract(self, query: str):
        results = self.kb.get(query, [])
        for r in results:
            self.note_store.add_note(r["snippet"], r["title"], r["url"])
            
    def synthesize_brief(self, topic: str) -> str:
        notes = self.note_store.get_all()
        if not notes:
            return f"# Research Brief: {topic}\n\nNo verified findings discovered."
            
        lines = [
            f"# Research Brief: {topic}",
            "",
            "## Executive Summary",
            f"This research investigation analyzed key findings regarding {topic}. The primary findings are detailed below:",
            ""
        ]
        
        for note in notes:
            lines.append(f"- {note['claim']} [{note['id']}]")
            
        lines.append("")
        lines.append("## Verified Sources")
        for note in notes:
            lines.append(f"[{note['id']}] [{note['title']}]({note['url']})")
            
        return "\n".join(lines)
        
    def execute_research(self, topic: str) -> str:
        sub_queries = self.decompose_query(topic)
        for q in sub_queries:
            self.search_and_extract(q)
        return self.synthesize_brief(topic)

if __name__ == "__main__":
    agent = AutonomousResearchAgent()
    brief = agent.execute_research("Solid-State Batteries")
    print(brief)
