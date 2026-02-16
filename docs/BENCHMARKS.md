# CrucibAI Benchmark System Documentation

## Overview

The CrucibAI Benchmark System provides comprehensive performance analysis and competitive comparison capabilities. It measures speed, quality, and validates our competitive advantages against leading AI development tools.

## Features

### 1. Speed Benchmarking
- Measures actual code generation speed across different project complexities
- Tracks token usage and cost per build
- Monitors success rates and build validation
- Groups results by complexity (simple, medium, complex)

### 2. Competitor Comparison
- Compares against Manus (formerly Devin), Cursor IDE, and Bolt.new
- Calculates speedup multipliers
- Validates marketing claims (e.g., 3.2× faster)
- Highlights unique features and advantages

### 3. Quality Analysis
- Analyzes cyclomatic complexity
- Calculates maintainability index
- Identifies high-complexity functions
- Generates actionable recommendations
- Supports Python code analysis (extensible to other languages)

### 4. Report Generation
- Generates beautiful HTML reports
- Exports Markdown summaries
- Includes visual metrics and comparisons
- Suitable for marketing and technical documentation

## API Endpoints

### Speed Benchmark

**Endpoint:** `POST /api/benchmark/speed`

Run the speed benchmark suite to measure performance across multiple prompts.

**Request Body:**
```json
{
  "prompts": ["Build a todo app", "Create a blog platform"],  // Optional
  "iterations": 1  // Optional, default: 1
}
```

**Response:**
```json
{
  "summary": {
    "total_runs": 9,
    "successful": 8,
    "failed": 1,
    "success_rate": 88.9,
    "avg_duration_seconds": 150.5,
    "avg_duration_minutes": 2.51,
    "avg_tokens": 5000,
    "avg_quality_score": 75,
    "avg_cost_per_build": 0.05
  },
  "by_complexity": {
    "simple": {"count": 3, "avg_duration": 90},
    "medium": {"count": 3, "avg_duration": 180},
    "complex": {"count": 2, "avg_duration": 420}
  },
  "detailed_results": [...]
}
```

### Competitor Comparison

**Endpoint:** `POST /api/benchmark/compare`

Compare your benchmark results against competitors.

**Request Body:**
```json
{
  "our_results": { ... },  // Results from speed benchmark
  "competitors": ["manus", "cursor", "bolt"]  // Optional
}
```

**Response:**
```json
{
  "our_performance": {
    "avg_time_seconds": 150.5,
    "avg_time_minutes": 2.51,
    "success_rate": 88.9,
    "quality_score": 75,
    "unique_features": [...]
  },
  "vs_competitors": {
    "manus": {
      "competitor_name": "Manus (formerly Devin)",
      "speedup": 3.32,
      "speedup_percent": 232.0,
      "advantages": ["3.3× faster", "+23.9% better success rate", ...]
    },
    ...
  },
  "overall": {
    "avg_speedup": 3.2,
    "avg_speedup_percent": 220.0,
    "claim_validated": true,
    "market_position": "#1"
  }
}
```

### Quality Analysis

**Endpoint:** `POST /api/benchmark/quality-analysis`

Perform deep code quality analysis on generated files.

**Request Body:**
```json
{
  "files": {
    "main.py": "def hello():\n    print('hello')\n",
    "app.py": "from fastapi import FastAPI\napp = FastAPI()\n"
  }
}
```

**Response:**
```json
{
  "summary": {
    "total_files": 2,
    "total_loc": 50,
    "avg_complexity": 5.5,
    "avg_maintainability": 85.0,
    "complex_functions": 0
  },
  "files": [...],
  "issues": {
    "high_complexity": [],
    "recommendations": []
  }
}
```

### Generate Report

**Endpoint:** `POST /api/benchmark/generate-report`

Generate a formatted HTML or Markdown report.

**Request Body:**
```json
{
  "format": "html",  // or "markdown"
  "benchmark_results": { ... },
  "comparison_results": { ... },  // Optional
  "quality_results": { ... }  // Optional
}
```

**Response:** HTML or Markdown content

## Usage Examples

### Example 1: Run Speed Benchmark

```python
import requests

response = requests.post(
    "http://localhost:8000/api/benchmark/speed",
    json={
        "prompts": [
            "Build a simple todo app with React",
            "Create a blog with React and FastAPI backend"
        ],
        "iterations": 1
    }
)

results = response.json()
print(f"Success rate: {results['summary']['success_rate']}%")
print(f"Avg duration: {results['summary']['avg_duration_minutes']} min")
```

### Example 2: Compare Against Competitors

```python
import requests

# First, run speed benchmark
speed_results = requests.post(
    "http://localhost:8000/api/benchmark/speed",
    json={"iterations": 1}
).json()

# Then compare
comparison = requests.post(
    "http://localhost:8000/api/benchmark/compare",
    json={
        "our_results": speed_results,
        "competitors": ["manus", "cursor", "bolt"]
    }
).json()

print(f"Average speedup: {comparison['overall']['avg_speedup']}×")
print(f"Claim validated: {comparison['overall']['claim_validated']}")
```

### Example 3: Analyze Code Quality

```python
import requests

with open("main.py", "r") as f:
    main_code = f.read()

with open("app.py", "r") as f:
    app_code = f.read()

analysis = requests.post(
    "http://localhost:8000/api/benchmark/quality-analysis",
    json={
        "files": {
            "main.py": main_code,
            "app.py": app_code
        }
    }
).json()

print(f"Total LOC: {analysis['summary']['total_loc']}")
print(f"Maintainability: {analysis['summary']['avg_maintainability']}/100")
```

### Example 4: Generate HTML Report

```python
import requests

# Get all results
speed_results = requests.post(
    "http://localhost:8000/api/benchmark/speed",
    json={"iterations": 1}
).json()

comparison = requests.post(
    "http://localhost:8000/api/benchmark/compare",
    json={"our_results": speed_results}
).json()

# Generate report
report = requests.post(
    "http://localhost:8000/api/benchmark/generate-report",
    json={
        "format": "html",
        "benchmark_results": speed_results,
        "comparison_results": comparison
    }
)

# Save to file
with open("benchmark_report.html", "w") as f:
    f.write(report.text)

print("Report saved to benchmark_report.html")
```

## Benchmark Prompts

The system includes 9 standard benchmark prompts across three complexity levels:

### Simple (30s-2min expected)
1. Build a simple todo app with React
2. Create a landing page for a SaaS product
3. Build a contact form with validation

### Medium (2-5min expected)
4. Build a blog with React and FastAPI backend
5. Create a dashboard with charts and user auth
6. Build an e-commerce product catalog

### Complex (5-10min expected)
7. Build a full-stack task management app with teams, projects, and real-time updates
8. Create a SaaS boilerplate with authentication, payments, and admin dashboard
9. Build a social media feed with posts, comments, likes, and notifications

## Competitor Data

The system includes performance data for major competitors:

### Manus (formerly Devin)
- Average speeds: 3min (simple), 7min (medium), 15min (complex)
- Success rate: ~65%
- No automatic validation
- No quality scoring

### Cursor IDE
- Average speeds: 2min (simple), 5min (medium), 10min (complex)
- Success rate: ~70%
- No automatic validation
- No quality scoring

### Bolt.new
- Average speeds: 1.5min (simple), 4min (medium), 8min (complex)
- Success rate: ~75%
- Has live preview
- No quality scoring

## Quality Metrics

The quality analyzer measures:

### Cyclomatic Complexity
- Measures code branching and decision points
- Lower is better (target: <10 per function)
- Identifies overly complex functions

### Maintainability Index
- 0-100 scale (higher is better)
- Considers complexity and code size
- Target: >60 for good maintainability

### Recommendations
- Automated suggestions for improvement
- Based on industry best practices
- Identifies files needing refactoring

## Integration

### With Orchestration System

The benchmark system can be integrated with your orchestration system:

```python
from backend.benchmarks import SpeedBenchmark
from backend.orchestration import run_orchestration_with_dag

# Create orchestrator wrapper
async def orchestrator_wrapper(prompt: str):
    # Your orchestration logic here
    result = await run_orchestration_with_dag(
        project_id="benchmark",
        user_id="system"
    )
    return result

# Run benchmark
benchmark = SpeedBenchmark(orchestrator_wrapper)
results = await benchmark.run_benchmark_suite()
```

### With CI/CD

Add benchmark tests to your CI pipeline:

```yaml
# .github/workflows/benchmark.yml
name: Benchmark Tests

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run benchmarks
        run: |
          python -m pytest backend/tests/test_benchmarks.py
      - name: Generate report
        run: |
          python scripts/generate_benchmark_report.py
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-report
          path: benchmark_report.html
```

## Best Practices

1. **Run Regular Benchmarks**: Schedule weekly or monthly benchmark runs to track performance trends
2. **Compare Iterations**: Compare results over time to measure improvements
3. **Document Changes**: Keep track of what changed between benchmark runs
4. **Share Results**: Use generated reports for marketing and stakeholder communication
5. **Act on Recommendations**: Address quality issues identified by the analyzer

## Limitations

1. **Competitor Data**: Based on public sources, manual testing, and user reports (not live API access)
2. **Language Support**: Quality analysis currently supports Python only (extensible to other languages)
3. **Resource Intensive**: Full benchmark suite can take significant time
4. **Cost**: Running multiple iterations uses API tokens

## Future Enhancements

- [ ] Support for JavaScript/TypeScript complexity analysis
- [ ] Real-time competitor benchmarking (if APIs become available)
- [ ] PDF report generation
- [ ] Automated benchmark scheduling
- [ ] Historical trend analysis
- [ ] Performance regression detection
- [ ] Integration with monitoring tools

## Support

For questions or issues with the benchmark system:
- Check the API documentation: `/docs`
- Review example code in `backend/tests/test_benchmarks.py`
- Contact support: support@crucibai.com

---

**Last Updated:** February 2026
**Version:** 1.0.0
