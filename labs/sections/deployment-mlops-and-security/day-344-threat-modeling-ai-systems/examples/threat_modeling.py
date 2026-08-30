from typing import Dict, Any, List, Optional

class AIThreatModelScorer:
    def __init__(self):
        self.identified_threats: List[Dict[str, Any]] = []

    def add_threat(self, threat_id: str, title: str, category_stride: str, 
                   owasp_id: str, damage: int, reproducibility: int, 
                   exploitability: int, affected_users: int, discoverability: int,
                   description: str) -> Dict[str, Any]:
        scores = [damage, reproducibility, exploitability, affected_users, discoverability]
        for s in scores:
            if not isinstance(s, int) or not (1 <= s <= 10):
                raise ValueError("All DREAD criteria must be integers between 1 and 10.")

        composite_score = round(sum(scores) / 5.0, 2)
        
        if composite_score >= 7.5:
            severity = "CRITICAL"
        elif composite_score >= 5.0:
            severity = "HIGH"
        elif composite_score >= 3.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        record = {
            "threat_id": threat_id,
            "title": title,
            "stride_category": category_stride,
            "owasp_id": owasp_id,
            "dread_scores": {
                "damage": damage,
                "reproducibility": reproducibility,
                "exploitability": exploitability,
                "affected_users": affected_users,
                "discoverability": discoverability
            },
            "composite_score": composite_score,
            "severity": severity,
            "description": description
        }
        self.identified_threats.append(record)
        return record

    def get_prioritized_remediation_plan(self) -> List[Dict[str, Any]]:
        return sorted(self.identified_threats, key=lambda x: x["composite_score"], reverse=True)

if __name__ == "__main__":
    s = AIThreatModelScorer()
    print(s.add_threat("T1", "Prompt Injection", "Elevation", "LLM01", 9, 8, 8, 9, 8, "Test"))
