"""Pure source metrics; independent of filesystem traversal and CLI reporting."""

import ast

from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

LIMITS = {"CC": 8, "MI": 50, "SLOC": 300, "function_lines": 60}


def block_complexities(source: str) -> list[int]:
    """Include methods and nested closures, not just top-level functions."""
    pending = list(cc_visit(source))
    values = []
    while pending:
        block = pending.pop()
        values.append(block.complexity)
        pending.extend(getattr(block, "methods", ()))
        pending.extend(getattr(block, "closures", ()))
    return values


def function_spans(tree: ast.AST) -> list[int]:
    """Count decorators and docstrings in the physical function-size limit."""
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            first = min([node.lineno, *[d.lineno for d in node.decorator_list]])
            spans.append((node.end_lineno or node.lineno) - first + 1)
    return spans


def measure(source: str) -> dict[str, float]:
    """SLOC excludes blanks/comments; MI uses Radon's multiline-docstring convention."""
    return {
        "CC": max(block_complexities(source), default=0),
        "MI": mi_visit(source, multi=True),
        "SLOC": analyze(source).sloc,
        "function_lines": max(function_spans(ast.parse(source)), default=0),
    }


def violations(metrics: dict[str, float]) -> list[str]:
    """Treat boundaries inclusively and retain all failures for one-pass feedback."""
    failures = []
    for name, limit in LIMITS.items():
        value = metrics[name]
        bad = value < limit if name == "MI" else value > limit
        if bad:
            operator = ">=" if name == "MI" else "<="
            failures.append(f"{name}={value:.4f}, required {operator} {limit}")
    return failures
