import os
from typing import List

class SpecCompiler:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)
        
    def bundle_context(self, relative_file_paths: List[str]) -> str:
        blocks = []
        for path in relative_file_paths:
            abs_path = os.path.join(self.workspace_root, path)
            if os.path.exists(abs_path):
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                blocks.append(f"### File: {path}\n```python\n{content}\n```")
            else:
                blocks.append(f"### File: {path} (NOT FOUND)")
        return "\n\n".join(blocks)
        
    def compile_prompt(
        self,
        goal: str,
        target_files: List[str],
        constraints: List[str],
        non_goals: List[str],
        verification_command: str
    ) -> str:
        context_str = self.bundle_context(target_files)
        
        prompt_lines = [
            f"# TASK OBJECTIVE\n{goal}\n",
            f"# SURGICAL CONTEXT\n{context_str}\n",
            "# HARD CONSTRAINTS",
            "\n".join([f"- {c}" for c in constraints]),
            "\n# NON-GOALS (DO NOT MODIFY)",
            "\n".join([f"- {ng}" for ng in non_goals]),
            f"\n# VERIFICATION PLAN\nRun the following command to verify your work:\n`{verification_command}`\n",
            "# INSTRUCTION FOR AGENT",
            "1. Output your step-by-step implementation plan first.",
            "2. Apply targeted edits using search-and-replace chunks.",
            "3. Run the verification command and report test results."
        ]
        return "\n".join(prompt_lines)

if __name__ == "__main__":
    compiler = SpecCompiler(".")
    res = compiler.compile_prompt("Refactor API", ["app.py"], ["Speed up"], ["Do not break tests"], "pytest")
    print(res[:200])
