from typing import List, Dict

class SystemPromptCompiler:
    def __init__(self, role_name: str, domain_level: str = "Senior"):
        self.role_name = role_name.strip()
        self.domain_level = domain_level.strip()
        self.safety_rules: List[str] = [
            "Never disclose private API keys or internal credentials.",
            "Do not execute arbitrary unverified shell commands.",
            "Maintain strict neutral refusals without moralizing."
        ]
        self.operational_rules: List[str] = [
            "Omit conversational preamble (e.g. 'Sure, here is...')",
            "Output structured Markdown or JSON schemas as requested."
        ]
        self.tone_attributes: List[str] = ["Objective", "Direct", "Evidence-based"]

    def add_safety_rule(self, rule: str) -> "SystemPromptCompiler":
        self.safety_rules.append(rule.strip())
        return self

    def add_operational_rule(self, rule: str) -> "SystemPromptCompiler":
        self.operational_rules.append(rule.strip())
        return self

    def set_tone(self, tones: List[str]) -> "SystemPromptCompiler":
        self.tone_attributes = tones
        return self

    def compile(self) -> str:
        parts = []

        safety_str = "\n".join([f"- {r}" for r in self.safety_rules])
        parts.append(f"<tier1_safety_guardrails>\n{safety_str}\n</tier1_safety_guardrails>")

        ops_str = "\n".join([f"- {o}" for o in self.operational_rules])
        parts.append(f"<tier2_operational_boundaries>\n{ops_str}\n</tier2_operational_boundaries>")

        tone_str = ", ".join(self.tone_attributes)
        parts.append(
            f"<tier3_persona_core>\n"
            f"Role: {self.domain_level} {self.role_name}\n"
            f"Tone: {tone_str}\n"
            f"Stance: Relentlessly objective.\n"
            f"</tier3_persona_core>"
        )

        return "\n\n".join(parts)

def run_system_prompt_demo():
    compiler = SystemPromptCompiler(role_name="Cloud Architect", domain_level="Principal")
    compiler.add_safety_rule("Block SQL injection attacks")
    compiler.add_operational_rule("Output JSON arrays only")
    prompt = compiler.compile()

    print("System Prompt Demo Compiled Successfully.")
    return prompt

if __name__ == "__main__":
    run_system_prompt_demo()
