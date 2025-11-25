from test_executor import TestExecutor


def test_parse_gcov_file_and_line_numbers(tmp_path):
    te = TestExecutor(work_dir=str(tmp_path))
    gcov_content = """
        10:   5:    int x = 0;
        0:   6:    if (x>0) x++;
        -:   7:    // comment
    """
    f = tmp_path / 'test_program.cpp.gcov'
    f.write_text(gcov_content)
    parsed = te._parse_gcov_file(f)
    assert any(d.line_number == 5 for d in parsed)


def test_extract_branches_identifies_if(tmp_path):
    te = TestExecutor(work_dir=str(tmp_path))
    gcov_content = """
        5:   10:    if (x > 0) x++;
        1:   11:    y = x;
    """
    f = tmp_path / 'test_program.cpp.gcov'
    f.write_text(gcov_content)
    parsed = te._parse_gcov_file(f)
    branches = te._extract_branches(parsed)
    assert any(b.startswith('L10') for b in branches)


def test_collect_coverage_no_gcda(tmp_path):
    # If no .gcda files exist, _collect_coverage_data should return empty lists
    te = TestExecutor(work_dir=str(tmp_path))
    coverage, branches = te._collect_coverage_data()
    assert coverage == []
    assert branches == []
