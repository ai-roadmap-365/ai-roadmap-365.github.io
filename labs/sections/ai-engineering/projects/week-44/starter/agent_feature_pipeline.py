import os
import ast
import subprocess
import re
from typing import Dict, Any, List, Optional

class AgentFeaturePipeline:
    def __init__(self, workspace_root: str, approved_packages: Optional[List[str]] = None):
        self.workspace_root = os.path.realpath(workspace_root)
        self.approved_packages = set(approved_packages or ["os", "sys", "math", "pytest", "typing"])
        
    def generate_repo_map(self) -> str:
        lines = []
        for root, _, files in os.walk(self.workspace_root):
            for file in sorted(files):
                if file.endswith(".py") and not file.startswith("test_"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.workspace_root)
                    lines.append(f"File: {rel_path}")
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        for l in f:
                            if l.strip().startswith("def ") or l.strip().startswith("class "):
                                lines.append(f"  {l.strip()}")
        return "\n".join(lines)
        
    def apply_patch(self, file_rel_path: str, search_block: str, replace_block: str) -> str:
        abs_path = os.path.join(self.workspace_root, file_rel_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {file_rel_path}")
            
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if search_block not in content:
            raise ValueError(f"Search block not found in {file_rel_path}")
            
        new_content = content.replace(search_block, replace_block, 1)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Updated {file_rel_path}"
        
    def audit_security(self, source_code: str) -> Dict[str, Any]:
        issues = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return {"passed": False, "issues": [{"rule": "SYNTAX_ERROR", "message": str(e)}]}
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("system", "popen"):
                    issues.append({"rule": "INSECURE_SHELL", "message": f"Avoid os.{node.func.attr}"})
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pkg = alias.name.split('.')[0]
                    if pkg not in self.approved_packages:
                        issues.append({"rule": "UNAPPROVED_DEPENDENCY", "message": f"Package '{pkg}' not approved"})
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    pkg = node.module.split('.')[0]
                    if pkg not in self.approved_packages:
                        issues.append({"rule": "UNAPPROVED_DEPENDENCY", "message": f"Package '{pkg}' not approved"})
        return {"passed": len(issues) == 0, "issues": issues}
        
    def run_tests(self, test_cmd: str = "python3 -m unittest") -> Dict[str, Any]:
        res = subprocess.run(test_cmd, shell=True, cwd=self.workspace_root, capture_output=True, text=True)
        return {
            "exit_code": res.returncode,
            "passed": res.returncode == 0,
            "stdout": res.stdout,
            "stderr": res.stderr
        }
        
    def format_walkthrough(self, feature_name: str, modified_files: List[str], test_res: Dict[str, Any]) -> str:
        status = "PASSED (100%)" if test_res.get("passed") else "FAILED"
        files_str = "\n".join([f"- `{f}`" for f in modified_files])
        return (
            f"# Feature Walkthrough: {feature_name}\n\n"
            f"## Modified Files\n{files_str}\n\n"
            f"## Verification Evidence\n"
            f"- Status: `{status}`\n"
            f"- Exit Code: `{test_res.get('exit_code')}`\n\n"
            f"### Output\n```text\n{test_res.get('stdout', '').strip()}\n```\n"
        )

if __name__ == "__main__":
    pipeline = AgentFeaturePipeline(".")
    print("Pipeline ready. Workspace map preview:\n", pipeline.generate_repo_map()[:100])
