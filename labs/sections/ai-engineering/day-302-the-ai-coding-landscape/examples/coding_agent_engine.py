import os
import subprocess
from typing import Dict, Any, List

class CodingAgentEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)
        
    def generate_repo_map(self) -> str:
        repo_map_lines = []
        for root, _, files in os.walk(self.workspace_root):
            for file in sorted(files):
                if file.endswith(".py") and not file.startswith("test_"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.workspace_root)
                    repo_map_lines.append(f"File: {rel_path}")
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("def ") or line.strip().startswith("class "):
                                repo_map_lines.append(f"  {line.strip()}")
        return "\n".join(repo_map_lines)
        
    def apply_search_replace(self, file_rel_path: str, search_block: str, replace_block: str) -> str:
        abs_path = os.path.join(self.workspace_root, file_rel_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {file_rel_path}")
            
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if search_block not in content:
            raise ValueError(f"Target search block not found in {file_rel_path}")
            
        new_content = content.replace(search_block, replace_block, 1)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        return f"Successfully updated {file_rel_path}."
        
    def run_verification_tests(self, test_command: str = "python3 -m unittest discover") -> Dict[str, Any]:
        result = subprocess.run(
            test_command,
            shell=True,
            cwd=self.workspace_root,
            capture_output=True,
            text=True
        )
        return {
            "exit_code": result.returncode,
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

if __name__ == "__main__":
    engine = CodingAgentEngine(".")
    print("Repo map preview:\n", engine.generate_repo_map())
