from typing import List, Optional

class PromptCompiler:
    def __init__(self, role: str, task: str):
        self.role = role
        self.task = task
        self.steps: List[str] = []
        self.constraints: List[str] = []
        self.output_schema: Optional[str] = None

    def add_step(self, step: str) -> "PromptCompiler":
        # TODO: Add execution step
        pass

    def add_constraint(self, constraint: str) -> "PromptCompiler":
        # TODO: Add constraint
        pass

    def set_output_schema(self, schema: str) -> "PromptCompiler":
        # TODO: Set schema
        pass

    def compile(self, input_payload: str, tag: str = "input_data") -> str:
        # TODO: Return full compiled XML prompt
        pass
