"""
F6: Rank and Report Suspicious Code Lines
Generates clear and actionable fault localization reports.
"""

from typing import List
import uuid
from datetime import datetime
from models import (
    SuspiciousLine, FaultLocalizationOutput, ReportOutput,
    ReportRequest
)


class FaultLocalizationReporter:
    """
    Generates formatted reports for fault localization results.
    """
    
    def generate_report(
        self,
        analysis: FaultLocalizationOutput,
        top_n: int = 10
    ) -> ReportOutput:
        """
        Generate a comprehensive fault localization report.
        
        Args:
            analysis: Fault localization analysis results
            top_n: Number of top suspicious lines to include
        
        Returns:
            ReportOutput with formatted report data
        """
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # Get top N suspicious lines
        top_suspicious = analysis.suspicious_lines[:top_n]
        
        # Generate summary
        summary = self._generate_summary(analysis, len(top_suspicious))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, top_suspicious)
        
        return ReportOutput(
            report_id=report_id,
            generated_at=timestamp,
            analysis_id=analysis.analysis_id,
            summary=summary,
            top_suspicious_lines=top_suspicious,
            recommendations=recommendations
        )
    
    def _generate_summary(
        self,
        analysis: FaultLocalizationOutput,
        num_reported: int
    ) -> str:
        """Generate a text summary of the analysis."""
        summary_parts = [
            f"Fault Localization Report for: {analysis.source_file}",
            f"Total tests executed: {analysis.total_tests}",
            f"Passed: {analysis.passed_tests}, Failed: {analysis.failed_tests}",
            f"Suspicious lines identified: {len(analysis.suspicious_lines)}",
            f"Top {num_reported} lines reported below"
        ]
        
        if analysis.failed_tests == 0:
            summary_parts.append("No test failures detected - no fault localization needed.")
        elif len(analysis.suspicious_lines) == 0:
            summary_parts.append("No executable lines covered by tests.")
        
        return " | ".join(summary_parts)
    
    def _generate_recommendations(
        self,
        analysis: FaultLocalizationOutput,
        top_suspicious: List[SuspiciousLine]
    ) -> List[str]:
        """
        Generate actionable recommendations based on the analysis.
        """
        recommendations = []
        
        if not top_suspicious:
            recommendations.append("No suspicious lines identified. Consider adding more test cases.")
            return recommendations
        
        # Recommendation 1: Focus on highest suspiciousness
        top_line = top_suspicious[0]
        if top_line.suspiciousness_score > 0.8:
            recommendations.append(
                f"HIGH PRIORITY: Line {top_line.line_number} has very high suspiciousness "
                f"({top_line.suspiciousness_score:.2f}). Start debugging here."
            )
        elif top_line.suspiciousness_score > 0.5:
            recommendations.append(
                f"MEDIUM PRIORITY: Line {top_line.line_number} shows moderate suspiciousness "
                f"({top_line.suspiciousness_score:.2f}). Review this line carefully."
            )
        else:
            recommendations.append(
                f"LOW SUSPICIOUSNESS: Top line ({top_line.line_number}) has score "
                f"{top_line.suspiciousness_score:.2f}. Fault may be subtle."
            )
        
        # Recommendation 2: Lines only in failed tests
        only_in_failed = [
            line for line in top_suspicious
            if line.passed_coverage == 0 and line.failed_coverage > 0
        ]
        if only_in_failed:
            recommendations.append(
                f"Found {len(only_in_failed)} line(s) ONLY executed in failed tests. "
                f"These are highly suspect: {[l.line_number for l in only_in_failed[:3]]}"
            )
        
        # Recommendation 3: Clustered suspicious lines
        if len(top_suspicious) >= 3:
            line_nums = [l.line_number for l in top_suspicious[:5]]
            if self._are_lines_clustered(line_nums):
                recommendations.append(
                    f"Suspicious lines appear clustered around lines {min(line_nums)}-{max(line_nums)}. "
                    f"The fault may be in this code region."
                )
        
        # Recommendation 4: Test coverage quality
        if analysis.total_tests < 5:
            recommendations.append(
                f"Only {analysis.total_tests} test(s) available. "
                f"Increase test suite size for better fault localization accuracy."
            )
        
        # Recommendation 5: Balance of passed/failed tests
        if analysis.passed_tests == 0:
            recommendations.append(
                "WARNING: No passing tests. Tarantula requires both passing and failing tests "
                "for accurate results. Add passing test cases."
            )
        elif analysis.failed_tests > analysis.passed_tests * 2:
            recommendations.append(
                f"Test suite is heavily skewed ({analysis.failed_tests} failed vs "
                f"{analysis.passed_tests} passed). Add more passing tests for better accuracy."
            )
        
        return recommendations
    
    def _are_lines_clustered(self, line_numbers: List[int], threshold: int = 5) -> bool:
        """Check if line numbers are close together (within threshold)."""
        if len(line_numbers) < 2:
            return False
        
        sorted_lines = sorted(line_numbers)
        max_gap = max(sorted_lines[i+1] - sorted_lines[i] for i in range(len(sorted_lines)-1))
        
        return max_gap <= threshold
    
    def format_text_report(self, report: ReportOutput) -> str:
        """
        Format report as human-readable text.
        
        Returns:
            Multi-line string with formatted report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("FAULT LOCALIZATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Report ID: {report.report_id}")
        lines.append(f"Generated: {report.generated_at}")
        lines.append(f"Analysis ID: {report.analysis_id}")
        lines.append("")
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(report.summary)
        lines.append("")
        lines.append("TOP SUSPICIOUS LINES")
        lines.append("-" * 80)
        lines.append(f"{'Rank':<6} {'Line':<6} {'Score':<8} {'Failed':<8} {'Passed':<8} {'Code'}")
        lines.append("-" * 80)
        
        for i, line in enumerate(report.top_suspicious_lines, 1):
            code_preview = line.line_content[:50] + "..." if len(line.line_content) > 50 else line.line_content
            lines.append(
                f"{i:<6} {line.line_number:<6} {line.suspiciousness_score:<8.4f} "
                f"{line.failed_coverage:<8} {line.passed_coverage:<8} {code_preview}"
            )
        
        lines.append("")
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def format_json_report(self, report: ReportOutput) -> dict:
        """
        Format report as JSON-serializable dictionary.
        """
        return report.model_dump()
    
    def export_to_file(self, report: ReportOutput, file_path: str, format: str = "text"):
        """
        Export report to a file.
        
        Args:
            report: Report to export
            file_path: Path to output file
            format: "text" or "json"
        """
        import json
        
        with open(file_path, 'w') as f:
            if format == "json":
                json.dump(self.format_json_report(report), f, indent=2)
            else:
                f.write(self.format_text_report(report))


def generate_quick_report(
    analysis: FaultLocalizationOutput,
    top_n: int = 10
) -> ReportOutput:
    """
    Convenience function to quickly generate a report.
    
    Args:
        analysis: Fault localization analysis results
        top_n: Number of top suspicious lines to include
    
    Returns:
        ReportOutput with formatted report
    """
    reporter = FaultLocalizationReporter()
    return reporter.generate_report(analysis, top_n)


def print_report(report: ReportOutput):
    """
    Print a formatted text report to console.
    """
    reporter = FaultLocalizationReporter()
    print(reporter.format_text_report(report))

