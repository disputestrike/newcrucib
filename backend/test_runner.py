"""
Test runner for executing and parsing test results.
Runs test suites and parses results from pytest and Jest.
"""
import re
import json
from typing import Dict, Any
from code_executor import CodeExecutor


class TestRunner:
    """Runs test suites and parses results"""
    
    def __init__(self, executor: CodeExecutor):
        self.executor = executor
    
    async def run_python_tests(
        self,
        files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Run pytest and parse results
        
        Args:
            files: Dictionary of file paths to content (including test files)
        
        Returns:
            {
                "passed": bool,
                "total": int,
                "passed_count": int,
                "failed_count": int,
                "skipped": int,
                "duration": float,
                "coverage": float or None,
                "failures": [
                    {
                        "test": "test_user_creation",
                        "file": "tests/test_user.py",
                        "error": "AssertionError: ..."
                    }
                ]
            }
        """
        # Run pytest
        result = await self.executor.run_tests(
            files=files,
            test_command="pytest -v",
            language="Python"
        )
        
        # Parse pytest output
        parsed = self._parse_pytest_output(result["stdout"], result["stderr"])
        
        # Merge with basic result
        return {
            "passed": result["passed"],
            "total": parsed["total"],
            "passed_count": parsed["passed_count"],
            "failed_count": parsed["failed_count"],
            "skipped": parsed["skipped"],
            "duration": result["duration"],
            "coverage": result.get("coverage"),
            "failures": parsed["failures"]
        }
    
    async def run_javascript_tests(
        self,
        files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Run Jest/Vitest and parse results
        
        Args:
            files: Dictionary of file paths to content (including test files)
        
        Returns:
            Same structure as run_python_tests
        """
        # Try to determine which test runner to use
        test_command = "npm test"
        
        # Check package.json for test script
        if "package.json" in files:
            try:
                package_json = json.loads(files["package.json"])
                scripts = package_json.get("scripts", {})
                test_script = scripts.get("test", "")
                
                if "jest" in test_script:
                    test_command = "npm test -- --json"
                elif "vitest" in test_script:
                    test_command = "npm test"
            except Exception:
                pass
        
        # Run tests
        result = await self.executor.run_tests(
            files=files,
            test_command=test_command,
            language="JavaScript"
        )
        
        # Parse jest/vitest output
        parsed = self._parse_jest_output(result["stdout"])
        
        return {
            "passed": result["passed"],
            "total": parsed["total"],
            "passed_count": parsed["passed_count"],
            "failed_count": parsed["failed_count"],
            "skipped": parsed["skipped"],
            "duration": result["duration"],
            "coverage": result.get("coverage"),
            "failures": parsed["failures"]
        }
    
    def _parse_pytest_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """
        Parse pytest console output
        
        Args:
            stdout: Standard output from pytest
            stderr: Standard error from pytest
        
        Returns:
            Dictionary with parsed test results
        """
        output = stdout + stderr
        
        # Initialize results
        result = {
            "total": 0,
            "passed_count": 0,
            "failed_count": 0,
            "skipped": 0,
            "failures": []
        }
        
        # Parse summary line: "5 passed, 2 failed, 1 skipped in 0.12s"
        summary_pattern = r'(\d+)\s+passed'
        passed_match = re.search(summary_pattern, output)
        if passed_match:
            result["passed_count"] = int(passed_match.group(1))
        
        failed_pattern = r'(\d+)\s+failed'
        failed_match = re.search(failed_pattern, output)
        if failed_match:
            result["failed_count"] = int(failed_match.group(1))
        
        skipped_pattern = r'(\d+)\s+skipped'
        skipped_match = re.search(skipped_pattern, output)
        if skipped_match:
            result["skipped"] = int(skipped_match.group(1))
        
        result["total"] = result["passed_count"] + result["failed_count"] + result["skipped"]
        
        # Parse failures - first split by FAILED markers, then process each
        failure_lines = output.split('FAILED ')
        for failure_line in failure_lines[1:]:  # Skip first empty split
            # Extract test identifier (file::test_name)
            test_match = re.match(r'([\w/\.]+)::([\w_]+)', failure_line)
            if test_match:
                file_path = test_match.group(1)
                test_name = test_match.group(2)
                
                # Extract error message (everything after the dash until next test or end)
                error_match = re.search(r'-\s*(.+?)(?=\nFAILED|\nPASSED|$)', failure_line, re.DOTALL)
                if error_match:
                    error_msg = error_match.group(1).strip()
                    # Take only first line for brevity
                    error_msg = error_msg.split('\n')[0] if '\n' in error_msg else error_msg
                else:
                    error_msg = "Test failed"
                
                result["failures"].append({
                    "test": test_name,
                    "file": file_path,
                    "error": error_msg
                })
        
        return result
    
    def _parse_jest_output(self, stdout: str) -> Dict[str, Any]:
        """
        Parse Jest JSON output
        
        Args:
            stdout: Standard output from Jest
        
        Returns:
            Dictionary with parsed test results
        """
        result = {
            "total": 0,
            "passed_count": 0,
            "failed_count": 0,
            "skipped": 0,
            "failures": []
        }
        
        # Try to parse JSON output first
        try:
            # Look for JSON in the output
            json_match = re.search(r'\{.*"testResults".*\}', stdout, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                result["total"] = data.get("numTotalTests", 0)
                result["passed_count"] = data.get("numPassedTests", 0)
                result["failed_count"] = data.get("numFailedTests", 0)
                result["skipped"] = data.get("numPendingTests", 0)
                
                # Extract failures
                for test_result in data.get("testResults", []):
                    for assertion_result in test_result.get("assertionResults", []):
                        if assertion_result.get("status") == "failed":
                            result["failures"].append({
                                "test": assertion_result.get("title", "Unknown"),
                                "file": test_result.get("name", "Unknown"),
                                "error": assertion_result.get("failureMessages", [""])[0]
                            })
                
                return result
        except Exception:
            pass
        
        # Fallback to text parsing
        # Parse summary: "Tests: 1 failed, 4 passed, 5 total"
        total_pattern = r'Tests:.*?(\d+)\s+total'
        total_match = re.search(total_pattern, stdout)
        if total_match:
            result["total"] = int(total_match.group(1))
        
        passed_pattern = r'(\d+)\s+passed'
        passed_match = re.search(passed_pattern, stdout)
        if passed_match:
            result["passed_count"] = int(passed_match.group(1))
        
        failed_pattern = r'(\d+)\s+failed'
        failed_match = re.search(failed_pattern, stdout)
        if failed_match:
            result["failed_count"] = int(failed_match.group(1))
        
        skipped_pattern = r'(\d+)\s+skipped'
        skipped_match = re.search(skipped_pattern, stdout)
        if skipped_match:
            result["skipped"] = int(skipped_match.group(1))
        
        # Parse failures (simple pattern)
        failure_pattern = r'●\s+(.*?)\n\s+(.*?)\n\s+(.+?)(?=\n\s*●|\n\s*Test Suites:|\Z)'
        for match in re.finditer(failure_pattern, stdout, re.DOTALL):
            test_name = match.group(1).strip()
            file_info = match.group(2).strip()
            error_msg = match.group(3).strip()
            
            # Extract file path from file info
            file_match = re.search(r'([\w/\.]+\.test\.\w+)', file_info)
            file_path = file_match.group(1) if file_match else "Unknown"
            
            result["failures"].append({
                "test": test_name,
                "file": file_path,
                "error": error_msg.split('\n')[0]
            })
        
        return result
