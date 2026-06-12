"""Tests for AST analysis module."""

from __future__ import annotations

from app.analysis import analyze_code


def test_analyze_python_functions():
    """Should detect Python function definitions."""
    code = """
def greet(name):
    return f"Hello, {name}"

async def fetch_data(url):
    return await api.get(url)
"""
    result = analyze_code(code, "python")
    names = [f["name"] for f in result.functions]
    assert "greet" in names
    assert "fetch_data" in names


def test_analyze_python_classes():
    """Should detect Python class definitions and their methods."""
    code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""
    result = analyze_code(code, "python")
    assert len(result.classes) == 1
    assert result.classes[0]["name"] == "Calculator"
    assert "add" in result.classes[0]["methods"]
    assert "subtract" in result.classes[0]["methods"]


def test_analyze_python_imports():
    """Should detect Python imports."""
    code = """
import os
import sys
from typing import List, Optional
from collections.abc import Iterable
"""
    result = analyze_code(code, "python")
    assert "os" in result.imports
    assert "sys" in result.imports
    # from typing import List, Optional → imports are ['List', 'Optional']
    assert "List" in result.imports
    assert "Optional" in result.imports
    # from collections.abc import Iterable → imports are ['Iterable']
    assert "Iterable" in result.imports


def test_analyze_python_syntax_error():
    """Should capture syntax errors gracefully."""
    code = "def broken(: )\n"
    result = analyze_code(code, "python")
    assert len(result.errors) > 0
    assert "Syntax error" in result.errors[0]


def test_analyze_javascript():
    """Should detect JS function and class declarations."""
    code = """
function greet(name) {
    return `Hello, ${name}`;
}

const add = (a, b) => a + b;

class Calculator {
    multiply(a, b) {
        return a * b;
    }
}
"""
    result = analyze_code(code, "javascript")
    names = [f["name"] for f in result.functions]
    assert "greet" in names
    assert "add" in names
    assert len(result.classes) == 1
    assert result.classes[0]["name"] == "Calculator"


def test_analyze_typescript():
    """Should detect TypeScript constructs."""
    code = """
import { Component } from 'react';

interface Props {
    name: string;
}

function Welcome(props: Props) {
    return <h1>Hello, {props.name}</h1>;
}

export default Welcome;
"""
    result = analyze_code(code, "typescript")
    names = [f["name"] for f in result.functions]
    assert "Welcome" in names
    assert "react" in result.imports