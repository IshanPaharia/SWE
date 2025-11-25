from reporter import FaultLocalizationReporter
from models import SuspiciousLine, FaultLocalizationOutput


def test_generate_report_and_summary():
    s1 = SuspiciousLine(file_name='f', line_number=10, line_content='x=1;', suspiciousness_score=0.9, failed_coverage=2, passed_coverage=0)
    s2 = SuspiciousLine(file_name='f', line_number=20, line_content='y=2;', suspiciousness_score=0.4, failed_coverage=1, passed_coverage=1)
    analysis = FaultLocalizationOutput(analysis_id='a', source_file='f', total_tests=3, failed_tests=2, passed_tests=1, suspicious_lines=[s1, s2])
    reporter = FaultLocalizationReporter()
    report = reporter.generate_report(analysis, top_n=2)
    assert report.report_id
    assert 'Fault' in report.summary or 'Top' in report.summary


def test_format_text_report_contains_sections():
    s1 = SuspiciousLine(file_name='f', line_number=10, line_content='x=1;', suspiciousness_score=0.9, failed_coverage=2, passed_coverage=0)
    analysis = FaultLocalizationOutput(analysis_id='a', source_file='f', total_tests=1, failed_tests=1, passed_tests=0, suspicious_lines=[s1])
    reporter = FaultLocalizationReporter()
    report = reporter.generate_report(analysis)
    text = reporter.format_text_report(report)
    assert 'FAULT LOCALIZATION REPORT' in text
    assert 'RECOMMENDATIONS' in text


def test_format_json_report_is_serializable():
    s1 = SuspiciousLine(file_name='f', line_number=5, line_content='z=0;', suspiciousness_score=0.5, failed_coverage=1, passed_coverage=0)
    analysis = FaultLocalizationOutput(analysis_id='a', source_file='f', total_tests=1, failed_tests=1, passed_tests=0, suspicious_lines=[s1])
    reporter = FaultLocalizationReporter()
    report = reporter.generate_report(analysis)
    j = reporter.format_json_report(report)
    assert isinstance(j, dict)
