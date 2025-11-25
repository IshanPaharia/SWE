import sys
import os

# Add parent directory to sys.path once for all tests
# This is the proper place for path configuration in pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



def pytest_runtest_logreport(report):
    """Pytest hook: print a message for each passed test call phase.

    This prints a concise message when a test passes (the call phase).
    """
    try:
        when = getattr(report, 'when', None)
        outcome = getattr(report, 'outcome', None)
        if when == 'call' and outcome == 'passed':
            # report.nodeid contains the test path::name
            print(f"[TEST PASSED] {report.nodeid}", flush=True)
    except Exception:
        # Don't let reporting errors break the test run
        pass
