import subprocess
import os
from typing import Dict, Any, List

class FeatureOrchestrator:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)
        
    def execute_quality_gates(self, test_cmd: str = "python3 -m unittest") -> Dict[str, Any]:
        res = subprocess.run(
            test_cmd,
            shell=True,
            cwd=self.workspace_root,
            capture_output=True,
            text=True
        )
        return {
            "exit_code": res.returncode,
            "passed": res.returncode == 0,
            "stdout": res.stdout,
            "stderr": res.stderr
        }
        
    def generate_walkthrough_artifact(
        self,
        feature_name: str,
        files_modified: List[str],
        test_results: Dict[str, Any]
    ) -> str:
        file_table = "\n".join([f"- `{f}`" for f in files_modified])
        status = "PASSED (100%)" if test_results.get("passed") else "FAILED"
        return (
            f"# Feature Walkthrough: {feature_name}\n\n"
            f"## Summary of Changes\n"
            f"The feature was implemented following the 6-stage agentic shipping playbook.\n\n"
            f"## Modified Files\n{file_table}\n\n"
            f"## Verification Evidence\n"
            f"- Test Execution Status: `{status}`\n"
            f"- Exit Code: `{test_results.get('exit_code')}`\n\n"
            f"### Test Output\n```text\n{test_results.get('stdout', '').strip()}\n```\n\n"
            f"> *Ready for human architectural review and merge.*"
        )

if __name__ == "__main__":
    orchestrator = FeatureOrchestrator(".")
    res = orchestrator.execute_quality_gates("python3 -c 'print(\"Tests OK\")'")
    print(orchestrator.generate_walkthrough_artifact("Demo Feature", ["a.py"], res)[:200])
