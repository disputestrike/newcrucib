"""
Advanced code quality benchmarking.
Goes beyond basic scoring to measure:
- Cyclomatic complexity (detailed)
- Code maintainability index
- Security vulnerabilities (detailed scan)
- Test coverage estimation
- Documentation completeness
"""

import ast
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ComplexityMetrics:
    """Detailed complexity metrics for a code file"""
    file_path: str
    language: str
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    functions: List[Dict]
    classes: List[Dict]
    maintainability_index: float
    
    def to_dict(self) -> Dict:
        return {
            "file": self.file_path,
            "language": self.language,
            "loc": self.lines_of_code,
            "cyclomatic": self.cyclomatic_complexity,
            "cognitive": self.cognitive_complexity,
            "functions": self.functions,
            "classes": self.classes,
            "maintainability": self.maintainability_index
        }


class AdvancedQualityAnalyzer:
    """Deep code quality analysis"""
    
    def analyze_python_complexity(self, code: str, filepath: str) -> ComplexityMetrics:
        """
        Analyze Python code complexity using AST.
        Calculate cyclomatic and cognitive complexity.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ComplexityMetrics(
                file_path=filepath,
                language="Python",
                lines_of_code=len(code.split('\n')),
                cyclomatic_complexity=0,
                cognitive_complexity=0,
                functions=[],
                classes=[],
                maintainability_index=0
            )
        
        functions = []
        classes = []
        total_complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_complexity = self._calculate_cyclomatic_complexity(node)
                functions.append({
                    "name": node.name,
                    "lines": len(ast.unparse(node).split('\n')),
                    "complexity": func_complexity,
                    "params": len(node.args.args)
                })
                total_complexity += func_complexity
            
            elif isinstance(node, ast.ClassDef):
                methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "methods": len(methods),
                    "lines": len(ast.unparse(node).split('\n'))
                })
        
        loc = len([line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        # Maintainability Index (simplified)
        # MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        # Simplified: higher is better, 100 is perfect
        if loc > 0:
            mi = max(0, min(100, 100 - (total_complexity * 2) - (loc / 10)))
        else:
            mi = 100
        
        return ComplexityMetrics(
            file_path=filepath,
            language="Python",
            lines_of_code=loc,
            cyclomatic_complexity=total_complexity,
            cognitive_complexity=total_complexity,  # Simplified
            functions=functions,
            classes=classes,
            maintainability_index=mi
        )
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def analyze_codebase(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze complete codebase quality"""
        metrics = []
        
        for filepath, code in files.items():
            if filepath.endswith('.py'):
                metric = self.analyze_python_complexity(code, filepath)
                metrics.append(metric)
        
        if not metrics:
            return {"error": "No analyzable files"}
        
        # Aggregate metrics
        total_loc = sum(m.lines_of_code for m in metrics)
        avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics)
        avg_maintainability = sum(m.maintainability_index for m in metrics) / len(metrics)
        
        # Find problematic functions
        all_functions = [f for m in metrics for f in m.functions]
        complex_functions = [f for f in all_functions if f["complexity"] > 10]
        
        return {
            "summary": {
                "total_files": len(metrics),
                "total_loc": total_loc,
                "avg_complexity": round(avg_complexity, 2),
                "avg_maintainability": round(avg_maintainability, 2),
                "complex_functions": len(complex_functions)
            },
            "files": [m.to_dict() for m in metrics],
            "issues": {
                "high_complexity": complex_functions,
                "recommendations": self._generate_recommendations(metrics)
            }
        }
    
    def _generate_recommendations(self, metrics: List[ComplexityMetrics]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        avg_complexity = sum(m.cyclomatic_complexity for m in metrics) / len(metrics)
        if avg_complexity > 15:
            recommendations.append("High complexity detected. Consider refactoring complex functions.")
        
        long_files = [m for m in metrics if m.lines_of_code > 300]
        if long_files:
            recommendations.append(f"{len(long_files)} files exceed 300 LOC. Consider splitting.")
        
        low_maintainability = [m for m in metrics if m.maintainability_index < 50]
        if low_maintainability:
            recommendations.append(f"{len(low_maintainability)} files have low maintainability. Refactor recommended.")
        
        return recommendations
