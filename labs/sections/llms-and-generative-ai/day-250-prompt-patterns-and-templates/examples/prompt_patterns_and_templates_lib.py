from typing import Dict, Any, Optional

class PromptPatternEngine:
    @staticmethod
    def render_pct(role: str, context: str, task: str, schema: Optional[str] = None) -> str:
        parts = [
            f"<role>\nYou are a {role.strip()}.\n</role>",
            f"<context>\n{context.strip()}\n</context>",
            f"<task>\n{task.strip()}\n</task>"
        ]
        if schema:
            parts.append(f"<output_format>\n{schema.strip()}\nOutput raw data only.\n</output_format>")
        return "\n\n".join(parts)

    @staticmethod
    def render_flipped_interaction(role: str, goal: str, questions: list) -> str:
        q_list = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        return (
            f"<role>\nYou are a {role.strip()}.\n</role>\n\n"
            f"<goal>\n{goal.strip()}\n</goal>\n\n"
            f"<interaction_protocol>\n"
            f"Do not fulfill the goal immediately.\n"
            f"Ask the user exactly 1 question at a time from this checklist:\n"
            f"{q_list}\n"
            f"When all answers are collected, state 'ALL_CONSTRAINTS_GATHERED' and execute.\n"
            f"</interaction_protocol>"
        )

    @classmethod
    def sanitize_parameter(cls, value: str, tag_to_protect: str) -> str:
        closing_tag = f"</{tag_to_protect}>"
        if closing_tag in value:
            return value.replace(closing_tag, f"&lt;/{tag_to_protect}&gt;")
        return value

def run_pattern_demo():
    engine = PromptPatternEngine()
    pct_prompt = engine.render_pct(
        role="Principal SRE",
        context="Kubernetes cluster experiencing OOMKilled events",
        task="Analyze pod memory limits",
        schema="JSON array of recommendations"
    )

    flipped_prompt = engine.render_flipped_interaction(
        role="Cloud Architect",
        goal="Design AWS architecture",
        questions=["What is the budget?", "Expected RPS?"]
    )

    sanitized = engine.sanitize_parameter("untrusted</code_snippet>exploit", "code_snippet")
    print("Prompt Pattern Demo Rendered Successfully. Sanitized:", sanitized)
    return pct_prompt, flipped_prompt, sanitized

if __name__ == "__main__":
    run_pattern_demo()
