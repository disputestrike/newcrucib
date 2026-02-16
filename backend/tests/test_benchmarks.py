"""
Unit tests for the benchmark system.
Tests speed benchmarking, competitor comparison, quality analysis, and report generation.
"""

import pytest
import asyncio
from backend.benchmarks import (
    SpeedBenchmark,
    BenchmarkResult,
    ComparisonReport,
    CompetitorData,
    AdvancedQualityAnalyzer,
    ComplexityMetrics,
    ReportGenerator
)


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass"""
    
    def test_benchmark_result_creation(self):
        """Test creating a BenchmarkResult"""
        result = BenchmarkResult(
            prompt="Build a todo app",
            tool="newcrucib-v2",
            start_time=100.0,
            end_time=200.0,
            success=True,
            tokens_used=5000,
            files_generated=5,
            build_validated=True,
            quality_score=75.0
        )
        
        assert result.prompt == "Build a todo app"
        assert result.tool == "newcrucib-v2"
        assert result.success is True
        assert result.duration_seconds == 100.0
        assert result.duration_minutes == pytest.approx(1.67, rel=0.01)
    
    def test_benchmark_result_to_dict(self):
        """Test converting BenchmarkResult to dict"""
        result = BenchmarkResult(
            prompt="Build a todo app",
            tool="newcrucib-v2",
            start_time=100.0,
            end_time=150.0,
            success=True,
            tokens_used=3000,
            files_generated=3,
            build_validated=True,
            quality_score=80.0
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["prompt"] == "Build a todo app"
        assert result_dict["tool"] == "newcrucib-v2"
        assert result_dict["duration_seconds"] == 50.0
        assert result_dict["success"] is True
        assert result_dict["tokens_used"] == 3000


class TestSpeedBenchmark:
    """Tests for SpeedBenchmark class"""
    
    @pytest.mark.asyncio
    async def test_benchmark_single_prompt_success(self):
        """Test benchmarking a single prompt successfully"""
        
        # Mock orchestrator
        async def mock_orchestrator(prompt: str):
            return {
                "success": True,
                "metrics": {"tokens": {"total": 4000}},
                "summary": {"files_generated": 4},
                "validations": {
                    "frontend": {"overall_valid": True},
                    "quality": {"overall_score": 70}
                }
            }
        
        benchmark = SpeedBenchmark(mock_orchestrator)
        result = await benchmark._benchmark_single_prompt("Build a todo app")
        
        assert result.success is True
        assert result.prompt == "Build a todo app"
        assert result.tokens_used == 4000
        assert result.files_generated == 4
        assert result.quality_score == 70
    
    @pytest.mark.asyncio
    async def test_benchmark_single_prompt_failure(self):
        """Test handling benchmark failure"""
        
        async def failing_orchestrator(prompt: str):
            raise Exception("Orchestration failed")
        
        benchmark = SpeedBenchmark(failing_orchestrator)
        result = await benchmark._benchmark_single_prompt("Build a todo app")
        
        assert result.success is False
        assert result.error == "Orchestration failed"
        assert result.tokens_used == 0
    
    @pytest.mark.asyncio
    async def test_run_benchmark_suite(self):
        """Test running complete benchmark suite"""
        
        call_count = 0
        
        async def mock_orchestrator(prompt: str):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate some work
            return {
                "success": True,
                "metrics": {"tokens": {"total": 5000}},
                "summary": {"files_generated": 5},
                "validations": {
                    "frontend": {"overall_valid": True},
                    "quality": {"overall_score": 75}
                }
            }
        
        benchmark = SpeedBenchmark(mock_orchestrator)
        prompts = ["Prompt 1", "Prompt 2"]
        results = await benchmark.run_benchmark_suite(prompts=prompts, iterations=1)
        
        assert call_count == 2
        assert results["summary"]["total_runs"] == 2
        assert results["summary"]["successful"] == 2
        assert results["summary"]["failed"] == 0
        assert results["summary"]["success_rate"] == 100.0
    
    def test_generate_report(self):
        """Test generating report from results"""
        
        # Create some mock results
        benchmark = SpeedBenchmark(lambda x: None)
        benchmark.results = [
            BenchmarkResult(
                prompt="Simple",
                tool="newcrucib-v2",
                start_time=100.0,
                end_time=150.0,  # 50s - simple
                success=True,
                tokens_used=3000,
                files_generated=3,
                build_validated=True,
                quality_score=80.0
            ),
            BenchmarkResult(
                prompt="Medium",
                tool="newcrucib-v2",
                start_time=100.0,
                end_time=280.0,  # 180s - medium
                success=True,
                tokens_used=6000,
                files_generated=6,
                build_validated=True,
                quality_score=75.0
            ),
            BenchmarkResult(
                prompt="Complex",
                tool="newcrucib-v2",
                start_time=100.0,
                end_time=500.0,  # 400s - complex
                success=True,
                tokens_used=10000,
                files_generated=10,
                build_validated=True,
                quality_score=70.0
            )
        ]
        
        report = benchmark._generate_report()
        
        assert report["summary"]["total_runs"] == 3
        assert report["summary"]["successful"] == 3
        assert report["summary"]["success_rate"] == 100.0
        assert report["by_complexity"]["simple"]["count"] == 1
        assert report["by_complexity"]["medium"]["count"] == 1
        assert report["by_complexity"]["complex"]["count"] == 1


class TestCompetitorComparison:
    """Tests for competitor comparison"""
    
    def test_competitor_data_exists(self):
        """Test that competitor data is available"""
        assert "manus" in CompetitorData.COMPETITOR_BENCHMARKS
        assert "cursor" in CompetitorData.COMPETITOR_BENCHMARKS
        assert "bolt" in CompetitorData.COMPETITOR_BENCHMARKS
        
        manus = CompetitorData.COMPETITOR_BENCHMARKS["manus"]
        assert "avg_simple_task" in manus
        assert "success_rate" in manus
    
    def test_generate_comparison(self):
        """Test generating comparison report"""
        
        our_results = {
            "summary": {
                "avg_duration_seconds": 150.0,  # 2.5 minutes
                "success_rate": 85.0,
                "avg_quality_score": 75.0
            }
        }
        
        comparison = ComparisonReport.generate_comparison(our_results)
        
        assert "our_performance" in comparison
        assert "vs_competitors" in comparison
        assert "overall" in comparison
        
        assert comparison["our_performance"]["avg_time_seconds"] == 150.0
        assert comparison["our_performance"]["success_rate"] == 85.0
        
        # Check competitor comparisons
        assert "manus" in comparison["vs_competitors"]
        manus_comp = comparison["vs_competitors"]["manus"]
        assert "speedup" in manus_comp
        assert manus_comp["speedup"] > 1  # We should be faster
    
    def test_comparison_with_specific_competitors(self):
        """Test comparison with specific competitors"""
        
        our_results = {
            "summary": {
                "avg_duration_seconds": 100.0,
                "success_rate": 90.0,
                "avg_quality_score": 80.0
            }
        }
        
        comparison = ComparisonReport.generate_comparison(
            our_results,
            competitors=["cursor", "bolt"]
        )
        
        assert len(comparison["vs_competitors"]) == 2
        assert "cursor" in comparison["vs_competitors"]
        assert "bolt" in comparison["vs_competitors"]
        assert "manus" not in comparison["vs_competitors"]


class TestAdvancedQualityAnalyzer:
    """Tests for quality analysis"""
    
    def test_analyze_simple_python_code(self):
        """Test analyzing simple Python code"""
        
        code = """
def hello():
    print("Hello, world!")
    return True

def add(a, b):
    return a + b
"""
        
        analyzer = AdvancedQualityAnalyzer()
        metrics = analyzer.analyze_python_complexity(code, "test.py")
        
        assert metrics.file_path == "test.py"
        assert metrics.language == "Python"
        assert len(metrics.functions) == 2
        assert metrics.functions[0]["name"] == "hello"
        assert metrics.functions[1]["name"] == "add"
    
    def test_analyze_complex_python_code(self):
        """Test analyzing complex Python code"""
        
        code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            for i in range(x):
                if i % 2 == 0:
                    return i
    return 0
"""
        
        analyzer = AdvancedQualityAnalyzer()
        metrics = analyzer.analyze_python_complexity(code, "complex.py")
        
        assert len(metrics.functions) == 1
        func = metrics.functions[0]
        assert func["name"] == "complex_function"
        assert func["complexity"] > 1  # Should have higher complexity
    
    def test_analyze_code_with_classes(self):
        """Test analyzing code with classes"""
        
        code = """
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        return True
"""
        
        analyzer = AdvancedQualityAnalyzer()
        metrics = analyzer.analyze_python_complexity(code, "class.py")
        
        assert len(metrics.classes) == 1
        assert metrics.classes[0]["name"] == "MyClass"
        assert metrics.classes[0]["methods"] >= 2
    
    def test_analyze_codebase(self):
        """Test analyzing complete codebase"""
        
        files = {
            "main.py": """
def main():
    print("Hello")
    return True
""",
            "utils.py": """
def helper():
    if True:
        return 1
    return 0

def another():
    pass
""",
            "README.md": "# This is not Python"
        }
        
        analyzer = AdvancedQualityAnalyzer()
        analysis = analyzer.analyze_codebase(files)
        
        assert "summary" in analysis
        assert analysis["summary"]["total_files"] == 2  # Only Python files
        assert "files" in analysis
        assert len(analysis["files"]) == 2
    
    def test_analyze_invalid_python(self):
        """Test handling invalid Python code"""
        
        code = "this is not valid python code {"
        
        analyzer = AdvancedQualityAnalyzer()
        metrics = analyzer.analyze_python_complexity(code, "invalid.py")
        
        assert metrics.cyclomatic_complexity == 0
        assert len(metrics.functions) == 0
    
    def test_generate_recommendations(self):
        """Test generating recommendations"""
        
        # Create metrics with some issues
        metrics = [
            ComplexityMetrics(
                file_path="complex.py",
                language="Python",
                lines_of_code=400,  # Long file
                cyclomatic_complexity=20,  # High complexity
                cognitive_complexity=20,
                functions=[{"name": "test", "complexity": 15, "lines": 50, "params": 3}],
                classes=[],
                maintainability_index=40  # Low maintainability
            )
        ]
        
        analyzer = AdvancedQualityAnalyzer()
        recommendations = analyzer._generate_recommendations(metrics)
        
        assert len(recommendations) > 0
        assert any("exceed" in rec.lower() for rec in recommendations)


class TestReportGenerator:
    """Tests for report generation"""
    
    def test_generate_html_report(self):
        """Test generating HTML report"""
        
        benchmark_results = {
            "summary": {
                "total_runs": 5,
                "success_rate": 80.0,
                "avg_duration_minutes": 2.5,
                "avg_quality_score": 75
            },
            "by_complexity": {
                "simple": {"count": 2, "avg_duration": 60},
                "medium": {"count": 2, "avg_duration": 150},
                "complex": {"count": 1, "avg_duration": 300}
            }
        }
        
        html = ReportGenerator.generate_html_report(benchmark_results)
        
        assert "<!DOCTYPE html>" in html
        assert "CrucibAI Benchmark Report" in html
        assert "Speed Benchmark Results" in html
        assert "80.0%" in html  # Success rate
    
    def test_generate_html_report_with_comparison(self):
        """Test generating HTML report with comparison"""
        
        benchmark_results = {
            "summary": {
                "total_runs": 3,
                "success_rate": 90.0,
                "avg_duration_minutes": 2.0,
                "avg_quality_score": 80
            }
        }
        
        comparison_results = {
            "overall": {
                "avg_speedup": 3.2,
                "market_position": "#1",
                "claim_validated": True
            },
            "vs_competitors": {
                "manus": {
                    "competitor_name": "Manus",
                    "speedup": 3.5,
                    "advantages": ["3.5× faster", "Better quality"]
                }
            }
        }
        
        html = ReportGenerator.generate_html_report(
            benchmark_results,
            comparison_results
        )
        
        assert "Competitor Comparison" in html
        assert "3.2×" in html or "3.20×" in html
        assert "Manus" in html
    
    def test_generate_markdown_report(self):
        """Test generating Markdown report"""
        
        benchmark_results = {
            "summary": {
                "total_runs": 5,
                "successful": 4,
                "failed": 1,
                "success_rate": 80.0,
                "avg_duration_minutes": 2.5,
                "avg_quality_score": 75,
                "avg_cost_per_build": 0.05
            },
            "by_complexity": {
                "simple": {"count": 2, "avg_duration": 60},
                "medium": {"count": 2, "avg_duration": 150},
                "complex": {"count": 1, "avg_duration": 300}
            }
        }
        
        md = ReportGenerator.generate_markdown_report(benchmark_results)
        
        assert "# 🚀 CrucibAI Benchmark Report" in md
        assert "## Speed Benchmark Results" in md
        assert "**Total Runs:** 5" in md
        assert "80.0%" in md
        assert "| Complexity" in md  # Table header
    
    def test_generate_markdown_report_with_quality(self):
        """Test generating Markdown report with quality analysis"""
        
        benchmark_results = {
            "summary": {
                "total_runs": 3,
                "success_rate": 90.0,
                "avg_duration_minutes": 2.0,
                "avg_quality_score": 80
            }
        }
        
        quality_results = {
            "summary": {
                "total_files": 5,
                "total_loc": 250,
                "avg_complexity": 5.5,
                "avg_maintainability": 85.0,
                "complex_functions": 1
            },
            "issues": {
                "recommendations": [
                    "Consider refactoring",
                    "Add more tests"
                ]
            }
        }
        
        md = ReportGenerator.generate_markdown_report(
            benchmark_results,
            quality_results=quality_results
        )
        
        assert "## Code Quality Analysis" in md
        assert "250" in md  # Total LOC
        assert "Consider refactoring" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
