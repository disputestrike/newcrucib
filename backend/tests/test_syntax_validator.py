"""
Tests for syntax_validator.py
"""
import pytest
from syntax_validator import SyntaxValidator


def test_validate_python_valid():
    """Test valid Python code"""
    code = "def hello(): return 'world'"
    result = SyntaxValidator.validate_python(code)
    assert result["valid"] is True
    assert result["error"] is None


def test_validate_python_invalid():
    """Test invalid Python code"""
    code = "def hello( return 'world'"
    result = SyntaxValidator.validate_python(code)
    assert result["valid"] is False
    assert "SyntaxError" in result["error"]


def test_validate_python_empty():
    """Test empty Python code"""
    code = ""
    result = SyntaxValidator.validate_python(code)
    assert result["valid"] is True
    assert "Empty code" in result["issues"]


def test_validate_python_with_wildcard_import():
    """Test Python code with wildcard import"""
    code = "from module import *\ndef hello(): return 'world'"
    result = SyntaxValidator.validate_python(code)
    assert result["valid"] is True
    assert any("Wildcard" in issue for issue in result["issues"])


def test_validate_javascript_valid():
    """Test valid JavaScript code"""
    code = "function hello() { return 'world'; }"
    result = SyntaxValidator.validate_javascript(code)
    assert result["valid"] is True


def test_validate_javascript_unbalanced_braces():
    """Test JavaScript with unbalanced braces"""
    code = "function hello() { return 'world';"
    result = SyntaxValidator.validate_javascript(code)
    assert result["valid"] is False
    assert "Unclosed" in result["error"]


def test_validate_javascript_empty():
    """Test empty JavaScript code"""
    code = ""
    result = SyntaxValidator.validate_javascript(code)
    assert result["valid"] is False
    assert "Empty code" in result["error"]


def test_validate_javascript_balanced_complex():
    """Test JavaScript with nested structures"""
    code = """
    function test() {
        const arr = [1, 2, 3];
        const obj = { key: 'value' };
        if (true) {
            console.log(arr[0]);
        }
    }
    """
    result = SyntaxValidator.validate_javascript(code)
    assert result["valid"] is True


def test_validate_react_component_valid():
    """Test valid React component"""
    code = """
    import React from 'react';
    
    export default function App() {
        return <div>Hello World</div>;
    }
    """
    result = SyntaxValidator.validate_react_component(code)
    assert result["valid"] is True


def test_validate_react_component_no_export():
    """Test React component without export"""
    code = """
    import React from 'react';
    
    function App() {
        return <div>Hello World</div>;
    }
    """
    result = SyntaxValidator.validate_react_component(code)
    assert result["valid"] is False
    assert "export" in result["error"].lower()


def test_validate_react_component_with_map():
    """Test React component with map but no key"""
    code = """
    import React from 'react';
    
    export default function App() {
        const items = [1, 2, 3];
        return <div>{items.map(i => <span>{i}</span>)}</div>;
    }
    """
    result = SyntaxValidator.validate_react_component(code)
    assert result["valid"] is True
    assert any("key" in issue.lower() for issue in result["issues"])


def test_validate_json_valid():
    """Test valid JSON"""
    content = '{"name": "test", "value": 123}'
    result = SyntaxValidator.validate_json(content)
    assert result["valid"] is True


def test_validate_json_invalid():
    """Test invalid JSON"""
    content = '{"name": "test", value: 123}'
    result = SyntaxValidator.validate_json(content)
    assert result["valid"] is False
    assert "JSONDecodeError" in result["error"]


def test_validate_json_empty():
    """Test empty JSON"""
    content = ""
    result = SyntaxValidator.validate_json(content)
    assert result["valid"] is False
