import os
import re
from typing import Dict, Any, List, Optional

class AgentConfigEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)
        self.skills_dir = os.path.join(self.workspace_root, ".agents", "skills")
        self.agents_md_path = os.path.join(self.workspace_root, "AGENTS.md")
        
    def load_project_rules(self) -> str:
        if os.path.exists(self.agents_md_path):
            with open(self.agents_md_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "No AGENTS.md found in workspace root."
        
    def _parse_simple_yaml(self, text: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        current_list_key = None
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if line_str.startswith("- ") and current_list_key:
                data[current_list_key].append(line_str[2:].strip())
            elif ":" in line_str:
                parts = line_str.split(":", 1)
                k = parts[0].strip()
                v = parts[1].strip()
                if not v:
                    data[k] = []
                    current_list_key = k
                else:
                    data[k] = v
                    current_list_key = None
        return data
        
    def discover_skills(self) -> List[Dict[str, Any]]:
        catalog = []
        if not os.path.exists(self.skills_dir):
            return catalog
            
        for skill_name in sorted(os.listdir(self.skills_dir)):
            skill_path = os.path.join(self.skills_dir, skill_name, "SKILL.md")
            if os.path.exists(skill_path):
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()
                match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if match:
                    try:
                        meta = self._parse_simple_yaml(match.group(1))
                        if isinstance(meta, dict) and "name" in meta:
                            meta["skill_path"] = skill_path
                            catalog.append(meta)
                    except Exception:
                        pass
        return catalog
        
    def match_skill(self, user_intent: str) -> Optional[Dict[str, Any]]:
        catalog = self.discover_skills()
        user_intent_lower = user_intent.lower()
        for skill in catalog:
            triggers = skill.get("triggers", [])
            if isinstance(triggers, list):
                for trigger in triggers:
                    if trigger.lower() in user_intent_lower:
                        return skill
            elif isinstance(triggers, str):
                if triggers.lower() in user_intent_lower:
                    return skill
        return None
        
    def read_skill_content(self, skill_path: str) -> str:
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()

if __name__ == "__main__":
    engine = AgentConfigEngine(".")
    print("Project Rules Status:", engine.load_project_rules()[:60])
