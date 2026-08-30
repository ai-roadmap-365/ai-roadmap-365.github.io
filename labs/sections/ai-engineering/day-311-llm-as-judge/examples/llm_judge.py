import json
import re
from typing import Dict, Any

class LLMJudgeEvaluator:
    @staticmethod
    def build_rubric_prompt(query: str, context: str, candidate_answer: str) -> str:
        prompt_template = (
            "You are an expert impartial evaluation judge. Grade the candidate response on a 1-5 scale for FAITHFULNESS.\n\n"
            "Evaluation Rubric:\n"
            "- Score 1: Completely ungrounded or contains severe factual hallucinations.\n"
            "- Score 2: Major claims cannot be verified against the context.\n"
            "- Score 3: Partially grounded, but includes minor unsupported extrapolations.\n"
            "- Score 4: Mostly grounded with only trivial non-factual filler.\n"
            "- Score 5: 100% faithful and fully supported by the context documents.\n\n"
            f"Input Context:\n{context}\n\n"
            f"User Query:\n{query}\n\n"
            f"Candidate Response:\n{candidate_answer}\n\n"
            "Respond ONLY with a JSON object in this exact schema:\n"
            '{\n  "reasoning": "<step-by-step critique>",\n  "score": <integer 1 to 5>,\n  "passed": <boolean>\n}'
        )
        return prompt_template

    @staticmethod
    def parse_judge_response(raw_response: str) -> Dict[str, Any]:
        try:
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if "score" in data and "reasoning" in data:
                    score = int(data["score"])
                    clamped_score = max(1, min(5, score))
                    return {
                        "score": clamped_score,
                        "reasoning": str(data["reasoning"]).strip(),
                        "passed": clamped_score >= 4
                    }
        except Exception:
            pass
        return {"score": 1, "reasoning": "Failed to parse judge output JSON", "passed": False}

    @staticmethod
    def resolve_pairwise_swap(pass1_winner: str, pass2_winner: str) -> str:
        norm_p1 = str(pass1_winner).strip().upper()
        norm_p2 = str(pass2_winner).strip().upper()
        
        if norm_p1 == "A" and norm_p2 == "B":
            return "candidate"
        elif norm_p1 == "B" and norm_p2 == "A":
            return "baseline"
        elif norm_p1 == "TIE" or norm_p2 == "TIE":
            return "tie"
        else:
            return "position_bias_inconsistent"

if __name__ == "__main__":
    judge = LLMJudgeEvaluator()
    sample_json = '```json\n{"reasoning": "Fully grounded in doc 1", "score": 5}\n```'
    print("Parsed Judge Output:", judge.parse_judge_response(sample_json))
