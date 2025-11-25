from fault_localizer import TarantulaLocalizer, calculate_ochiai_score, calculate_jaccard_score
from models import TestResult


def test_tarantula_no_failures_returns_empty():
    passed = TestResult(test_id='p', status='passed', covered_lines=[1, 2])
    localizer = TarantulaLocalizer()
    out = localizer.analyze('f.cpp', [passed], source_lines={1: 'a', 2: 'b'})
    assert out.failed_tests == 0
    assert out.suspicious_lines == []


def test_tarantula_basic_scores():
    passed = TestResult(test_id='p', status='passed', covered_lines=[1])
    failed = TestResult(test_id='f', status='failed', covered_lines=[1, 2])
    localizer = TarantulaLocalizer()
    out = localizer.analyze('f.cpp', [passed, failed], source_lines={1: 'a', 2: 'b'})
    assert out.failed_tests == 1
    assert out.passed_tests == 1
    # Ensure suspicious lines include both lines
    nums = [s.line_number for s in out.suspicious_lines]
    assert 1 in nums and 2 in nums


def test_metrics_edge_cases():
    # Ochiai denominator zero
    assert calculate_ochiai_score(0, 0, 0) == 0.0
    # Jaccard denominator zero
    assert calculate_jaccard_score(0, 0, 0) == 0.0
    # Known values
    assert calculate_ochiai_score(1, 0, 1) == 1.0
    assert calculate_jaccard_score(1, 0, 1) == 1.0
