"""
Generate beautiful HTML/PDF benchmark reports for marketing.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime


class ReportGenerator:
    """Generate benchmark reports in various formats"""
    
    @staticmethod
    def generate_html_report(
        benchmark_results: Dict[str, Any],
        comparison_results: Optional[Dict[str, Any]] = None,
        quality_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an HTML benchmark report.
        
        Args:
            benchmark_results: Results from SpeedBenchmark
            comparison_results: Results from ComparisonReport (optional)
            quality_results: Results from AdvancedQualityAnalyzer (optional)
            
        Returns:
            HTML string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrucibAI Benchmark Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header .timestamp {{
            opacity: 0.9;
            margin-top: 10px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .metric {{
            display: inline-block;
            background: #f8f9fa;
            padding: 15px 20px;
            margin: 10px 10px 10px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .success {{
            color: #28a745;
        }}
        .warning {{
            color: #ffc107;
        }}
        .error {{
            color: #dc3545;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .comparison {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .competitor-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #f8f9fa;
        }}
        .competitor-card h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .speedup {{
            font-size: 2em;
            font-weight: bold;
            color: #28a745;
            margin: 10px 0;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 CrucibAI Benchmark Report</h1>
        <div class="timestamp">Generated: {timestamp}</div>
    </div>
"""
        
        # Speed benchmark section
        if benchmark_results:
            summary = benchmark_results.get("summary", {})
            html += f"""
    <div class="section">
        <h2>Speed Benchmark Results</h2>
        <div>
            <div class="metric">
                <div class="metric-label">Total Runs</div>
                <div class="metric-value">{summary.get('total_runs', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value success">{summary.get('success_rate', 0):.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Duration</div>
                <div class="metric-value">{summary.get('avg_duration_minutes', 0):.2f} min</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Quality Score</div>
                <div class="metric-value">{summary.get('avg_quality_score', 0):.0f}/100</div>
            </div>
        </div>
"""
            
            # Complexity breakdown
            by_complexity = benchmark_results.get("by_complexity", {})
            if by_complexity:
                html += """
        <h3>Performance by Complexity</h3>
        <table>
            <thead>
                <tr>
                    <th>Complexity</th>
                    <th>Count</th>
                    <th>Avg Duration</th>
                </tr>
            </thead>
            <tbody>
"""
                for complexity in ["simple", "medium", "complex"]:
                    data = by_complexity.get(complexity, {})
                    count = data.get("count", 0)
                    avg_dur = data.get("avg_duration", 0)
                    html += f"""
                <tr>
                    <td>{complexity.capitalize()}</td>
                    <td>{count}</td>
                    <td>{avg_dur:.2f}s</td>
                </tr>
"""
                html += """
            </tbody>
        </table>
"""
            
            html += """
    </div>
"""
        
        # Competitor comparison section
        if comparison_results:
            overall = comparison_results.get("overall", {})
            vs_competitors = comparison_results.get("vs_competitors", {})
            
            html += f"""
    <div class="section">
        <h2>Competitor Comparison</h2>
        <div class="metric">
            <div class="metric-label">Average Speedup</div>
            <div class="metric-value success">{overall.get('avg_speedup', 0):.2f}×</div>
        </div>
        <div class="metric">
            <div class="metric-label">Market Position</div>
            <div class="metric-value">{overall.get('market_position', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Speedup Claim Validated</div>
            <div class="metric-value {'success' if overall.get('claim_validated') else 'warning'}">
                {'✅ Yes' if overall.get('claim_validated') else '⚠️ No'}
            </div>
        </div>
        
        <div class="comparison">
"""
            
            for comp_name, comp_data in vs_competitors.items():
                html += f"""
            <div class="competitor-card">
                <h3>{comp_data.get('competitor_name', comp_name)}</h3>
                <div class="speedup">{comp_data.get('speedup', 0):.2f}× faster</div>
                <p><strong>Success Rate:</strong> Ours: {comp_data.get('our_success_rate', 0):.1f}% vs Theirs: {comp_data.get('their_success_rate', 0):.1f}%</p>
                <p><strong>Our Advantages:</strong></p>
                <ul>
"""
                for advantage in comp_data.get('advantages', []):
                    if advantage:  # Skip empty advantages
                        html += f"                    <li>{advantage}</li>\n"
                
                html += """
                </ul>
            </div>
"""
            
            html += """
        </div>
    </div>
"""
        
        # Quality analysis section
        if quality_results and "summary" in quality_results:
            summary = quality_results.get("summary", {})
            html += f"""
    <div class="section">
        <h2>Code Quality Analysis</h2>
        <div>
            <div class="metric">
                <div class="metric-label">Total Files</div>
                <div class="metric-value">{summary.get('total_files', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total LOC</div>
                <div class="metric-value">{summary.get('total_loc', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Complexity</div>
                <div class="metric-value">{summary.get('avg_complexity', 0):.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Maintainability</div>
                <div class="metric-value">{summary.get('avg_maintainability', 0):.1f}/100</div>
            </div>
        </div>
"""
            
            # Recommendations
            issues = quality_results.get("issues", {})
            recommendations = issues.get("recommendations", [])
            if recommendations:
                html += """
        <h3>Recommendations</h3>
        <ul>
"""
                for rec in recommendations:
                    html += f"            <li>{rec}</li>\n"
                html += """
        </ul>
"""
            
            html += """
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def save_html_report(
        html_content: str,
        filepath: str = "benchmark_report.html"
    ) -> str:
        """Save HTML report to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTML report saved to {filepath}")
        return filepath
    
    @staticmethod
    def generate_markdown_report(
        benchmark_results: Dict[str, Any],
        comparison_results: Optional[Dict[str, Any]] = None,
        quality_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a Markdown benchmark report.
        
        Args:
            benchmark_results: Results from SpeedBenchmark
            comparison_results: Results from ComparisonReport (optional)
            quality_results: Results from AdvancedQualityAnalyzer (optional)
            
        Returns:
            Markdown string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# 🚀 CrucibAI Benchmark Report

Generated: {timestamp}

---

"""
        
        # Speed benchmark section
        if benchmark_results:
            summary = benchmark_results.get("summary", {})
            md += f"""## Speed Benchmark Results

- **Total Runs:** {summary.get('total_runs', 0)}
- **Successful:** {summary.get('successful', 0)}
- **Failed:** {summary.get('failed', 0)}
- **Success Rate:** {summary.get('success_rate', 0):.1f}%
- **Average Duration:** {summary.get('avg_duration_minutes', 0):.2f} minutes
- **Average Quality Score:** {summary.get('avg_quality_score', 0):.0f}/100
- **Average Cost per Build:** ${summary.get('avg_cost_per_build', 0):.4f}

### Performance by Complexity

"""
            by_complexity = benchmark_results.get("by_complexity", {})
            md += "| Complexity | Count | Avg Duration (seconds) |\n"
            md += "|------------|-------|------------------------|\n"
            
            for complexity in ["simple", "medium", "complex"]:
                data = by_complexity.get(complexity, {})
                count = data.get("count", 0)
                avg_dur = data.get("avg_duration", 0)
                md += f"| {complexity.capitalize()} | {count} | {avg_dur:.2f} |\n"
            
            md += "\n---\n\n"
        
        # Competitor comparison section
        if comparison_results:
            overall = comparison_results.get("overall", {})
            vs_competitors = comparison_results.get("vs_competitors", {})
            
            md += f"""## Competitor Comparison

- **Average Speedup:** {overall.get('avg_speedup', 0):.2f}×
- **Market Position:** {overall.get('market_position', 'N/A')}
- **Speedup Claim Validated:** {'✅ Yes' if overall.get('claim_validated') else '⚠️ No'}

### Detailed Comparisons

"""
            
            for comp_name, comp_data in vs_competitors.items():
                md += f"""#### vs {comp_data.get('competitor_name', comp_name)}

- **Speedup:** {comp_data.get('speedup', 0):.2f}×
- **Our Success Rate:** {comp_data.get('our_success_rate', 0):.1f}%
- **Their Success Rate:** {comp_data.get('their_success_rate', 0):.1f}%

**Our Advantages:**
"""
                for advantage in comp_data.get('advantages', []):
                    if advantage:
                        md += f"- {advantage}\n"
                
                md += "\n"
            
            md += "---\n\n"
        
        # Quality analysis section
        if quality_results and "summary" in quality_results:
            summary = quality_results.get("summary", {})
            md += f"""## Code Quality Analysis

- **Total Files Analyzed:** {summary.get('total_files', 0)}
- **Total Lines of Code:** {summary.get('total_loc', 0)}
- **Average Cyclomatic Complexity:** {summary.get('avg_complexity', 0):.2f}
- **Average Maintainability Index:** {summary.get('avg_maintainability', 0):.1f}/100
- **High Complexity Functions:** {summary.get('complex_functions', 0)}

"""
            
            # Recommendations
            issues = quality_results.get("issues", {})
            recommendations = issues.get("recommendations", [])
            if recommendations:
                md += "### Recommendations\n\n"
                for rec in recommendations:
                    md += f"- {rec}\n"
                md += "\n"
        
        return md
    
    @staticmethod
    def save_markdown_report(
        md_content: str,
        filepath: str = "benchmark_report.md"
    ) -> str:
        """Save Markdown report to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📄 Markdown report saved to {filepath}")
        return filepath
