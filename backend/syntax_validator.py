"""
Syntax validation for various programming languages.
Validates code syntax without executing it.
"""
import ast
import json
import re
import tempfile
import os
import asyncio
from typing import Dict, Any


class SyntaxValidator:
    """Validates code syntax using AST parsers"""
    
    @staticmethod
    def validate_python(code: str) -> Dict[str, Any]:
        """
        Validate Python syntax using ast.parse()
        
        Args:
            code: Python code string
        
        Returns:
            {
                "valid": bool,
                "error": str or None,
                "line": int or None,
                "issues": List[str]
            }
        """
        issues = []
        
        try:
            # Parse the code
            ast.parse(code)
            
            # Additional checks
            if not code.strip():
                issues.append("Empty code")
            
            # Check for common issues
            if "import *" in code:
                issues.append("Wildcard imports found (consider explicit imports)")
            
            return {
                "valid": True,
                "error": None,
                "line": None,
                "issues": issues
            }
        
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"SyntaxError: {e.msg}",
                "line": e.lineno,
                "issues": issues
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "line": None,
                "issues": issues
            }
    
    @staticmethod
    def validate_javascript(code: str) -> Dict[str, Any]:
        """
        Basic JavaScript syntax validation
        Check for:
        - Balanced braces, brackets, parentheses
        - Valid variable declarations
        - Import/export statements
        
        Args:
            code: JavaScript code string
        
        Returns:
            Same structure as validate_python
        """
        issues = []
        
        try:
            if not code.strip():
                return {
                    "valid": False,
                    "error": "Empty code",
                    "line": None,
                    "issues": ["Empty code"]
                }
            
            # Check balanced braces, brackets, parentheses
            stack = []
            pairs = {'(': ')', '[': ']', '{': '}'}
            line_num = 1
            
            # Remove strings and comments to avoid false positives
            cleaned_code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
            cleaned_code = re.sub(r'/\*.*?\*/', '', cleaned_code, flags=re.DOTALL)
            cleaned_code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cleaned_code)
            cleaned_code = re.sub(r"'(?:[^'\\]|\\.)*'", "''", cleaned_code)
            cleaned_code = re.sub(r'`(?:[^`\\]|\\.)*`', '``', cleaned_code)
            
            for i, char in enumerate(cleaned_code):
                if char == '\n':
                    line_num += 1
                
                if char in pairs:
                    stack.append((char, line_num))
                elif char in pairs.values():
                    if not stack:
                        return {
                            "valid": False,
                            "error": f"Unmatched closing '{char}'",
                            "line": line_num,
                            "issues": issues
                        }
                    opening, open_line = stack.pop()
                    if pairs[opening] != char:
                        return {
                            "valid": False,
                            "error": f"Mismatched brackets: '{opening}' opened at line {open_line}, closed with '{char}'",
                            "line": line_num,
                            "issues": issues
                        }
            
            if stack:
                opening, open_line = stack[0]
                return {
                    "valid": False,
                    "error": f"Unclosed '{opening}' from line {open_line}",
                    "line": open_line,
                    "issues": issues
                }
            
            # Check for valid variable declarations
            invalid_var_pattern = r'\b(var|let|const)\s+\d+'
            if re.search(invalid_var_pattern, code):
                issues.append("Variable names cannot start with numbers")
            
            # Check for common syntax errors
            if re.search(r'function\s*\(', code):
                issues.append("Anonymous function without assignment may cause issues")
            
            return {
                "valid": True,
                "error": None,
                "line": None,
                "issues": issues
            }
        
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "line": None,
                "issues": issues
            }
    
    @staticmethod
    async def validate_typescript(code: str, temp_dir: str = None) -> Dict[str, Any]:
        """
        Validate TypeScript using tsc compiler
        Write to temp file, run tsc --noEmit
        
        Args:
            code: TypeScript code string
            temp_dir: Optional temp directory (created if not provided)
        
        Returns:
            Same structure as validate_python
        """
        should_cleanup = False
        
        try:
            if temp_dir is None:
                temp_dir = tempfile.mkdtemp(prefix="ts_validate_")
                should_cleanup = True
            
            # Write code to temp file
            temp_file = os.path.join(temp_dir, "temp.ts")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Create minimal tsconfig.json
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "strict": False,
                    "noEmit": True,
                    "skipLibCheck": True
                }
            }
            tsconfig_path = os.path.join(temp_dir, "tsconfig.json")
            with open(tsconfig_path, 'w', encoding='utf-8') as f:
                json.dump(tsconfig, f)
            
            # Run tsc
            process = await asyncio.create_subprocess_exec(
                "npx", "tsc", "--noEmit",
                cwd=temp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=10
            )
            
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
            
            if process.returncode != 0:
                # Parse error message
                error_lines = output.strip().split('\n')
                error_msg = error_lines[0] if error_lines else "TypeScript compilation failed"
                
                # Try to extract line number
                line_match = re.search(r'temp\.ts\((\d+),', output)
                line_num = int(line_match.group(1)) if line_match else None
                
                return {
                    "valid": False,
                    "error": error_msg,
                    "line": line_num,
                    "issues": []
                }
            
            return {
                "valid": True,
                "error": None,
                "line": None,
                "issues": []
            }
        
        except asyncio.TimeoutError:
            return {
                "valid": False,
                "error": "TypeScript validation timeout",
                "line": None,
                "issues": []
            }
        except FileNotFoundError:
            return {
                "valid": False,
                "error": "TypeScript compiler (tsc) not found. Install with: npm install -g typescript",
                "line": None,
                "issues": []
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "line": None,
                "issues": []
            }
        finally:
            if should_cleanup and temp_dir and os.path.exists(temp_dir):
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
    
    @staticmethod
    def validate_react_component(code: str) -> Dict[str, Any]:
        """
        Validate React component structure:
        - Has import statements
        - Has export statement
        - Balanced JSX tags
        - Props are typed (if TypeScript)
        
        Args:
            code: React component code
        
        Returns:
            Validation result with specific React checks
        """
        issues = []
        
        try:
            if not code.strip():
                return {
                    "valid": False,
                    "error": "Empty component code",
                    "line": None,
                    "issues": ["Empty code"]
                }
            
            # Check for import statements
            if not re.search(r'import\s+', code):
                issues.append("No import statements found")
            
            # Check for React import (if not using new JSX transform)
            if 'React' not in code and '<' in code and '>' in code:
                issues.append("Consider importing React or using new JSX transform")
            
            # Check for export
            if not re.search(r'export\s+(default|const|function|class)', code):
                return {
                    "valid": False,
                    "error": "No export statement found",
                    "line": None,
                    "issues": issues
                }
            
            # Check for balanced JSX tags (simplified)
            jsx_pattern = r'<([A-Z][a-zA-Z0-9]*|[a-z][a-zA-Z0-9]*)'
            jsx_tags = re.findall(jsx_pattern, code)
            
            # Remove strings and comments for accurate JSX parsing
            cleaned_code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
            cleaned_code = re.sub(r'/\*.*?\*/', '', cleaned_code, flags=re.DOTALL)
            cleaned_code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cleaned_code)
            cleaned_code = re.sub(r"'(?:[^'\\]|\\.)*'", "''", cleaned_code)
            cleaned_code = re.sub(r'`(?:[^`\\]|\\.)*`', '``', cleaned_code)
            
            # Count JSX open and close tags
            open_tags = re.findall(r'<([A-Z][a-zA-Z0-9]*|[a-z][a-zA-Z0-9-]*)\b', cleaned_code)
            close_tags = re.findall(r'</([A-Z][a-zA-Z0-9]*|[a-z][a-zA-Z0-9-]*)>', cleaned_code)
            self_closing = re.findall(r'<[A-Za-z][a-zA-Z0-9-]*[^>]*/>', cleaned_code)
            
            # Adjust for self-closing tags
            open_count = len(open_tags) - len(self_closing)
            close_count = len(close_tags)
            
            if open_count != close_count:
                issues.append(f"Possibly unbalanced JSX tags: {open_count} opening, {close_count} closing")
            
            # Check for TypeScript props typing
            if code.endswith('.tsx') or ': ' in code:
                if re.search(r'function\s+\w+\s*\([^)]*\)', code):
                    if not re.search(r'function\s+\w+\s*\([^)]*:\s*\{', code):
                        issues.append("Consider typing component props for better type safety")
            
            # Check for key prop in map operations
            if '.map(' in code and 'key=' not in code:
                issues.append("Remember to add 'key' prop when using .map()")
            
            return {
                "valid": True,
                "error": None,
                "line": None,
                "issues": issues
            }
        
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "line": None,
                "issues": issues
            }
    
    @staticmethod
    def validate_json(content: str) -> Dict[str, Any]:
        """
        Validate JSON syntax
        
        Args:
            content: JSON string
        
        Returns:
            Same structure as validate_python
        """
        try:
            json.loads(content)
            return {
                "valid": True,
                "error": None,
                "line": None,
                "issues": []
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"JSONDecodeError: {e.msg}",
                "line": e.lineno,
                "issues": []
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "line": None,
                "issues": []
            }
