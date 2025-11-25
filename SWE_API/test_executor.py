"""
F4: Test Execution with Coverage Instrumentation (gcov)
Automates compilation, execution, and coverage collection workflow.
"""

import os
import subprocess
import tempfile
import time
import uuid
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from models import TestExecutionOutput, GCovData


class TestExecutor:
    """
    Handles compilation with coverage flags, test execution, 
    and gcov-based coverage data collection.
    """
    
    def __init__(self, work_dir: Optional[str] = None):
        """
        Initialize test executor.
        
        Args:
            work_dir: Working directory for compilation and execution.
                     If None, uses a temporary directory.
        """
        if work_dir:
            self.work_dir = Path(work_dir)
            self.work_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.work_dir = Path(tempfile.mkdtemp(prefix="test_exec_"))
        
        self.cleanup_files = []
    
    def compile_with_coverage(
        self,
        source_code: str,
        source_filename: str = "test_program.cpp"
    ) -> tuple[bool, str, str]:
        """
        Compile C/C++ source code with GCC coverage flags.
        
        Args:
            source_code: C/C++ source code to compile
            source_filename: Name for the source file
        
        Returns:
            (success, binary_path, error_message)
        """
        source_path = self.work_dir / source_filename
        binary_path = self.work_dir / "test_program"
        
        # Write source code to file
        try:
            with open(source_path, 'w') as f:
                f.write(source_code)
            self.cleanup_files.append(source_path)
        except Exception as e:
            return False, "", f"Failed to write source: {e}"
        
        # Compile with coverage flags
        # -fprofile-arcs: Generates .gcda files (execution counts)
        # -ftest-coverage: Generates .gcno files (graph info)
        # --coverage: Shorthand for both
        compile_cmd = [
            "g++",
            "--coverage",           # Enable coverage instrumentation
            "-g",                    # Debug symbols
            "-O0",                   # No optimization for accurate coverage
            str(source_path),
            "-o", str(binary_path)
        ]
        
        try:
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.work_dir)
            )
            
            if result.returncode != 0:
                return False, "", f"Compilation failed: {result.stderr}"
            
            self.cleanup_files.append(binary_path)
            return True, str(binary_path), ""
            
        except subprocess.TimeoutExpired:
            return False, "", "Compilation timeout"
        except Exception as e:
            return False, "", f"Compilation error: {e}"
    
    def execute_test(
        self,
        binary_path: str,
        test_inputs: List[Any],
        expected_output: Optional[Any] = None,
        timeout: int = 5
    ) -> TestExecutionOutput:
        """
        Execute compiled binary with test inputs and collect results.
        
        Args:
            binary_path: Path to compiled binary
            test_inputs: List of input values for the program
            expected_output: Expected output (for pass/fail determination)
            timeout: Execution timeout in seconds
        
        Returns:
            TestExecutionOutput with execution results and coverage data
        """
        test_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Prepare input string
        input_str = "\n".join(str(inp) for inp in test_inputs) + "\n"
        
        try:
            # Execute the binary
            result = subprocess.run(
                [binary_path],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.work_dir)
            )
            
            execution_time = time.time() - start_time
            output = result.stdout.strip()
            error = result.stderr.strip() if result.stderr else None
            
            # Determine pass/fail status
            if result.returncode != 0:
                status = "failed"
            elif expected_output is not None:
                status = "passed" if str(output) == str(expected_output) else "failed"
            else:
                status = "passed"  # No expected output, just check if it ran
            
            # Collect coverage data
            coverage_data, branches_taken = self._collect_coverage_data()
            
            return TestExecutionOutput(
                test_id=test_id,
                execution_status=status,
                output=output,
                error=error,
                coverage_data=coverage_data,
                branches_taken=branches_taken,
                execution_time=round(execution_time, 3)
            )
            
        except subprocess.TimeoutExpired:
            return TestExecutionOutput(
                test_id=test_id,
                execution_status="error",
                output=None,
                error="Execution timeout",
                coverage_data=[],
                branches_taken=[],
                execution_time=timeout
            )
        except Exception as e:
            return TestExecutionOutput(
                test_id=test_id,
                execution_status="error",
                output=None,
                error=str(e),
                coverage_data=[],
                branches_taken=[],
                execution_time=time.time() - start_time
            )
    
    def _collect_coverage_data(self) -> tuple[List[GCovData], List[str]]:
        """
        Run gcov and parse coverage data.
        
        Returns:
            (coverage_data, branches_taken)
        """
        coverage_data = []
        branches_taken = []
        
        try:
            # Find .gcda files (execution count data)
            gcda_files = list(self.work_dir.glob("*.gcda"))
            
            if not gcda_files:
                return coverage_data, branches_taken
            
            # Run gcov on the source file
            gcov_cmd = ["gcov", "-b", "test_program.cpp"]  # -b for branch coverage
            
            result = subprocess.run(
                gcov_cmd,
                capture_output=True,
                text=True,
                cwd=str(self.work_dir),
                timeout=10
            )
            
            # Parse gcov output file
            gcov_file = self.work_dir / "test_program.cpp.gcov"
            if gcov_file.exists():
                coverage_data = self._parse_gcov_file(gcov_file)
                branches_taken = self._extract_branches(coverage_data)
            
        except Exception as e:
            print(f"Coverage collection error: {e}")
        
        return coverage_data, branches_taken
    
    def _parse_gcov_file(self, gcov_file: Path) -> List[GCovData]:
        """
        Parse a .gcov file to extract line-by-line coverage.
        
        gcov format:
            execution_count:line_number:source_code
        Example:
            5:   10:    int x = 0;
            -:   11:    // comment
            #####:   12:    unreachable();
        """
        coverage_data = []
        
        try:
            with open(gcov_file, 'r') as f:
                for line in f:
                    # Match pattern: "count:line_num:source"
                    match = re.match(r'\s*([^:]+):\s*(\d+):(.*)', line)
                    if match:
                        count_str = match.group(1).strip()
                        line_num = int(match.group(2))
                        source = match.group(3)
                        
                        # Parse execution count
                        if count_str == '-':
                            exec_count = -1  # Non-executable line
                        elif count_str == '#####' or count_str == '=====':
                            exec_count = 0   # Not executed
                        else:
                            try:
                                exec_count = int(count_str)
                            except ValueError:
                                exec_count = -1
                        
                        coverage_data.append(GCovData(
                            file_name="test_program.cpp",
                            line_number=line_num,
                            execution_count=exec_count,
                            source_line=source
                        ))
        except Exception as e:
            print(f"Error parsing gcov file: {e}")
        
        return coverage_data
    
    def _extract_branches(self, coverage_data: List[GCovData]) -> List[str]:
        """
        Extract branch identifiers from coverage data.
        A branch is taken if the line with decision logic was executed.
        """
        branches = []
        
        for i, cov in enumerate(coverage_data):
            if cov.execution_count > 0:
                source = cov.source_line.strip()
                
                # Identify decision points (branches)
                if any(keyword in source for keyword in ['if', 'else', 'for', 'while', 'switch', 'case']):
                    # Create branch identifier
                    branch_id = f"L{cov.line_number}"
                    branches.append(branch_id)
                    
                    # For if statements, we can have true/false branches
                    if 'if' in source:
                        branches.append(f"L{cov.line_number}_true")
                        # Check if next line was executed for false branch
                        if i + 1 < len(coverage_data):
                            next_cov = coverage_data[i + 1]
                            if next_cov.execution_count > 0:
                                branches.append(f"L{cov.line_number}_false")
        
        return branches
    
    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.cleanup_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()


def execute_test_case(
    source_code: str,
    test_inputs: List[Any],
    expected_output: Optional[Any] = None,
    work_dir: Optional[str] = None
) -> TestExecutionOutput:
    """
    Convenience function to compile and execute a single test case.
    
    Args:
        source_code: C/C++ source code
        test_inputs: Input values for the test
        expected_output: Expected output for pass/fail determination
        work_dir: Working directory (uses temp if None)
    
    Returns:
        TestExecutionOutput with results and coverage data
    """
    executor = TestExecutor(work_dir)
    
    # Compile
    success, binary_path, error = executor.compile_with_coverage(source_code)
    
    if not success:
        return TestExecutionOutput(
            test_id=str(uuid.uuid4())[:8],
            execution_status="error",
            output=None,
            error=f"Compilation failed: {error}",
            coverage_data=[],
            branches_taken=[],
            execution_time=0.0
        )
    
    # Execute
    result = executor.execute_test(binary_path, test_inputs, expected_output)
    
    return result

