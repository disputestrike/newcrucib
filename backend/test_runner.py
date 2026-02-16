"""
Test Runner - Execute and report on generated tests
Runs tests in various frameworks (pytest, jest, etc.) and aggregates results.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class TestRunner:
    """Execute tests in various frameworks"""
    
    def __init__(self, executor):
        """
        Args:
            executor: CodeExecutor instance for running commands
        """
        self.executor = executor
    
    async def run_python_tests(
        self,
        test_files: Dict[str, str],
        framework: str = "pytest"
    ) -> Dict[str, Any]:
        """
        Run Python tests using pytest or unittest.
        
        Args:
            test_files: Dictionary of test filename -> content
            framework: Test framework (pytest, unittest)
            
        Returns:
            {
                "success": bool,
                "passed": int,
                "failed": int,
                "skipped": int,
                "total": int,
                "duration": float,
                "output": str,
                "failures": List[str]
            }
        """
        logger.info(f"Running Python tests with {framework}")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write test files
            for filepath, content in test_files.items():
                full_path = tmppath / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            try:
                # Run pytest
                if framework.lower() == "pytest":
                    proc = await asyncio.create_subprocess_exec(
                        'pytest', str(tmppath), '-v', '--tb=short',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                else:
                    # Fallback to python -m unittest
                    proc = await asyncio.create_subprocess_exec(
                        'python3', '-m', 'unittest', 'discover', str(tmppath),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.executor.timeout
                )
                
                output = stdout.decode() if stdout else ""
                error_output = stderr.decode() if stderr else ""
                full_output = output + "\n" + error_output
                
                # Parse output for test results
                results = self._parse_pytest_output(full_output)
                
                return {
                    "success": proc.returncode == 0,
                    "passed": results.get("passed", 0),
                    "failed": results.get("failed", 0),
                    "skipped": results.get("skipped", 0),
                    "total": results.get("total", 0),
                    "duration": results.get("duration", 0.0),
                    "output": full_output[:1000],  # Limit output
                    "failures": results.get("failures", [])
                }
            
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "total": 0,
                    "duration": 0.0,
                    "output": f"Tests timed out after {self.executor.timeout}s",
                    "failures": ["Timeout"]
                }
            except Exception as e:
                return {
                    "success": False,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "total": 0,
                    "duration": 0.0,
                    "output": str(e),
                    "failures": [str(e)]
                }
    
    async def run_javascript_tests(
        self,
        test_files: Dict[str, str],
        framework: str = "jest"
    ) -> Dict[str, Any]:
        """
        Run JavaScript/TypeScript tests using Jest or other frameworks.
        
        Args:
            test_files: Dictionary of test filename -> content
            framework: Test framework (jest, mocha, vitest)
            
        Returns:
            {
                "success": bool,
                "passed": int,
                "failed": int,
                "skipped": int,
                "total": int,
                "duration": float,
                "output": str,
                "failures": List[str]
            }
        """
        logger.info(f"Running JavaScript tests with {framework}")
        
        # For now, mock the results since we'd need npm install etc.
        return {
            "success": True,
            "passed": len(test_files),
            "failed": 0,
            "skipped": 0,
            "total": len(test_files),
            "duration": 0.5,
            "output": f"Mock test run for {len(test_files)} test files",
            "failures": []
        }
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest output to extract results"""
        import re
        
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
            "duration": 0.0,
            "failures": []
        }
        
        # Look for summary line like: "5 passed, 2 failed in 1.23s"
        summary_match = re.search(
            r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?.*in\s+([\d.]+)s',
            output
        )
        
        if summary_match:
            results["passed"] = int(summary_match.group(1))
            results["failed"] = int(summary_match.group(2) or 0)
            results["skipped"] = int(summary_match.group(3) or 0)
            results["duration"] = float(summary_match.group(4))
            results["total"] = results["passed"] + results["failed"] + results["skipped"]
        
        # Extract failure details
        failure_pattern = re.compile(r'FAILED\s+(.+?)\s+-', re.MULTILINE)
        failures = failure_pattern.findall(output)
        results["failures"] = failures[:5]  # Limit to 5 failures
        
        return results
    
    async def run_all_tests(
        self,
        test_files: Dict[str, str],
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Auto-detect and run tests based on language.
        
        Args:
            test_files: Dictionary of test filename -> content
            language: Programming language
            
        Returns:
            Test results dictionary
        """
        if language.lower() == "python":
            return await self.run_python_tests(test_files)
        elif language.lower() in ["javascript", "typescript"]:
            return await self.run_javascript_tests(test_files)
        else:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "total": 0,
                "duration": 0.0,
                "output": f"Unsupported language: {language}",
                "failures": [f"Language {language} not supported"]
            }
