"""AST parsing utilities for code analysis."""

from __future__ import annotations

import ast
import logging
import re
from typing import Any

from app.models import AnalysisResult

logger = logging.getLogger(__name__)


def analyze_code(code: str, language: str) -> AnalysisResult:
    """Analyze source code using AST parsing.

    Supports 'python' natively. For other languages, falls back to regex-based analysis.

    Args:
        code: Source code to analyze.
        language: Programming language identifier.

    Returns:
        AnalysisResult with extracted functions, classes, imports, and errors.
    """
    if language == "python":
        return _analyze_python(code)
    elif language in ("javascript", "typescript", "jsx", "tsx"):
        return _analyze_js_like(code, language)
    else:
        return _analyze_generic(code, language)


def _analyze_python(code: str) -> AnalysisResult:
    """Parse Python code using the built-in `ast` module."""
    result = AnalysisResult(language="python")
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        result.errors.append(f"Syntax error: {e}")
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result.functions.append({
                "name": node.name,
                "line": node.lineno,
                "args": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node) or "",
            })
        elif isinstance(node, ast.AsyncFunctionDef):
            result.functions.append({
                "name": node.name,
                "line": node.lineno,
                "args": [arg.arg for arg in node.args.args],
                "async": True,
                "docstring": ast.get_docstring(node) or "",
            })
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(item.name)
            result.classes.append({
                "name": node.name,
                "line": node.lineno,
                "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                "methods": methods,
                "docstring": ast.get_docstring(node) or "",
            })
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                result.imports.append(alias.name)

    return result


def _analyze_js_like(code: str, language: str) -> AnalysisResult:
    """Analyze JavaScript/TypeScript code using regex patterns (no tree-sitter needed)."""
    result = AnalysisResult(language=language)

    # Extract imports
    import_patterns = [
        r'import\s+(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"](\S+)[\'"]',
        r'const\s+\w+\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
    ]
    for pattern in import_patterns:
        for match in re.finditer(pattern, code, re.MULTILINE):
            result.imports.append(match.group(1))

    # Extract function declarations
    func_patterns = [
        r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
        r'(?:export\s+)?(?:async\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>',
        r'(?:export\s+)?(?:async\s+)?const\s+(\w+)\s*=\s*function\s*\(',
    ]
    for pattern in func_patterns:
        for match in re.finditer(pattern, code, re.MULTILINE):
            line_num = code[: match.start()].count("\n") + 1
            result.functions.append({
                "name": match.group(1),
                "line": line_num,
            })

    # Extract class declarations
    class_pattern = r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
    for match in re.finditer(class_pattern, code, re.MULTILINE):
        line_num = code[: match.start()].count("\n") + 1
        cls = {"name": match.group(1), "line": line_num}
        if match.group(2):
            cls["extends"] = match.group(2)
        result.classes.append(cls)

    return result


def _analyze_generic(code: str, language: str) -> AnalysisResult:
    """Generic fallback — basic regex analysis."""
    result = AnalysisResult(language=language)

    # Simple function detection
    for match in re.finditer(r'(?:def|function|fn|func)\s+(\w+)\s*\(', code):
        line_num = code[: match.start()].count("\n") + 1
        result.functions.append({"name": match.group(1), "line": line_num})

    # Simple class detection
    for match in re.finditer(r'(?:class|struct|trait)\s+(\w+)', code):
        line_num = code[: match.start()].count("\n") + 1
        result.classes.append({"name": match.group(1), "line": line_num})

    return result