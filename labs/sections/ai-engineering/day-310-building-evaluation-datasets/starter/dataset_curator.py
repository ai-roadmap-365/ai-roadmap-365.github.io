import json
import os
from typing import List, Dict, Any, Optional

class EvalDatasetCurator:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        
    def add_record(self, record_id: str, category: str, query: str, expected_output: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if not record_id or not query or not expected_output:
            return False
            
        valid_categories = {"happy_path", "hard_negative", "schema_boundary", "adversarial"}
        if category not in valid_categories:
            return False
            
        for r in self.records:
            if r["query"].strip().lower() == query.strip().lower():
                return False
                
        record = {
            "id": str(record_id).strip(),
            "category": category,
            "query": query.strip(),
            "expected_output": expected_output.strip(),
            "metadata": metadata or {}
        }
        self.records.append(record)
        return True
        
    def get_stratified_counts(self) -> Dict[str, int]:
        counts = {"happy_path": 0, "hard_negative": 0, "schema_boundary": 0, "adversarial": 0}
        for r in self.records:
            cat = r["category"]
            counts[cat] = counts.get(cat, 0) + 1
        return counts
        
    def export_jsonl(self, filepath: str) -> int:
        with open(filepath, "w", encoding="utf-8") as f:
            for r in self.records:
                f.write(json.dumps(r) + "\n")
        return len(self.records)
        
    def load_jsonl(self, filepath: str) -> int:
        count = 0
        if not os.path.exists(filepath):
            return 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    if self.add_record(data.get("id"), data.get("category"), data.get("query"), data.get("expected_output"), data.get("metadata")):
                        count += 1
                except Exception:
                    continue
        return count

if __name__ == "__main__":
    curator = EvalDatasetCurator()
    curator.add_record("eval_01", "happy_path", "What is the return policy?", "30 days with receipt.")
    print("Stratified counts:", curator.get_stratified_counts())
