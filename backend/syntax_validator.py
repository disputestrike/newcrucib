"""
Syntax Validator - Syntax checking for multiple programming languages
Validates code syntax without execution.
"""

import ast
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SyntaxValidator:
    """Validate syntax for various programming languages"""
    
    def validate_python(self, code: str) -> Dict[str, Any]:
        """
        Validate Python code syntax.
        
        Args:
            code: Python code string
            
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "line_count": int
            }
        """
        errors = []
        warnings = []
        
        try:
            # Try to parse as AST
            ast.parse(code)
            
            # Check for common issues
            lines = code.split('\n')
            line_count = len(lines)
            
            # Warn about missing docstrings in functions
            if 'def ' in code:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not ast.get_docstring(node):
                            warnings.append(f"Function '{node.name}' missing docstring")
            
            return {
                "valid": True,
                "errors": [],
                "warnings": warnings,
                "line_count": line_count
            }
        
        except SyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.msg}")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "line_count": len(code.split('\n'))
            }
        except Exception as e:
            errors.append(str(e))
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "line_count": len(code.split('\n'))
            }
    
    def validate_javascript(self, code: str) -> Dict[str, Any]:
        """
        Validate JavaScript/TypeScript code syntax (basic checks).
        
        Args:
            code: JavaScript/TypeScript code string
            
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "line_count": int
            }
        """
        errors = []
        warnings = []
        lines = code.split('\n')
        line_count = len(lines)
        
        # Check for unmatched brackets
        if code.count('{') != code.count('}'):
            errors.append("Unmatched curly braces")
        if code.count('(') != code.count(')'):
            errors.append("Unmatched parentheses")
        if code.count('[') != code.count(']'):
            errors.append("Unmatched square brackets")
        
        # Check for common syntax patterns
        if 'import' in code and 'from' not in code and 'require' not in code:
            # Check if it's ES6 imports without from
            if re.search(r'import\s+\w+\s*;', code):
                errors.append("Import statement missing 'from' clause")
        
        # Check for var usage (warn about let/const)
        if re.search(r'\bvar\s+', code):
            warnings.append("Consider using 'let' or 'const' instead of 'var'")
        
        # Check for console.log (warn in production)
        if 'console.log' in code:
            warnings.append("Remove console.log statements before production")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "line_count": line_count
        }
    
    def validate_react_component(self, code: str) -> Dict[str, Any]:
        """
        Validate React component code.
        
        Args:
            code: React component code (JSX/TSX)
            
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str],
                "component_name": Optional[str]
            }
        """
        errors = []
        warnings = []
        component_name = None
        
        # First run JavaScript validation
        js_result = self.validate_javascript(code)
        errors.extend(js_result["errors"])
        warnings.extend(js_result["warnings"])
        
        # Check for React import
        if 'import React' not in code and "import { " not in code and "from 'react'" not in code:
            warnings.append("Missing React import")
        
        # Try to find component name
        # Look for function components
        func_match = re.search(r'function\s+(\w+)', code)
        if func_match:
            component_name = func_match.group(1)
        else:
            # Look for const/let components
            const_match = re.search(r'(?:const|let)\s+(\w+)\s*=', code)
            if const_match:
                component_name = const_match.group(1)
        
        # Check for JSX syntax
        has_jsx = '<' in code and '>' in code and ('return' in code or '=>' in code)
        if not has_jsx:
            warnings.append("Component doesn't appear to return JSX")
        
        # Check for export
        if 'export' not in code:
            warnings.append("Component not exported")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "component_name": component_name
        }
    
    def validate_sql(self, code: str) -> Dict[str, Any]:
        """
        Validate SQL code (basic checks).
        
        Args:
            code: SQL code string
            
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        errors = []
        warnings = []
        
        # Check for common SQL keywords
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        has_sql = any(keyword.lower() in code.lower() for keyword in sql_keywords)
        
        if not has_sql:
            warnings.append("No SQL keywords found")
        
        # Check for missing semicolons
        statements = [s.strip() for s in code.split(';') if s.strip()]
        if statements and not code.rstrip().endswith(';'):
            warnings.append("SQL statement should end with semicolon")
        
        # Check for SELECT without FROM
        if re.search(r'\bSELECT\b(?!.*\bFROM\b)', code, re.IGNORECASE | re.DOTALL):
            # Allow SELECT without FROM for simple queries like SELECT 1
            if not re.search(r'\bSELECT\s+[\d\*]', code, re.IGNORECASE):
                warnings.append("SELECT statement without FROM clause")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def validate_json(self, code: str) -> Dict[str, Any]:
        """
        Validate JSON syntax.
        
        Args:
            code: JSON string
            
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "parsed": Optional[dict]
            }
        """
        import json
        
        try:
            parsed = json.loads(code)
            return {
                "valid": True,
                "errors": [],
                "parsed": parsed
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Line {e.lineno}: {e.msg}"],
                "parsed": None
            }
