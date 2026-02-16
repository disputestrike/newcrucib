"""
Code execution and validation system for generated code.
Executes code in isolated environments and validates it works.
"""
import asyncio
import tempfile
import shutil
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional


class CodeExecutor:
    """Executes and validates generated code in sandboxed environments"""
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
    
    async def validate_frontend(
        self, 
        files: Dict[str, str], 
        framework: str = "React"
    ) -> Dict[str, Any]:
        """
        Validate frontend by running npm install + npm run build
        
        Args:
            files: Dictionary of file paths to content
            framework: Frontend framework (React, Vue, Angular, etc.)
        
        Returns:
            {
                "valid": bool,
                "stage": "install|build|success",
                "error": str or None,
                "build_time": float,
                "build_output": str
            }
        """
        temp_dir = None
        start_time = time.time()
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="frontend_validate_")
            
            # Write all files
            for file_path, content in files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Ensure package.json exists
            package_json_path = os.path.join(temp_dir, "package.json")
            if not os.path.exists(package_json_path):
                return {
                    "valid": False,
                    "stage": "validation",
                    "error": "No package.json found",
                    "build_time": time.time() - start_time,
                    "build_output": ""
                }
            
            # Run npm install (120s timeout)
            install_result = await self._run_command(
                ["npm", "install"],
                cwd=temp_dir,
                timeout=120
            )
            
            if install_result["returncode"] != 0:
                return {
                    "valid": False,
                    "stage": "install",
                    "error": f"npm install failed: {install_result['stderr']}",
                    "build_time": time.time() - start_time,
                    "build_output": install_result["stdout"] + install_result["stderr"]
                }
            
            # Run npm run build (180s timeout)
            build_result = await self._run_command(
                ["npm", "run", "build"],
                cwd=temp_dir,
                timeout=180
            )
            
            build_time = time.time() - start_time
            
            if build_result["returncode"] != 0:
                return {
                    "valid": False,
                    "stage": "build",
                    "error": f"npm run build failed: {build_result['stderr']}",
                    "build_time": build_time,
                    "build_output": build_result["stdout"] + build_result["stderr"]
                }
            
            return {
                "valid": True,
                "stage": "success",
                "error": None,
                "build_time": build_time,
                "build_output": build_result["stdout"]
            }
            
        except asyncio.TimeoutError:
            return {
                "valid": False,
                "stage": "timeout",
                "error": "Validation exceeded timeout",
                "build_time": time.time() - start_time,
                "build_output": "",
                "suggestion": "Code may be too complex or has infinite loops"
            }
        except Exception as e:
            return {
                "valid": False,
                "stage": "unknown",
                "error": str(e),
                "build_time": time.time() - start_time,
                "build_output": "",
                "traceback": traceback.format_exc()
            }
        finally:
            # Clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
    
    async def validate_backend(
        self,
        files: Dict[str, str],
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Validate backend syntax and dependencies
        
        For Python:
        - Check syntax with ast.parse()
        - Install dependencies
        - Run static type checking if applicable
        
        For Node.js/TypeScript:
        - Run npm install
        - Run tsc --noEmit for TypeScript
        - Check for syntax errors
        
        Args:
            files: Dictionary of file paths to content
            language: Backend language (Python, Node.js, TypeScript)
        
        Returns:
            {
                "valid": bool,
                "stage": "syntax|dependencies|typecheck|success",
                "error": str or None,
                "files_checked": int
            }
        """
        import ast
        
        try:
            language_lower = language.lower()
            files_checked = 0
            
            if language_lower == "python":
                # Check Python syntax with ast.parse()
                syntax_errors = []
                for file_path, content in files.items():
                    if file_path.endswith('.py'):
                        try:
                            ast.parse(content)
                            files_checked += 1
                        except SyntaxError as e:
                            syntax_errors.append(f"{file_path}: {str(e)}")
                
                if syntax_errors:
                    return {
                        "valid": False,
                        "stage": "syntax",
                        "error": "; ".join(syntax_errors),
                        "files_checked": files_checked
                    }
                
                # Check for requirements.txt and validate dependencies
                if "requirements.txt" in files:
                    temp_dir = None
                    try:
                        temp_dir = tempfile.mkdtemp(prefix="backend_validate_")
                        req_path = os.path.join(temp_dir, "requirements.txt")
                        with open(req_path, 'w', encoding='utf-8') as f:
                            f.write(files["requirements.txt"])
                        
                        # Try to install (with timeout)
                        result = await self._run_command(
                            ["pip", "install", "-r", "requirements.txt", "--dry-run"],
                            cwd=temp_dir,
                            timeout=30
                        )
                        
                        if result["returncode"] != 0:
                            return {
                                "valid": False,
                                "stage": "dependencies",
                                "error": f"Dependency check failed: {result['stderr']}",
                                "files_checked": files_checked
                            }
                    finally:
                        if temp_dir and os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)
                
                return {
                    "valid": True,
                    "stage": "success",
                    "error": None,
                    "files_checked": files_checked
                }
            
            elif language_lower in ("node.js", "nodejs", "javascript", "typescript"):
                temp_dir = None
                try:
                    temp_dir = tempfile.mkdtemp(prefix="backend_validate_")
                    
                    # Write all files
                    for file_path, content in files.items():
                        full_path = os.path.join(temp_dir, file_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        if file_path.endswith(('.js', '.ts', '.tsx')):
                            files_checked += 1
                    
                    # Run npm install if package.json exists
                    if "package.json" in files:
                        result = await self._run_command(
                            ["npm", "install"],
                            cwd=temp_dir,
                            timeout=60
                        )
                        
                        if result["returncode"] != 0:
                            return {
                                "valid": False,
                                "stage": "dependencies",
                                "error": f"npm install failed: {result['stderr']}",
                                "files_checked": files_checked
                            }
                    
                    # Run TypeScript type checking if applicable
                    if language_lower == "typescript" or any(f.endswith(('.ts', '.tsx')) for f in files.keys()):
                        result = await self._run_command(
                            ["npx", "tsc", "--noEmit"],
                            cwd=temp_dir,
                            timeout=30
                        )
                        
                        if result["returncode"] != 0:
                            return {
                                "valid": False,
                                "stage": "typecheck",
                                "error": f"TypeScript check failed: {result['stderr']}",
                                "files_checked": files_checked
                            }
                    
                    return {
                        "valid": True,
                        "stage": "success",
                        "error": None,
                        "files_checked": files_checked
                    }
                finally:
                    if temp_dir and os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
            
            else:
                return {
                    "valid": False,
                    "stage": "unknown",
                    "error": f"Unsupported language: {language}",
                    "files_checked": 0
                }
        
        except Exception as e:
            return {
                "valid": False,
                "stage": "unknown",
                "error": str(e),
                "files_checked": files_checked if 'files_checked' in locals() else 0,
                "traceback": traceback.format_exc()
            }
    
    async def run_tests(
        self,
        files: Dict[str, str],
        test_command: str,
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Run test suite and return results
        
        Args:
            files: Dictionary of file paths to content
            test_command: Command to run tests (e.g., "pytest", "npm test")
            language: Language of the tests
        
        Returns:
            {
                "passed": bool,
                "stdout": str,
                "stderr": str,
                "duration": float,
                "tests_run": int,
                "tests_passed": int,
                "tests_failed": int,
                "coverage": float or None
            }
        """
        temp_dir = None
        start_time = time.time()
        
        try:
            temp_dir = tempfile.mkdtemp(prefix="test_run_")
            
            # Write all files
            for file_path, content in files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Install dependencies first
            if language.lower() == "python" and "requirements.txt" in files:
                await self._run_command(
                    ["pip", "install", "-r", "requirements.txt"],
                    cwd=temp_dir,
                    timeout=60
                )
            elif "package.json" in files:
                await self._run_command(
                    ["npm", "install"],
                    cwd=temp_dir,
                    timeout=60
                )
            
            # Run tests
            cmd = test_command.split()
            result = await self._run_command(
                cmd,
                cwd=temp_dir,
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            
            # Parse output to extract test counts
            tests_run = 0
            tests_passed = 0
            tests_failed = 0
            coverage = None
            
            # Simple parsing for pytest and jest
            output = result["stdout"] + result["stderr"]
            if "pytest" in test_command:
                # Look for patterns like "5 passed in 0.12s"
                import re
                passed_match = re.search(r'(\d+) passed', output)
                failed_match = re.search(r'(\d+) failed', output)
                if passed_match:
                    tests_passed = int(passed_match.group(1))
                if failed_match:
                    tests_failed = int(failed_match.group(1))
                tests_run = tests_passed + tests_failed
                
                # Look for coverage
                coverage_match = re.search(r'TOTAL.*?(\d+)%', output)
                if coverage_match:
                    coverage = float(coverage_match.group(1))
            
            elif "jest" in test_command or "vitest" in test_command:
                import re
                # Look for "Tests: 1 failed, 4 passed, 5 total"
                test_match = re.search(r'Tests:.*?(\d+) total', output)
                passed_match = re.search(r'(\d+) passed', output)
                failed_match = re.search(r'(\d+) failed', output)
                
                if test_match:
                    tests_run = int(test_match.group(1))
                if passed_match:
                    tests_passed = int(passed_match.group(1))
                if failed_match:
                    tests_failed = int(failed_match.group(1))
            
            return {
                "passed": result["returncode"] == 0,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "duration": duration,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "coverage": coverage
            }
        
        except asyncio.TimeoutError:
            return {
                "passed": False,
                "stdout": "",
                "stderr": f"Test execution exceeded {self.timeout}s timeout",
                "duration": time.time() - start_time,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "coverage": None
            }
        except Exception as e:
            return {
                "passed": False,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "coverage": None,
                "traceback": traceback.format_exc()
            }
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
    
    async def _run_command(
        self,
        cmd: List[str],
        cwd: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Helper to run shell commands with timeout
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory
            timeout: Timeout in seconds
        
        Returns:
            {
                "returncode": int,
                "stdout": str,
                "stderr": str,
                "duration": float
            }
        """
        start_time = time.time()
        timeout = timeout or self.timeout
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "duration": time.time() - start_time
            }
        
        except asyncio.TimeoutError:
            # Kill the process
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            raise
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time
            }
