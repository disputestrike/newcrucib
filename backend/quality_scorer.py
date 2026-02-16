"""
Code quality scoring system.
Scores code quality across multiple dimensions using heuristics and pattern matching.
"""
import re
import ast
from typing import Dict, List, Any, Tuple


class QualityScorer:
    """Scores code quality across multiple dimensions"""
    
    def score_code(
        self,
        files: Dict[str, str],
        language: str
    ) -> Dict[str, Any]:
        """
        Comprehensive code quality scoring
        
        Args:
            files: Dictionary of file paths to content
            language: Primary language (Python, JavaScript, TypeScript, etc.)
        
        Returns:
            {
                "overall_score": 0-100,
                "metrics": {
                    "complexity": 0-100,
                    "documentation": 0-100,
                    "error_handling": 0-100,
                    "testing": 0-100,
                    "security": 0-100,
                    "maintainability": 0-100
                },
                "issues": [...],
                "strengths": [...],
                "recommendations": [...]
            }
        """
        language_lower = language.lower()
        
        # Calculate individual metrics
        complexity_score, complexity_issues = self._calculate_complexity(files, language_lower)
        documentation_score = self._score_documentation(files)
        error_handling_score, error_issues = self._score_error_handling(files, language_lower)
        testing_score = self._score_testing(files)
        security_score, security_issues = self._score_security(files, language_lower)
        maintainability_score, maintainability_issues = self._score_maintainability(files)
        
        # Combine all issues
        all_issues = complexity_issues + error_issues + security_issues + maintainability_issues
        
        # Calculate overall score (weighted average)
        weights = {
            "complexity": 0.20,
            "documentation": 0.15,
            "error_handling": 0.20,
            "testing": 0.15,
            "security": 0.20,
            "maintainability": 0.10
        }
        
        overall_score = (
            complexity_score * weights["complexity"] +
            documentation_score * weights["documentation"] +
            error_handling_score * weights["error_handling"] +
            testing_score * weights["testing"] +
            security_score * weights["security"] +
            maintainability_score * weights["maintainability"]
        )
        
        # Identify strengths
        strengths = []
        if documentation_score >= 80:
            strengths.append("Good documentation")
        if error_handling_score >= 80:
            strengths.append("Good error handling")
        if testing_score >= 70:
            strengths.append("Comprehensive tests")
        if security_score >= 85:
            strengths.append("Good security practices")
        if complexity_score >= 80:
            strengths.append("Low complexity")
        
        # Generate recommendations
        recommendations = []
        if documentation_score < 60:
            recommendations.append("Add more documentation and comments")
        if complexity_score < 60:
            recommendations.append("Reduce code complexity by breaking down large functions")
        if error_handling_score < 60:
            recommendations.append("Improve error handling with try/catch blocks")
        if testing_score < 50:
            recommendations.append("Add more comprehensive tests")
        if security_score < 70:
            recommendations.append("Review security practices and input validation")
        if maintainability_score < 60:
            recommendations.append("Improve code organization and reduce duplication")
        
        return {
            "overall_score": round(overall_score, 1),
            "metrics": {
                "complexity": round(complexity_score, 1),
                "documentation": round(documentation_score, 1),
                "error_handling": round(error_handling_score, 1),
                "testing": round(testing_score, 1),
                "security": round(security_score, 1),
                "maintainability": round(maintainability_score, 1)
            },
            "issues": all_issues,
            "strengths": strengths,
            "recommendations": recommendations
        }
    
    def _calculate_complexity(self, files: Dict[str, str], language: str) -> Tuple[int, List[Dict]]:
        """
        Calculate cyclomatic complexity
        For Python: use AST analysis
        For JS/TS: count decision points
        
        Returns:
            (score: 0-100, issues: List)
        """
        issues = []
        total_complexity = 0
        function_count = 0
        
        try:
            if language == "python":
                for file_path, content in files.items():
                    if not file_path.endswith('.py'):
                        continue
                    
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                function_count += 1
                                complexity = self._calculate_python_complexity(node)
                                total_complexity += complexity
                                
                                if complexity > 10:
                                    issues.append({
                                        "severity": "high" if complexity > 15 else "medium",
                                        "category": "complexity",
                                        "file": file_path,
                                        "line": node.lineno,
                                        "message": f"Function '{node.name}' has high complexity (CC={complexity})",
                                        "suggestion": "Break into smaller functions"
                                    })
                    except Exception:
                        pass
            
            elif language in ("javascript", "typescript"):
                for file_path, content in files.items():
                    if not file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        continue
                    
                    # Count decision points (if, for, while, case, &&, ||, ?, etc.)
                    functions = re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>', content)
                    function_count += len(functions)
                    
                    # Simple heuristic: count control flow statements
                    decision_keywords = ['if', 'for', 'while', 'case', '&&', '||', '?', 'catch']
                    for keyword in decision_keywords:
                        total_complexity += content.count(keyword)
            
            # Calculate score (lower complexity = higher score)
            if function_count > 0:
                avg_complexity = total_complexity / function_count
                # Score: 100 for CC=1, 50 for CC=10, 0 for CC=20+
                score = max(0, min(100, 100 - (avg_complexity - 1) * 5))
            else:
                score = 100  # No functions found
            
            return score, issues
        
        except Exception:
            return 50, issues  # Default score on error
    
    def _calculate_python_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a Python function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Add 1 for each decision point
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Add for each boolean operator
                complexity += len(child.values) - 1
        
        return complexity
    
    def _score_documentation(self, files: Dict[str, str]) -> int:
        """
        Score documentation quality:
        - README exists and is comprehensive
        - Functions have docstrings/JSDoc
        - API endpoints documented
        - Comments explain why, not what
        
        Returns:
            Score 0-100
        """
        score = 0
        
        # Check for README
        readme_files = [f for f in files.keys() if f.lower().startswith('readme')]
        if readme_files:
            readme_content = files[readme_files[0]]
            if len(readme_content) > 200:
                score += 20
            if 'installation' in readme_content.lower() or 'setup' in readme_content.lower():
                score += 10
            if 'usage' in readme_content.lower() or 'example' in readme_content.lower():
                score += 10
        
        # Check for docstrings/comments in code files
        total_functions = 0
        documented_functions = 0
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                # Python docstrings
                functions = re.findall(r'def\s+\w+', content)
                total_functions += len(functions)
                
                # Count all docstrings (""" or ''')
                docstring_count = len(re.findall(r'"""', content)) // 2  # Pairs of """
                docstring_count += len(re.findall(r"'''", content)) // 2  # Pairs of '''
                
                # Assume module docstring + function docstrings
                # Give credit for having docstrings even if not every function has one
                if docstring_count > 0:
                    documented_functions += min(docstring_count, total_functions)
                
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                # JSDoc comments
                functions = re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>', content)
                total_functions += len(functions)
                
                # Count functions with JSDoc
                jsdoc_blocks = re.findall(r'/\*\*.*?\*/', content, re.DOTALL)
                documented_functions += len(jsdoc_blocks)
        
        # Score based on documentation ratio
        if total_functions > 0:
            doc_ratio = documented_functions / total_functions
            score += int(doc_ratio * 60)
        else:
            score += 30  # Default if no functions
        
        # Check for inline comments (count per file type)
        total_lines = sum(len(content.split('\n')) for content in files.values())
        total_comments = 0
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                total_comments += content.count('#')
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                total_comments += content.count('//')
        
        if total_lines > 0 and total_comments / total_lines > 0.05:
            score += 10
        
        return min(100, score)
    
    def _score_error_handling(self, files: Dict[str, str], language: str) -> Tuple[int, List[Dict]]:
        """
        Check for:
        - Try/catch blocks
        - Error return types
        - Validation of inputs
        - Proper error messages
        
        Returns:
            (score: 0-100, issues: List)
        """
        score = 0
        issues = []
        
        try_catch_count = 0
        validation_count = 0
        total_functions = 0
        
        for file_path, content in files.items():
            if language == "python" and file_path.endswith('.py'):
                # Count try/except blocks
                try_catch_count += content.count('try:')
                
                # Count validation patterns
                validation_count += content.count('if not ')
                validation_count += content.count('raise ValueError')
                validation_count += content.count('raise TypeError')
                
                # Count functions
                total_functions += len(re.findall(r'def\s+\w+', content))
                
            elif language in ("javascript", "typescript") and file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                # Count try/catch blocks
                try_catch_count += content.count('try {')
                
                # Count validation patterns
                validation_count += content.count('if (!') + content.count('if(!') 
                validation_count += content.count('throw ')
                
                # Count functions
                total_functions += len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>', content))
        
        # Score based on error handling presence
        if total_functions > 0:
            try_ratio = try_catch_count / max(1, total_functions)
            validation_ratio = validation_count / max(1, total_functions)
            
            # Try/catch blocks (40 points)
            score += min(40, int(try_ratio * 100))
            
            # Validation (40 points)
            score += min(40, int(validation_ratio * 80))
            
            # Bonus for good practices (20 points)
            if try_catch_count > 0:
                score += 10
            if validation_count > 0:
                score += 10
        else:
            score = 50  # Default if no functions
        
        # Generate issues
        if try_catch_count == 0 and total_functions > 0:
            issues.append({
                "severity": "medium",
                "category": "error_handling",
                "file": "global",
                "line": None,
                "message": "No try/catch blocks found",
                "suggestion": "Add error handling for operations that might fail"
            })
        
        return min(100, score), issues
    
    def _score_testing(self, files: Dict[str, str]) -> int:
        """
        Score test coverage:
        - Test files exist
        - Tests cover main functionality
        - Edge cases tested
        - Assertions are meaningful
        
        Returns:
            Score 0-100
        """
        score = 0
        
        # Check for test files
        test_files = [f for f in files.keys() if 'test' in f.lower() or 'spec' in f.lower()]
        
        if not test_files:
            return 0
        
        score += 30  # Base score for having tests
        
        # Analyze test content
        total_tests = 0
        total_assertions = 0
        
        for file_path in test_files:
            content = files[file_path]
            
            # Count test functions
            if file_path.endswith('.py'):
                total_tests += len(re.findall(r'def\s+test_\w+', content))
                total_assertions += content.count('assert ')
                
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                total_tests += content.count('it(') + content.count('test(')
                total_assertions += content.count('expect(')
        
        # Score based on number of tests
        if total_tests > 0:
            score += min(40, total_tests * 4)
        
        # Score based on assertions
        if total_assertions > 0:
            score += min(30, total_assertions * 2)
        
        return min(100, score)
    
    def _score_security(self, files: Dict[str, str], language: str) -> Tuple[int, List[Dict]]:
        """
        Check for common vulnerabilities:
        - SQL injection (parameterized queries?)
        - XSS (proper escaping?)
        - CSRF protection
        - Secrets in code
        - Input validation
        
        Returns:
            (score: 0-100, issues: List)
        """
        score = 100  # Start with perfect score, deduct for issues
        issues = []
        
        for file_path, content in files.items():
            # Check for hardcoded secrets
            secret_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password found"),
                (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key found"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret found"),
                (r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "Hardcoded token found"),
            ]
            
            for pattern, message in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip if it's a placeholder or environment variable reference
                    matched_text = match.group(0)
                    if 'YOUR_' in matched_text or 'ENTER_' in matched_text or 'process.env' in matched_text or 'os.environ' in matched_text:
                        continue
                    
                    score -= 15
                    issues.append({
                        "severity": "high",
                        "category": "security",
                        "file": file_path,
                        "line": content[:match.start()].count('\n') + 1,
                        "message": message,
                        "suggestion": "Use environment variables instead"
                    })
            
            # Check for SQL injection vulnerabilities
            if language == "python":
                # Look for string formatting in SQL queries
                if re.search(r'execute\s*\([^)]*%s|execute\s*\([^)]*\.format\(', content):
                    score -= 10
                    issues.append({
                        "severity": "high",
                        "category": "security",
                        "file": file_path,
                        "line": None,
                        "message": "Potential SQL injection vulnerability",
                        "suggestion": "Use parameterized queries"
                    })
            
            # Check for eval() usage
            if 'eval(' in content:
                score -= 20
                issues.append({
                    "severity": "critical",
                    "category": "security",
                    "file": file_path,
                    "line": None,
                    "message": "Use of eval() is dangerous",
                    "suggestion": "Avoid eval() or use safer alternatives"
                })
            
            # Check for XSS vulnerabilities (basic check)
            if file_path.endswith(('.jsx', '.tsx')):
                if 'dangerouslySetInnerHTML' in content:
                    score -= 10
                    issues.append({
                        "severity": "medium",
                        "category": "security",
                        "file": file_path,
                        "line": None,
                        "message": "Use of dangerouslySetInnerHTML can lead to XSS",
                        "suggestion": "Ensure content is properly sanitized"
                    })
        
        return max(0, score), issues
    
    def _score_maintainability(self, files: Dict[str, str]) -> Tuple[int, List[Dict]]:
        """
        Score based on:
        - File organization
        - Function length
        - Variable naming
        - Code duplication
        - Separation of concerns
        
        Returns:
            (score: 0-100, issues: List)
        """
        score = 0
        issues = []
        
        # Check file organization
        has_structure = any('/' in f or '\\' in f for f in files.keys())
        if has_structure:
            score += 20
        
        # Check function length
        long_functions = 0
        total_functions = 0
        
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                # Find function definitions and measure their length
                function_pattern = r'def\s+\w+[^:]*:(.*?)(?=\ndef\s|\nclass\s|\Z)'
                matches = re.finditer(function_pattern, content, re.DOTALL)
                
                for match in matches:
                    total_functions += 1
                    lines = match.group(1).strip().split('\n')
                    if len(lines) > 50:
                        long_functions += 1
                        issues.append({
                            "severity": "low",
                            "category": "maintainability",
                            "file": file_path,
                            "line": content[:match.start()].count('\n') + 1,
                            "message": f"Function is {len(lines)} lines long",
                            "suggestion": "Consider breaking into smaller functions"
                        })
            
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                # Simple check for long functions
                function_pattern = r'function\s+\w+[^{]*\{|const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*\{'
                matches = list(re.finditer(function_pattern, content))
                total_functions += len(matches)
        
        # Score based on function length
        if total_functions > 0:
            long_ratio = long_functions / total_functions
            score += int((1 - long_ratio) * 40)
        else:
            score += 20
        
        # Check for good naming (camelCase, snake_case)
        good_naming = True
        for file_path, content in files.items():
            if file_path.endswith('.py'):
                # Check for snake_case
                if re.search(r'def\s+[a-z]+[A-Z]', content):
                    good_naming = False
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                # Check for camelCase
                if re.search(r'function\s+[a-z]+_[a-z]', content):
                    good_naming = False
        
        if good_naming:
            score += 20
        
        # Check for code duplication (simple heuristic)
        all_code = '\n'.join(files.values())
        lines = [l.strip() for l in all_code.split('\n') if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')]
        unique_lines = set(lines)
        
        if len(lines) > 0:
            uniqueness = len(unique_lines) / len(lines)
            score += int(uniqueness * 20)
        
        return min(100, score), issues
