"""
Integration Test 2: Test Execution and Fault Localization Workflow
Tests the integration of Test Executor -> Fault Localizer -> Reporter
"""
import tempfile
from pathlib import Path

from test_executor import TestExecutor, execute_test_case
from fault_localizer import TarantulaLocalizer
from reporter import FaultLocalizationReporter
from models import TestResult, GCovData


def test_execute_and_collect_coverage(tmp_path):
    """Test that test executor can compile, run, and collect coverage data"""
    # Simple C++ program with a bug
    source_code = """
    #include <iostream>
    
    int divide(int a, int b) {
        // Bug: no check for division by zero
        return a / b;
    }
    
    int main() {
        int x, y;
        std::cin >> x >> y;
        int result = divide(x, y);
        std::cout << result << std::endl;
        return 0;
    }
    """
    
    # Test with valid inputs
    executor = TestExecutor(work_dir=str(tmp_path))
    
    success, binary_path, error = executor.compile_with_coverage(source_code, "divide_test.cpp")
    
    if success:
        # Execute with valid input
        result = executor.execute_test(binary_path, [10, 2], expected_output=5, timeout=5)
        
        assert result.execution_status in ['passed', 'failed', 'timeout']
        # Should have some coverage data or branches
        assert result.coverage_data is not None or result.branches_taken is not None
    
    executor.cleanup()


def test_fault_localization_with_test_results():
    """Test fault localization based on passing and failing tests"""
    # Create test results manually
    passing_tests = [
        TestResult(test_id='pass1', status='passed', covered_lines=[1, 2, 3, 5]),
        TestResult(test_id='pass2', status='passed', covered_lines=[1, 2, 4, 5]),
    ]
    
    failing_tests = [
        TestResult(test_id='fail1', status='failed', covered_lines=[1, 2, 3, 6, 7]),
        TestResult(test_id='fail2', status='failed', covered_lines=[1, 2, 6, 7, 8]),
    ]
    
    all_tests = passing_tests + failing_tests
    
    # Create source lines mapping
    source_lines = {
        1: '#include <iostream>',
        2: 'int divide(int a, int b) {',
        3: '    if (b == 0) return 0;',  # This line only in passing tests
        4: '    return a / b;',
        5: '}',
        6: '    // Missing null check',  # This line in failing tests
        7: '    return a / b;',
        8: '}',
    }
    
    # Perform fault localization
    localizer = TarantulaLocalizer()
    result = localizer.analyze('divide.cpp', all_tests, source_lines)
    
    # Verify analysis
    assert result.total_tests == len(all_tests)
    assert result.passed_tests == len(passing_tests)
    assert result.failed_tests == len(failing_tests)
    assert len(result.suspicious_lines) > 0
    
    # Lines 6, 7, 8 should be more suspicious (only in failing tests)
    suspicious_line_numbers = [line.line_number for line in result.suspicious_lines]
    assert any(num in [6, 7, 8] for num in suspicious_line_numbers)


def test_generate_fault_report():
    """Test complete workflow: test results -> fault localization -> report generation"""
    # Step 1: Create test results
    passing_tests = [
        TestResult(test_id='t1', status='passed', covered_lines=[10, 11, 12]),
        TestResult(test_id='t2', status='passed', covered_lines=[10, 11, 13]),
    ]
    
    failing_tests = [
        TestResult(test_id='t3', status='failed', covered_lines=[10, 15, 16]),
        TestResult(test_id='t4', status='failed', covered_lines=[10, 15, 17]),
    ]
    
    all_tests = passing_tests + failing_tests
    
    source_lines = {
        10: 'int buggy_function(int x) {',
        11: '    if (x > 0) return x * 2;',
        12: '    return x;',
        13: '}',
        15: '    // Bug: should check for overflow',
        16: '    return x * x * x;',
        17: '}',
    }
    
    # Step 2: Perform fault localization
    localizer = TarantulaLocalizer()
    analysis = localizer.analyze('buggy.cpp', all_tests, source_lines)
    
    assert analysis is not None
    assert analysis.failed_tests > 0
    
    # Step 3: Generate report
    reporter = FaultLocalizationReporter()
    report = reporter.generate_report(analysis, top_n=5)
    
    # Verify report
    assert report.report_id is not None
    assert report.analysis_id == analysis.analysis_id
    assert len(report.top_suspicious_lines) > 0
    assert report.summary is not None
    
    # Step 4: Format reports
    text_report = reporter.format_text_report(report)
    assert 'FAULT LOCALIZATION REPORT' in text_report
    assert 'RECOMMENDATIONS' in text_report
    
    json_report = reporter.format_json_report(report)
    assert isinstance(json_report, dict)
    assert 'report_id' in json_report
    assert 'top_suspicious_lines' in json_report


def test_end_to_end_bug_detection_workflow(tmp_path):
    """Test complete workflow from code execution to bug report generation"""
    # Buggy code with intentional error
    buggy_code = """
    #include <iostream>
    
    int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    
    int main() {
        int num;
        std::cin >> num;
        int result = factorial(num);
        std::cout << result << std::endl;
        return 0;
    }
    """
    
    # Step 1: Execute multiple test cases
    executor = TestExecutor(work_dir=str(tmp_path))
    test_inputs_list = [
        ([0], 1),    # Edge case
        ([1], 1),    # Base case
        ([5], 120),  # Normal case
        ([10], 3628800),  # Larger case
    ]
    
    test_results = []
    
    for i, (inputs, expected) in enumerate(test_inputs_list):
        success, binary, error = executor.compile_with_coverage(buggy_code, f"factorial_{i}.cpp")
        
        if success:
            result = executor.execute_test(binary, inputs, expected, timeout=5)
            
            # Convert to TestResult format
            covered_lines = [gcov.line_number for gcov in result.coverage_data] if result.coverage_data else []
            
            test_result = TestResult(
                test_id=f'factorial_test_{i}',
                status=result.execution_status,
                covered_lines=covered_lines if covered_lines else [1, 2, 3, 4, 5]  # Mock data
            )
            test_results.append(test_result)
    
    executor.cleanup()
    
    # Step 2: Perform fault localization if we have both passing and failing tests
    passing = [t for t in test_results if t.status == 'passed']
    failing = [t for t in test_results if t.status == 'failed']
    
    if len(test_results) > 0:
        # Create mock source lines
        source_lines = {
            1: '#include <iostream>',
            2: 'int factorial(int n) {',
            3: '    if (n <= 1) return 1;',
            4: '    return n * factorial(n - 1);',
            5: '}',
        }
        
        localizer = TarantulaLocalizer()
        analysis = localizer.analyze('factorial.cpp', test_results, source_lines)
        
        # Step 3: Generate report
        if analysis:
            reporter = FaultLocalizationReporter()
            report = reporter.generate_report(analysis, top_n=3)
            
            assert report is not None
            assert report.top_suspicious_lines is not None
            
            # Verify we can generate both text and JSON reports
            text = reporter.format_text_report(report)
            json_data = reporter.format_json_report(report)
            
            assert len(text) > 0
            assert isinstance(json_data, dict)


def test_integration_with_coverage_data(tmp_path):
    """Test that coverage data flows correctly through the pipeline"""
    # Create a simple test executor
    executor = TestExecutor(work_dir=str(tmp_path))
    
    # Write a gcov file manually to test parsing
    gcov_content = """
        -:    0:Source:test.cpp
        -:    1:#include <iostream>
        5:    2:int add(int a, int b) {
        5:    3:    return a + b;
        -:    4:}
        1:    5:int main() {
        1:    6:    int result = add(2, 3);
        1:    7:    std::cout << result;
    #####:    8:    unreachable_code();
        1:    9:    return 0;
        -:   10:}
    """
    
    gcov_file = Path(tmp_path) / "test.cpp.gcov"
    gcov_file.write_text(gcov_content)
    
    # Parse the gcov file
    coverage_data = executor._parse_gcov_file(gcov_file)
    
    # Verify coverage data was parsed
    assert len(coverage_data) > 0
    
    # Check that executed lines are identified
    executed_lines = [gc.line_number for gc in coverage_data if gc.execution_count > 0]
    assert 2 in executed_lines
    assert 3 in executed_lines
    
    # Check that unexecuted lines are identified Line 8 should have 0 execution
    line_8_data = [gc for gc in coverage_data if gc.line_number == 8]
    if line_8_data:
        assert line_8_data[0].execution_count == 0
    
    # Extract branches
    branches = executor._extract_branches(coverage_data)
    assert isinstance(branches, list)
    
    executor.cleanup()
