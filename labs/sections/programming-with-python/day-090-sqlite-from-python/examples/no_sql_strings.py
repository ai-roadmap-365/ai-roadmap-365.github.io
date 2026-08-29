"""A guard: no SQL statement in this lab is built out of pieces.

Reviewing for injection by reading is unreliable — the dangerous line looks
exactly like the safe one until you notice the `f`. So this check is
mechanical, it runs in the test suite, and it fails the build.

It parses each file with `ast` rather than grepping, because a regular
expression over source text cannot tell a statement from the word "select"
in a comment or a print. Two places are inspected, and only those two:

  * the first argument of any `.execute`, `.executemany` or `.executescript`
    call — the string that actually reaches the engine;
  * any assignment to a name that says it holds SQL (`sql`, `query`,
    `statement`, `stmt`, or those names with a prefix or suffix).

In either place, four shapes are refused:

    f"SELECT ... {value} ..."        an f-string with a substitution
    "SELECT ... " + value            a concatenation with a non-literal
    "SELECT ... %s" % value          percent formatting
    "SELECT ... {}".format(value)    str.format

Adjacent string literals — "SELECT a, b" " FROM t" — are NOT flagged.
Python joins those at compile time; no runtime value can enter, so they are
the recommended way to wrap a long statement across lines.

`injection_demo.py` is exempt by name, because building a broken query on
purpose is the entire point of that file.

Run it:  python3 no_sql_strings.py [directory]
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

EXEMPT = {"injection_demo.py", "no_sql_strings.py"}

SQL_WORDS = (
    "select ", "insert into", "update ", "delete from", "create table",
    "drop table", " from ", " where ", "order by", "values (",
)


def looks_like_sql(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in SQL_WORDS)


def literal_parts(node: ast.AST) -> str:
    """The constant text of an expression, ignoring the variable parts."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            part.value for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
    if isinstance(node, ast.BinOp):
        return literal_parts(node.left) + literal_parts(node.right)
    return ""


EXECUTE_METHODS = {"execute", "executemany", "executescript"}
SQL_NAME_PARTS = ("sql", "query", "statement", "stmt")


def names_sql(name: str) -> bool:
    return any(part in name.lower() for part in SQL_NAME_PARTS)


class Scanner(ast.NodeVisitor):
    """Look only where a built string could actually become a statement."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[str] = []

    def report(self, node: ast.AST, how: str, where: str) -> None:
        self.findings.append(
            f"{self.path.name}:{node.lineno}: SQL built by {how} and {where}"
        )

    def inspect(self, node: ast.AST, where: str) -> None:
        """Refuse any assembled string that reads like SQL."""
        if isinstance(node, ast.JoinedStr):
            substituted = any(isinstance(part, ast.FormattedValue) for part in node.values)
            if substituted and looks_like_sql(literal_parts(node)):
                self.report(node, "an f-string", where)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            both_literal = isinstance(node.left, ast.Constant) and isinstance(
                node.right, ast.Constant
            )
            if not both_literal and looks_like_sql(literal_parts(node)):
                self.report(node, "concatenation with +", where)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            if looks_like_sql(literal_parts(node.left)):
                self.report(node, "percent formatting", where)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
            and looks_like_sql(literal_parts(node.func.value))
        ):
            self.report(node, "str.format", where)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in EXECUTE_METHODS
            and node.args
        ):
            self.inspect(node.args[0], f"passed straight to {node.func.attr}()")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name) and names_sql(target.id):
                self.inspect(node.value, f"stored in {target.id}")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and names_sql(node.target.id) and node.value:
            self.inspect(node.value, f"stored in {node.target.id}")
        self.generic_visit(node)


def scan(directory: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(directory.rglob("*.py")):
        if path.name in EXEMPT:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        scanner = Scanner(path)
        scanner.visit(tree)
        findings.extend(scanner.findings)
    return findings


def main() -> int:
    directory = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)
    checked = [p.name for p in sorted(directory.rglob("*.py")) if p.name not in EXEMPT]
    findings = scan(directory)

    print(f"Scanning {len(checked)} Python file(s) under {directory.name}/ for assembled SQL.")
    for name in checked:
        print(f"    {name}")
    print(f"Exempt by name (they build broken SQL on purpose): {', '.join(sorted(EXEMPT))}")
    print()
    if findings:
        for finding in findings:
            print(f"  FAIL: {finding}")
        print()
        print(f"{len(findings)} SQL string(s) built from parts. Bind the values instead.")
        return 1
    print("  ok: every SQL statement is a literal; every value is bound.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
