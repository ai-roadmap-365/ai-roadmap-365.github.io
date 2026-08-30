import subprocess
import re
from typing import Dict, Any

class SelfHealingTestRunner:
    def __init__(self, workspace_root: str, max_iterations: int = 4):
        self.workspace_root = workspace_root
        self.max_iterations = max_iterations
        
    def execute_test_command(self, test_cmd: str) -> Dict[str, Any]:
        result = subprocess.run(
            test_cmd,
            shell=True,
            cwd=self.workspace_root,
            capture_output=True,
            text=True
        )
        return {
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "combined_output": result.stdout + "\n" + result.stderr
        }
        
    def extract_traceback_diagnostics(self, raw_output: str) -> Dict[str, Any]:
        diagnostics = {
            "failing_file": None,
            "line_number": None,
            "error_type": "UnknownError",
            "error_message": ""
        }
        
        file_match = re.search(r'File "([^"]+\.py)", line (\d+)', raw_output)
        if file_match:
            diagnostics["failing_file"] = file_match.group(1)
            diagnostics["line_number"] = int(file_match.group(2))
            
        error_match = re.search(r'([A-Za-z]+Error|Exception): (.+)', raw_output)
        if error_match:
            diagnostics["error_type"] = error_match.group(1)
            diagnostics["error_message"] = error_match.group(2).strip()
            
        return diagnostics
        
    def format_repair_prompt(self, diagnostics: Dict[str, Any], raw_output: str) -> str:
        return (
            f"# TEST FAILURE DETECTED\n"
            f"Failing File: {diagnostics.get('failing_file')}\n"
            f"Line Number: {diagnostics.get('line_number')}\n"
            f"Error: {diagnostics.get('error_type')}: {diagnostics.get('error_message')}\n\n"
            f"## Full Terminal Output:\n```text\n{raw_output.strip()}\n```\n\n"
            f"## Instructions:\n"
            f"1. Analyze the root cause of this failure.\n"
            f"2. Apply a targeted search-and-replace fix.\n"
            f"3. Do not modify unrelated functions."
        )

if __name__ == "__main__":
    runner = SelfHealingTestRunner(".")
    res = runner.execute_test_command("python3 -c 'print(\"Tests OK\")'")
    print("Execution output:", res["stdout"].strip())
