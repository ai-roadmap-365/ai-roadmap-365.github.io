import ast
from typing import Dict, Any, List

class AICodeReviewScanner:
    def __init__(self, approved_packages: List[str]):
        self.approved_packages = set(approved_packages)
        
    def scan_code(self, source_code: str, filename: str = "<string>") -> Dict[str, Any]:
        issues = []
        try:
            tree = ast.parse(source_code, filename=filename)
        except SyntaxError as e:
            return {
                "file": filename,
                "passed": False,
                "syntax_error": str(e),
                "issues": []
            }
            
        for node in ast.walk(tree):
            # Check 1: Insecure Shell Execution
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("system", "popen"):
                    issues.append({
                        "line": node.lineno,
                        "rule": "INSECURE_SHELL_EXECUTION",
                        "severity": "CRITICAL",
                        "message": f"Avoid using os.{node.func.attr}; use safe subprocess APIs."
                    })
                    
            # Check 2: Unapproved External Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pkg_root = alias.name.split('.')[0]
                    if pkg_root not in self.approved_packages:
                        issues.append({
                            "line": node.lineno,
                            "rule": "UNAPPROVED_DEPENDENCY",
                            "severity": "HIGH",
                            "message": f"Import '{pkg_root}' is not in approved package whitelist."
                        })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    pkg_root = node.module.split('.')[0]
                    if pkg_root not in self.approved_packages:
                        issues.append({
                            "line": node.lineno,
                            "rule": "UNAPPROVED_DEPENDENCY",
                            "severity": "HIGH",
                            "message": f"ImportFrom '{pkg_root}' is not in approved whitelist."
                        })
                        
            # Check 3: Weak/Tautological Assertions
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    issues.append({
                        "line": node.lineno,
                        "rule": "WEAK_ASSERTION",
                        "severity": "MEDIUM",
                        "message": "Found tautological 'assert True' in test code."
                    })
                    
        return {
            "file": filename,
            "passed": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues
        }

if __name__ == "__main__":
    scanner = AICodeReviewScanner(["os", "sys", "math", "pytest"])
    sample = "import os\nos.system('ls')"
    print(scanner.scan_code(sample))
