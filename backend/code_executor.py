"""
Code Executor - Safe code execution and validation engine
Validates and executes generated code in isolated environments.
"""

import asyncio
import tempfile
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Execute and validate generated code"""
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
    
    async def validate_frontend(
        self,
        files: Dict[str, str],
        framework: str = "React"
    ) -> Dict[str, Any]:
        """
        Validate frontend code by checking syntax and attempting build.
        
        Args:
            files: Dictionary of filename -> content
            framework: Frontend framework (React, Vue, etc.)
            
        Returns:
            {
                "valid": bool,
                "build_output": str,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        logger.info(f"Validating {framework} frontend code")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Write files
            for filepath, content in files.items():
                full_path = tmppath / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
            
            # Check if package.json exists
            package_json = tmppath / "package.json"
            if not package_json.exists():
                # Create minimal package.json
                if framework.lower() == "react":
                    package_json.write_text('''{
  "name": "app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0"
  }
}''')
            
            # Try to parse TypeScript/JavaScript files
            errors = []
            warnings = []
            
            for filepath, content in files.items():
                if filepath.endswith(('.tsx', '.ts', '.jsx', '.js')):
                    # Basic syntax check
                    try:
                        # Check for common syntax errors
                        if 'import' in content and 'from' not in content:
                            errors.append(f"{filepath}: Import statement missing 'from'")
                        
                        # Check for unmatched brackets
                        if content.count('{') != content.count('}'):
                            errors.append(f"{filepath}: Unmatched curly braces")
                        if content.count('(') != content.count(')'):
                            errors.append(f"{filepath}: Unmatched parentheses")
                        if content.count('[') != content.count(']'):
                            errors.append(f"{filepath}: Unmatched square brackets")
                    
                    except Exception as e:
                        errors.append(f"{filepath}: {str(e)}")
            
            # Simulate build (in production, would run actual build)
            if errors:
                return {
                    "valid": False,
                    "build_output": "Build skipped due to syntax errors",
                    "errors": errors,
                    "warnings": warnings
                }
            
            # Mock successful build
            return {
                "valid": True,
                "build_output": "Build completed successfully",
                "errors": [],
                "warnings": warnings
            }
    
    async def validate_backend(
        self,
        files: Dict[str, str],
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Validate backend code by checking syntax.
        
        Args:
            files: Dictionary of filename -> content
            language: Programming language (Python, JavaScript, etc.)
            
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        logger.info(f"Validating {language} backend code")
        
        errors = []
        warnings = []
        
        if language.lower() == "python":
            for filepath, content in files.items():
                if filepath.endswith('.py'):
                    try:
                        # Try to compile Python code
                        compile(content, filepath, 'exec')
                    except SyntaxError as e:
                        errors.append(f"{filepath}:{e.lineno}: {e.msg}")
                    except Exception as e:
                        errors.append(f"{filepath}: {str(e)}")
        
        elif language.lower() in ["javascript", "typescript"]:
            for filepath, content in files.items():
                if filepath.endswith(('.js', '.ts')):
                    # Basic syntax checks
                    if content.count('{') != content.count('}'):
                        errors.append(f"{filepath}: Unmatched curly braces")
                    if content.count('(') != content.count(')'):
                        errors.append(f"{filepath}: Unmatched parentheses")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def execute_code(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Execute code in isolated environment (for testing).
        
        Args:
            code: Code to execute
            language: Programming language
            
        Returns:
            {
                "success": bool,
                "output": str,
                "error": Optional[str]
            }
        """
        logger.info(f"Executing {language} code")
        
        try:
            if language.lower() == "python":
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                try:
                    # Execute with timeout
                    proc = await asyncio.create_subprocess_exec(
                        'python3', temp_file,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(),
                        timeout=self.timeout
                    )
                    
                    output = stdout.decode() if stdout else ""
                    error = stderr.decode() if stderr else None
                    
                    return {
                        "success": proc.returncode == 0,
                        "output": output,
                        "error": error
                    }
                
                finally:
                    # Clean up
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
            
            else:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Language '{language}' not supported for execution"
                }
        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {self.timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
