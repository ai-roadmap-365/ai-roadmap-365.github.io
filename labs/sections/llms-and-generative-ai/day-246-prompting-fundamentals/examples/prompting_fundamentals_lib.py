from typing import List, Optional

class PromptCompiler:
    def __init__(self, role: str, task: str):
        self.role = role.strip()
        self.task = task.strip()
        self.steps: List[str] = []
        self.constraints: List[str] = []
        self.output_schema: Optional[str] = None

    def add_step(self, step: str) -> "PromptCompiler":
        self.steps.append(step.strip())
        return self

    def add_constraint(self, constraint: str) -> "PromptCompiler":
        self.constraints.append(constraint.strip())
        return self

    def set_output_schema(self, schema: str) -> "PromptCompiler":
        self.output_schema = schema.strip()
        return self

    def compile(self, input_payload: str, tag: str = "input_data") -> str:
        parts = []
        parts.append(f"<role_and_task>\nRole: {self.role}\nTask: {self.task}\n</role_and_task>")
        parts.append(f"<{tag}>\n{input_payload.strip()}\n</{tag}>")

        if self.steps:
            steps_str = "\n".join([f"{i+1}. {s}" for i, s in enumerate(self.steps)])
            parts.append(f"<execution_steps>\n{steps_str}\n</execution_steps>")

        if self.constraints:
            c_str = "\n".join([f"- {c}" for c in self.constraints])
            parts.append(f"<constraints>\n{c_str}\n</constraints>")

        if self.output_schema:
            parts.append(f"<output_format>\n{self.output_schema}\nOutput raw data only.\n</output_format>")

        return "\n\n".join(parts)

def run_prompt_demo():
    compiler = PromptCompiler(
        role="Senior Code Reviewer",
        task="Audit database query for security vulnerabilities"
    )
    compiler.add_step("Identify injection vulnerabilities")
    compiler.add_step("Propose parameterized query fix")
    compiler.add_constraint("Focus strictly on SQL security")
    compiler.set_output_schema("Return JSON array with keys: ['vulnerability', 'fix']")

    prompt = compiler.compile("SELECT * FROM users WHERE id = '" + "1' OR '1'='1", tag="code_snippet")
    print("Prompt Demo Compiled Successfully.")
    return prompt

if __name__ == "__main__":
    run_prompt_demo()
