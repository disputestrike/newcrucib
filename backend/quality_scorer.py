"""
Quality Scorer - Code quality metrics and scoring system
Analyzes generated code for quality, maintainability, and best practices.
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class QualityScorer:
    """Score code quality across multiple dimensions"""
    
    def score_code(
        self,
        files: Dict[str, str],
        language: str = "Python"
    ) -> Dict[str, Any]:
        """
        Score code quality across multiple metrics.
        
        Args:
            files: Dictionary of filename -> content
            language: Primary programming language
            
        Returns:
            {
                "overall_score": int (0-100),
                "metrics": {
                    "readability": int,
                    "maintainability": int,
                    "complexity": int,
                    "documentation": int,
                    "best_practices": int,
                    "security": int
                },
                "details": {
                    "total_lines": int,
                    "code_lines": int,
                    "comment_lines": int,
                    "blank_lines": int,
                    "files_analyzed": int
                },
                "issues": List[str],
                "suggestions": List[str]
            }
        """
        logger.info(f"Scoring {len(files)} files in {language}")
        
        metrics = {
            "readability": 0,
            "maintainability": 0,
            "complexity": 0,
            "documentation": 0,
            "best_practices": 0,
            "security": 0
        }
        
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        issues = []
        suggestions = []
        
        for filepath, content in files.items():
            if not content:
                continue
            
            lines = content.split('\n')
            total_lines += len(lines)
            
            # Count line types
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    blank_lines += 1
                elif stripped.startswith('#') or stripped.startswith('//'):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            # Language-specific scoring
            if language.lower() == "python":
                file_metrics = self._score_python_file(filepath, content)
            elif language.lower() in ["javascript", "typescript"]:
                file_metrics = self._score_javascript_file(filepath, content)
            else:
                file_metrics = self._score_generic_file(filepath, content)
            
            # Aggregate metrics
            for key in metrics:
                metrics[key] += file_metrics["metrics"].get(key, 0)
            
            issues.extend(file_metrics.get("issues", []))
            suggestions.extend(file_metrics.get("suggestions", []))
        
        # Average metrics across files
        num_files = len(files)
        if num_files > 0:
            for key in metrics:
                metrics[key] = min(100, metrics[key] // num_files)
        
        # Calculate overall score (weighted average)
        overall_score = int(
            metrics["readability"] * 0.20 +
            metrics["maintainability"] * 0.20 +
            metrics["complexity"] * 0.15 +
            metrics["documentation"] * 0.15 +
            metrics["best_practices"] * 0.20 +
            metrics["security"] * 0.10
        )
        
        return {
            "overall_score": overall_score,
            "metrics": metrics,
            "details": {
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "blank_lines": blank_lines,
                "files_analyzed": num_files
            },
            "issues": issues[:10],  # Limit to top 10
            "suggestions": suggestions[:10]  # Limit to top 10
        }
    
    def _score_python_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Score a Python file"""
        metrics = {
            "readability": 70,
            "maintainability": 70,
            "complexity": 70,
            "documentation": 60,
            "best_practices": 70,
            "security": 80
        }
        issues = []
        suggestions = []
        
        lines = content.split('\n')
        
        # Readability checks
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            metrics["readability"] -= min(20, len(long_lines) * 2)
            issues.append(f"{filepath}: {len(long_lines)} lines exceed 100 characters")
        
        # Documentation checks
        has_module_docstring = content.strip().startswith('"""') or content.strip().startswith("'''")
        if not has_module_docstring:
            metrics["documentation"] -= 20
            suggestions.append(f"{filepath}: Add module-level docstring")
        
        func_count = content.count('def ')
        docstring_pattern = r'def\s+\w+[^:]*:\s*"""'
        docstring_count = len(re.findall(docstring_pattern, content, re.MULTILINE))
        if func_count > 0 and docstring_count < func_count:
            metrics["documentation"] -= min(30, (func_count - docstring_count) * 5)
            suggestions.append(f"{filepath}: {func_count - docstring_count} functions missing docstrings")
        
        # Complexity checks
        # Count nested levels (approximation)
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        
        if max_indent > 4:
            metrics["complexity"] -= (max_indent - 4) * 10
            issues.append(f"{filepath}: Deep nesting detected (level {max_indent})")
        
        # Best practices
        if 'import *' in content:
            metrics["best_practices"] -= 15
            issues.append(f"{filepath}: Avoid wildcard imports")
        
        if re.search(r'except\s*:', content):
            metrics["best_practices"] -= 10
            issues.append(f"{filepath}: Avoid bare except clauses")
        
        # Security checks
        if 'eval(' in content or 'exec(' in content:
            metrics["security"] -= 30
            issues.append(f"{filepath}: Avoid eval() and exec() - security risk")
        
        if re.search(r'password\s*=\s*["\']', content, re.IGNORECASE):
            metrics["security"] -= 20
            issues.append(f"{filepath}: Hardcoded password detected")
        
        return {
            "metrics": metrics,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _score_javascript_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Score a JavaScript/TypeScript file"""
        metrics = {
            "readability": 70,
            "maintainability": 70,
            "complexity": 70,
            "documentation": 60,
            "best_practices": 70,
            "security": 80
        }
        issues = []
        suggestions = []
        
        # Readability
        lines = content.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            metrics["readability"] -= min(20, len(long_lines) * 2)
        
        # Documentation
        if '/**' not in content and '//' not in content[:100]:
            metrics["documentation"] -= 20
            suggestions.append(f"{filepath}: Add file-level documentation")
        
        # Best practices
        if re.search(r'\bvar\s+', content):
            metrics["best_practices"] -= 10
            suggestions.append(f"{filepath}: Use 'let' or 'const' instead of 'var'")
        
        if 'console.log' in content:
            metrics["best_practices"] -= 5
            suggestions.append(f"{filepath}: Remove console.log statements")
        
        # Security
        if 'eval(' in content:
            metrics["security"] -= 30
            issues.append(f"{filepath}: Avoid eval() - security risk")
        
        if re.search(r'innerHTML\s*=', content):
            metrics["security"] -= 15
            issues.append(f"{filepath}: innerHTML can lead to XSS vulnerabilities")
        
        return {
            "metrics": metrics,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _score_generic_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Score a generic code file"""
        metrics = {
            "readability": 70,
            "maintainability": 70,
            "complexity": 70,
            "documentation": 60,
            "best_practices": 70,
            "security": 80
        }
        
        # Basic checks
        lines = content.split('\n')
        if len(lines) > 500:
            metrics["maintainability"] -= 10
        
        return {
            "metrics": metrics,
            "issues": [],
            "suggestions": []
        }
