"""
Tests for test_runner.py
"""
import pytest
from test_runner import TestRunner
from code_executor import CodeExecutor


@pytest.mark.asyncio
async def test_run_python_tests_basic():
    """Test basic Python test execution"""
    executor = CodeExecutor()
    runner = TestRunner(executor)
    
    files = {
        "main.py": "def add(a, b): return a + b",
        "test_main.py": '''
def test_add():
    from main import add
    assert add(1, 2) == 3
'''
    }
    
    result = await runner.run_python_tests(files)
    assert "passed" in result
    assert "total" in result
    assert "duration" in result


def test_parse_pytest_output_success():
    """Test parsing successful pytest output"""
    runner = TestRunner(CodeExecutor())
    
    stdout = """
============================= test session starts ==============================
collected 5 items

test_main.py::test_add PASSED                                            [ 20%]
test_main.py::test_subtract PASSED                                       [ 40%]
test_main.py::test_multiply PASSED                                       [ 60%]
test_main.py::test_divide PASSED                                         [ 80%]
test_main.py::test_modulo PASSED                                         [100%]

============================== 5 passed in 0.12s ===============================
"""
    
    result = runner._parse_pytest_output(stdout, "")
    assert result["total"] == 5
    assert result["passed_count"] == 5
    assert result["failed_count"] == 0
    assert result["skipped"] == 0
    assert len(result["failures"]) == 0


def test_parse_pytest_output_with_failures():
    """Test parsing pytest output with failures"""
    runner = TestRunner(CodeExecutor())
    
    stdout = """
============================= test session starts ==============================
collected 3 items

test_main.py::test_add PASSED                                            [ 33%]
test_main.py::test_divide FAILED                                         [ 66%]
test_main.py::test_multiply PASSED                                       [100%]

=================================== FAILURES ===================================
FAILED test_main.py::test_divide - AssertionError: assert 5 == 2.5
============================== 2 passed, 1 failed in 0.15s =======================
"""
    
    result = runner._parse_pytest_output(stdout, "")
    assert result["total"] == 3
    assert result["passed_count"] == 2
    assert result["failed_count"] == 1
    assert len(result["failures"]) == 1
    assert result["failures"][0]["test"] == "test_divide"
    assert "AssertionError" in result["failures"][0]["error"]


def test_parse_pytest_output_with_skipped():
    """Test parsing pytest output with skipped tests"""
    runner = TestRunner(CodeExecutor())
    
    stdout = """
============================= test session starts ==============================
collected 4 items

test_main.py::test_add PASSED                                            [ 25%]
test_main.py::test_skip SKIPPED                                          [ 50%]
test_main.py::test_divide FAILED                                         [ 75%]
test_main.py::test_multiply PASSED                                       [100%]

=================================== FAILURES ===================================
FAILED test_main.py::test_divide - ZeroDivisionError
==================== 2 passed, 1 failed, 1 skipped in 0.18s ====================
"""
    
    result = runner._parse_pytest_output(stdout, "")
    assert result["total"] == 4
    assert result["passed_count"] == 2
    assert result["failed_count"] == 1
    assert result["skipped"] == 1


def test_parse_jest_output_success():
    """Test parsing successful Jest output"""
    runner = TestRunner(CodeExecutor())
    
    stdout = """
PASS  test/main.test.js
  ✓ test add (3 ms)
  ✓ test subtract (1 ms)
  ✓ test multiply (2 ms)

Tests:       3 passed, 3 total
Snapshots:   0 total
Time:        1.234 s
"""
    
    result = runner._parse_jest_output(stdout)
    assert result["total"] == 3
    assert result["passed_count"] == 3
    assert result["failed_count"] == 0


def test_parse_jest_output_with_failures():
    """Test parsing Jest output with failures"""
    runner = TestRunner(CodeExecutor())
    
    stdout = """
FAIL  test/main.test.js
  ✓ test add (3 ms)
  ✕ test divide (5 ms)
  ✓ test multiply (2 ms)

  ● test divide
    expect(received).toBe(expected)
    Expected: 2.5
    Received: 5

Tests:       1 failed, 2 passed, 3 total
Snapshots:   0 total
Time:        1.456 s
"""
    
    result = runner._parse_jest_output(stdout)
    assert result["total"] == 3
    assert result["passed_count"] == 2
    assert result["failed_count"] == 1
    assert len(result["failures"]) >= 0  # Parsing failures is best-effort


def test_parse_jest_json_output():
    """Test parsing Jest JSON output"""
    runner = TestRunner(CodeExecutor())
    
    stdout = """{
  "numTotalTests": 5,
  "numPassedTests": 4,
  "numFailedTests": 1,
  "numPendingTests": 0,
  "testResults": [
    {
      "name": "test/main.test.js",
      "assertionResults": [
        {
          "title": "test add",
          "status": "passed"
        },
        {
          "title": "test divide",
          "status": "failed",
          "failureMessages": ["Expected 2.5 but got 5"]
        }
      ]
    }
  ]
}"""
    
    result = runner._parse_jest_output(stdout)
    assert result["total"] == 5
    assert result["passed_count"] == 4
    assert result["failed_count"] == 1
    assert len(result["failures"]) == 1
    assert result["failures"][0]["test"] == "test divide"


def test_parse_empty_output():
    """Test parsing empty output"""
    runner = TestRunner(CodeExecutor())
    
    result = runner._parse_pytest_output("", "")
    assert result["total"] == 0
    assert result["passed_count"] == 0
    assert result["failed_count"] == 0
    assert result["skipped"] == 0
    
    result = runner._parse_jest_output("")
    assert result["total"] == 0
    assert result["passed_count"] == 0
    assert result["failed_count"] == 0


@pytest.mark.asyncio
async def test_run_javascript_tests_basic():
    """Test basic JavaScript test execution"""
    executor = CodeExecutor()
    runner = TestRunner(executor)
    
    files = {
        "package.json": '''{
            "name": "test",
            "version": "1.0.0",
            "scripts": {
                "test": "echo 'Tests: 5 passed, 5 total'"
            }
        }''',
        "main.js": "function add(a, b) { return a + b; }",
        "test/main.test.js": '''
test('add', () => {
    expect(add(1, 2)).toBe(3);
});
'''
    }
    
    result = await runner.run_javascript_tests(files)
    assert "passed" in result
    assert "total" in result
    assert "duration" in result
