"""
F5: Spectrum-Based Fault Localization (Tarantula)
Identifies suspicious code lines based on test pass/fail coverage.
"""

from typing import List, Dict, Set
import uuid
from models import (
    TestResult, SuspiciousLine, FaultLocalizationOutput,
    TestExecutionOutput
)


class TarantulaLocalizer:
    """
    Implements the Tarantula fault localization algorithm.
    
    The Tarantula formula measures how suspicious each line of code is
    based on its execution in passing vs. failing tests:
    
    Suspiciousness(s) = %failed(s) / (%failed(s) + %passed(s))
    
    Where:
    - %failed(s) = (failed tests executing s) / (total failed tests)
    - %passed(s) = (passed tests executing s) / (total passed tests)
    """
    
    def __init__(self):
        self.line_coverage: Dict[int, Dict[str, int]] = {}  # line -> {passed: N, failed: M}
    
    def analyze(
        self,
        source_file: str,
        test_results: List[TestResult],
        source_lines: Dict[int, str] = None
    ) -> FaultLocalizationOutput:
        """
        Perform Tarantula fault localization analysis.
        
        Args:
            source_file: Path/name of the source file being analyzed
            test_results: List of test results with coverage information
            source_lines: Optional dict mapping line numbers to source code
        
        Returns:
            FaultLocalizationOutput with ranked suspicious lines
        """
        analysis_id = str(uuid.uuid4())[:8]
        
        # Separate passed and failed tests
        passed_tests = [t for t in test_results if t.status == "passed"]
        failed_tests = [t for t in test_results if t.status == "failed"]
        
        if not failed_tests:
            # No failures, no fault localization needed
            return FaultLocalizationOutput(
                analysis_id=analysis_id,
                source_file=source_file,
                total_tests=len(test_results),
                failed_tests=0,
                passed_tests=len(passed_tests),
                suspicious_lines=[]
            )
        
        # Build coverage matrix
        self._build_coverage_matrix(passed_tests, failed_tests)
        
        # Calculate suspiciousness scores
        suspicious_lines = self._calculate_suspiciousness(
            source_file,
            len(passed_tests),
            len(failed_tests),
            source_lines
        )
        
        # Sort by suspiciousness (highest first)
        suspicious_lines.sort(key=lambda x: x.suspiciousness_score, reverse=True)
        
        return FaultLocalizationOutput(
            analysis_id=analysis_id,
            source_file=source_file,
            total_tests=len(test_results),
            failed_tests=len(failed_tests),
            passed_tests=len(passed_tests),
            suspicious_lines=suspicious_lines
        )
    
    def _build_coverage_matrix(
        self,
        passed_tests: List[TestResult],
        failed_tests: List[TestResult]
    ):
        """
        Build a matrix tracking how many passed/failed tests cover each line.
        """
        self.line_coverage = {}
        
        # Count coverage in passed tests
        for test in passed_tests:
            for line_num in test.covered_lines:
                if line_num not in self.line_coverage:
                    self.line_coverage[line_num] = {"passed": 0, "failed": 0}
                self.line_coverage[line_num]["passed"] += 1
        
        # Count coverage in failed tests
        for test in failed_tests:
            for line_num in test.covered_lines:
                if line_num not in self.line_coverage:
                    self.line_coverage[line_num] = {"passed": 0, "failed": 0}
                self.line_coverage[line_num]["failed"] += 1
    
    def _calculate_suspiciousness(
        self,
        source_file: str,
        total_passed: int,
        total_failed: int,
        source_lines: Dict[int, str] = None
    ) -> List[SuspiciousLine]:
        """
        Calculate Tarantula suspiciousness score for each line.
        
        Formula:
        suspiciousness(s) = %failed(s) / (%failed(s) + %passed(s))
        
        Where:
        - %failed(s) = n_failed(s) / total_failed
        - %passed(s) = n_passed(s) / total_passed
        """
        suspicious_lines = []
        
        for line_num, coverage in self.line_coverage.items():
            n_passed = coverage["passed"]
            n_failed = coverage["failed"]
            
            # Calculate percentages
            if total_failed > 0:
                pct_failed = n_failed / total_failed
            else:
                pct_failed = 0.0
            
            if total_passed > 0:
                pct_passed = n_passed / total_passed
            else:
                pct_passed = 0.0
            
            # Tarantula formula
            denominator = pct_failed + pct_passed
            if denominator > 0:
                suspiciousness = pct_failed / denominator
            else:
                suspiciousness = 0.0
            
            # Get source code for this line
            line_content = ""
            if source_lines and line_num in source_lines:
                line_content = source_lines[line_num]
            else:
                line_content = f"<line {line_num}>"
            
            suspicious_lines.append(SuspiciousLine(
                file_name=source_file,
                line_number=line_num,
                line_content=line_content,
                suspiciousness_score=round(suspiciousness, 4),
                failed_coverage=n_failed,
                passed_coverage=n_passed
            ))
        
        return suspicious_lines
    
    def get_top_suspicious(
        self,
        analysis: FaultLocalizationOutput,
        top_n: int = 10
    ) -> List[SuspiciousLine]:
        """
        Get the top N most suspicious lines from an analysis.
        """
        return analysis.suspicious_lines[:top_n]


def analyze_from_executions(
    source_file: str,
    source_code: str,
    executions: List[tuple[str, TestExecutionOutput]]
) -> FaultLocalizationOutput:
    """
    Convenience function to perform fault localization from test executions.
    
    Args:
        source_file: Name of the source file
        source_code: The actual source code (for line content)
        executions: List of (test_id, TestExecutionOutput) tuples
    
    Returns:
        FaultLocalizationOutput with Tarantula analysis
    """
    # Parse source code into lines
    source_lines = {}
    for i, line in enumerate(source_code.split('\n'), start=1):
        source_lines[i] = line
    
    # Convert executions to TestResult format
    test_results = []
    for test_id, execution in executions:
        # Extract covered lines from coverage data
        covered_lines = [
            cov.line_number
            for cov in execution.coverage_data
            if cov.execution_count > 0
        ]
        
        test_results.append(TestResult(
            test_id=test_id,
            status=execution.execution_status,
            covered_lines=covered_lines
        ))
    
    # Perform analysis
    localizer = TarantulaLocalizer()
    return localizer.analyze(source_file, test_results, source_lines)


def calculate_ochiai_score(n_failed: int, n_passed: int, total_failed: int) -> float:
    """
    Alternative fault localization metric: Ochiai
    
    Ochiai(s) = n_failed(s) / sqrt(total_failed * (n_failed(s) + n_passed(s)))
    
    Often performs better than Tarantula in practice.
    """
    denominator = total_failed * (n_failed + n_passed)
    if denominator == 0:
        return 0.0
    
    import math
    return n_failed / math.sqrt(denominator)


def calculate_jaccard_score(n_failed: int, n_passed: int, total_failed: int) -> float:
    """
    Alternative fault localization metric: Jaccard
    
    Jaccard(s) = n_failed(s) / (total_failed + n_passed(s))
    """
    denominator = total_failed + n_passed
    if denominator == 0:
        return 0.0
    
    return n_failed / denominator

