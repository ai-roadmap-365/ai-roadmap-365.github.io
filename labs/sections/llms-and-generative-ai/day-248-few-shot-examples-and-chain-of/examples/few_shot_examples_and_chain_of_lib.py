from typing import List, Dict, Any
from collections import Counter

class FewShotCoTEngine:
    def __init__(self, task_description: str):
        self.task_description = task_description.strip()
        self.exemplars: List[Dict[str, str]] = []

    def add_exemplar(self, question: str, reasoning: str, answer: str) -> "FewShotCoTEngine":
        self.exemplars.append({
            "question": question.strip(),
            "reasoning": reasoning.strip(),
            "answer": answer.strip()
        })
        return self

    def compile_prompt(self, query: str) -> str:
        parts = [f"<instructions>\n{self.task_description}\nThink step by step before providing the final answer.\n</instructions>"]

        if self.exemplars:
            parts.append("<examples>")
            for i, ex in enumerate(self.exemplars):
                parts.append(
                    f'<example id="{i+1}">\n'
                    f'<input>{ex["question"]}</input>\n'
                    f'<reasoning>{ex["reasoning"]}</reasoning>\n'
                    f'<answer>{ex["answer"]}</answer>\n'
                    f'</example>'
                )
            parts.append("</examples>")

        parts.append(f"<query>\n{query.strip()}\n</query>\n\n<scratchpad>\nLet us reason step by step:")
        return "\n\n".join(parts)

    @staticmethod
    def aggregate_self_consistency(sampled_answers: List[str]) -> Dict[str, Any]:
        if not sampled_answers:
            raise ValueError("Sampled answers list cannot be empty.")

        counts = Counter(sampled_answers)
        majority_answer, vote_count = counts.most_common(1)[0]
        confidence = vote_count / len(sampled_answers)

        return {
            "consensus_answer": majority_answer,
            "confidence": confidence,
            "votes": dict(counts),
            "total_samples": len(sampled_answers)
        }

def run_cot_demo():
    engine = FewShotCoTEngine("Solve multi-step math problems")
    engine.add_exemplar("What is 12 * 15?", "12 * 10 = 120, 12 * 5 = 60, 120 + 60 = 180", "180")
    prompt = engine.compile_prompt("What is 14 * 16?")

    samples = ["224", "224", "214", "224", "224"]
    result = engine.aggregate_self_consistency(samples)

    print("CoT Demo Compiled Successfully. Consensus:", result["consensus_answer"])
    return prompt, result

if __name__ == "__main__":
    run_cot_demo()
