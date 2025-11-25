# Automated Test Case Generator with Fault Localization

A comprehensive FastAPI-based system for automated test case generation using Genetic Algorithms (GA) and fault localization using the Tarantula algorithm. This system analyzes C/C++ code, generates test cases, evaluates branch coverage, and identifies suspicious code lines when tests fail.

## Features

### F1: Control Flow Graph (CFG) Generation
- Parses C/C++ source code using LibClang
- Generates detailed Control Flow Graphs with nodes and edges
- Identifies decision points (if, for, while, switch statements)
- Detects function parameters for test input generation

### F2: Genetic Algorithm Population Management
- Initializes random populations of test cases
- Evolves populations through selection, crossover, and mutation
- Supports tournament selection for parent selection
- Configurable mutation and crossover rates

### F3: Fitness Evaluation via Branch Coverage
- Evaluates test case fitness based on branch coverage
- Rewards test cases that discover new branches
- Integrates with gcov for accurate coverage measurement
- Supports both individual and population-wide evaluation

### F4: Test Execution with Coverage Instrumentation
- Compiles C/C++ code with GCC coverage flags (--coverage)
- Executes instrumented binaries with test inputs
- Collects line-by-line coverage data using gcov
- Tracks branch execution and coverage metrics

### F5: Spectrum-Based Fault Localization (Tarantula)
- Implements the Tarantula algorithm for fault localization
- Calculates suspiciousness scores for each code line
- Identifies lines more likely to contain faults
- Requires both passing and failing test cases

### F6: Report Generation
- Generates comprehensive fault localization reports
- Ranks suspicious lines by suspiciousness score
- Provides actionable debugging recommendations
- Supports both JSON and human-readable text formats

## Installation

### Prerequisites

1. **Python 3.8+**
2. **GCC/G++ with gcov** (for coverage instrumentation)
3. **LibClang** (for C/C++ parsing)

### Install LLVM/Clang (Windows)

Download and install LLVM from: https://releases.llvm.org/

After installation, you may need to configure the library path in `cfg_parser.py`:

```python
import clang.cindex
clang.cindex.Config.set_library_path(r'C:\Program Files\LLVM\bin')
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

## API Endpoints

### F1: CFG Generation

**POST** `/analysis/generate-cfg`

Generate a Control Flow Graph from C/C++ source code.

```json
{
  "filename": "test.cpp",
  "source_code": "#include <iostream>\nint max(int a, int b) {\n    if (a > b) return a;\n    return b;\n}"
}
```

Response:
```json
{
  "cfg_id": "abc123",
  "total_nodes": 3,
  "nodes": [...],
  "edges": [...],
  "complexity": 2,
  "required_inputs": ["int", "int"]
}
```

### F2: Initialize Population

**POST** `/ga/initialize`

Initialize a random population of test cases based on CFG.

```json
{
  "cfg_id": "abc123",
  "population_size": 50
}
```

Response:
```json
{
  "generation_id": 0,
  "status": "Initialized",
  "population_count": 50,
  "individuals": [
    {
      "id": "test_001",
      "genes": [42, -15],
      "fitness_score": 0.0
    }
  ]
}
```

### F2: Evolve Population

**POST** `/ga/evolve`

Evolve the population to the next generation.

```json
{
  "cfg_id": "abc123",
  "mutation_rate": 0.1,
  "crossover_rate": 0.8
}
```

### F3: Evaluate Fitness

**POST** `/fitness/evaluate`

Evaluate fitness of a single test case.

```json
{
  "cfg_id": "abc123",
  "test_case_id": "test_001",
  "source_file": "test.cpp",
  "test_inputs": [42, -15]
}
```

**POST** `/fitness/evaluate-population`

Evaluate fitness for entire population (query params: `cfg_id`, `source_code`).

### F4: Execute Tests

**POST** `/test/execute`

Execute a single test case with coverage instrumentation.

```json
{
  "source_file": "test.cpp",
  "source_code": "#include <iostream>\nint max(int a, int b) {...}",
  "test_inputs": [42, -15],
  "expected_output": "42"
}
```

Response:
```json
{
  "test_id": "xyz789",
  "execution_status": "passed",
  "output": "42",
  "error": null,
  "coverage_data": [
    {
      "file_name": "test_program.cpp",
      "line_number": 3,
      "execution_count": 1,
      "source_line": "    if (a > b) return a;"
    }
  ],
  "branches_taken": ["L3", "L3_true"],
  "execution_time": 0.123
}
```

**POST** `/test/execute-batch`

Execute multiple test cases (query params: `source_code`, body: `test_cases` array).

### F5: Fault Localization

**POST** `/fault-localization/analyze`

Perform Tarantula fault localization analysis.

```json
{
  "source_file": "buggy_program.cpp",
  "test_results": [
    {
      "test_id": "test_001",
      "status": "passed",
      "covered_lines": [1, 2, 3, 5]
    },
    {
      "test_id": "test_002",
      "status": "failed",
      "covered_lines": [1, 2, 4, 5]
    }
  ]
}
```

Response:
```json
{
  "analysis_id": "fault_123",
  "source_file": "buggy_program.cpp",
  "total_tests": 2,
  "failed_tests": 1,
  "passed_tests": 1,
  "suspicious_lines": [
    {
      "file_name": "buggy_program.cpp",
      "line_number": 4,
      "line_content": "    result = x / 0;",
      "suspiciousness_score": 1.0,
      "failed_coverage": 1,
      "passed_coverage": 0
    }
  ]
}
```

**POST** `/fault-localization/analyze-from-executions`

Perform fault localization using stored test execution results (query params: `source_file`, `source_code`, `test_ids`).

### F6: Report Generation

**POST** `/report/generate`

Generate a comprehensive fault localization report.

```json
{
  "analysis_id": "fault_123",
  "top_n": 10
}
```

Response:
```json
{
  "report_id": "rpt_456",
  "generated_at": "2025-11-25T10:30:00",
  "analysis_id": "fault_123",
  "summary": "Fault Localization Report for: buggy_program.cpp | Total tests executed: 10 | Passed: 7, Failed: 3 | Suspicious lines identified: 15 | Top 10 lines reported below",
  "top_suspicious_lines": [...],
  "recommendations": [
    "HIGH PRIORITY: Line 42 has very high suspiciousness (0.95). Start debugging here.",
    "Found 2 line(s) ONLY executed in failed tests. These are highly suspect: [42, 57]"
  ]
}
```

**GET** `/report/{report_id}/text`

Get report in human-readable text format.

**GET** `/report/{report_id}/json`

Get report in JSON format.

### Utility Endpoints

**GET** `/status`

Get system status and statistics.

**DELETE** `/clear`

Clear all stored data (useful for testing).

## Complete Workflow Example

### 1. Generate CFG from Source Code

```python
import requests

base_url = "http://localhost:8000"

source_code = """
#include <iostream>
using namespace std;

int divide(int a, int b) {
    if (b == 0) {
        return -1;  // Error case
    }
    return a / b;
}

int main() {
    int x, y;
    cin >> x >> y;
    int result = divide(x, y);
    cout << result << endl;
    return 0;
}
"""

# Step 1: Generate CFG
response = requests.post(f"{base_url}/analysis/generate-cfg", json={
    "filename": "divide.cpp",
    "source_code": source_code
})
cfg = response.json()
cfg_id = cfg["cfg_id"]
print(f"CFG generated: {cfg_id}")
print(f"Required inputs: {cfg['required_inputs']}")
```

### 2. Initialize and Evolve GA Population

```python
# Step 2: Initialize population
response = requests.post(f"{base_url}/ga/initialize", json={
    "cfg_id": cfg_id,
    "population_size": 20
})
population = response.json()
print(f"Population initialized: {population['population_count']} individuals")

# Step 3: Evolve population (optional, for demonstration)
response = requests.post(f"{base_url}/ga/evolve", json={
    "cfg_id": cfg_id,
    "mutation_rate": 0.15,
    "crossover_rate": 0.75
})
evolved_pop = response.json()
print(f"Population evolved to generation {evolved_pop['generation_id']}")
```

### 3. Execute Tests with Coverage

```python
# Step 3: Execute multiple test cases
test_cases = [
    [10, 2],   # Should pass
    [15, 3],   # Should pass
    [20, 0],   # Edge case - divide by zero
    [100, 5],  # Should pass
]

test_ids = []
for test_inputs in test_cases:
    response = requests.post(f"{base_url}/test/execute", json={
        "source_file": "divide.cpp",
        "source_code": source_code,
        "test_inputs": test_inputs,
        "expected_output": None  # We'll check manually
    })
    result = response.json()
    test_ids.append(result["test_id"])
    print(f"Test {result['test_id']}: {result['execution_status']} - Output: {result['output']}")
```

### 4. Evaluate Fitness

```python
# Step 4: Evaluate population fitness
response = requests.post(
    f"{base_url}/fitness/evaluate-population",
    params={"cfg_id": cfg_id, "source_code": source_code}
)
fitness = response.json()
print(f"Best fitness: {fitness['best_fitness']}")
print(f"Average fitness: {fitness['avg_fitness']}")
```

### 5. Perform Fault Localization

```python
# Step 5: Prepare test results for fault localization
# (Assuming we manually marked some tests as failed based on incorrect output)

test_results = [
    {"test_id": test_ids[0], "status": "passed", "covered_lines": [4, 5, 6, 7, 9, 10]},
    {"test_id": test_ids[1], "status": "passed", "covered_lines": [4, 5, 6, 7, 9, 10]},
    {"test_id": test_ids[2], "status": "failed", "covered_lines": [4, 5, 6, 9, 10]},  # Missed line 7
    {"test_id": test_ids[3], "status": "passed", "covered_lines": [4, 5, 6, 7, 9, 10]},
]

response = requests.post(f"{base_url}/fault-localization/analyze", json={
    "source_file": "divide.cpp",
    "test_results": test_results
})
analysis = response.json()
analysis_id = analysis["analysis_id"]
print(f"Fault analysis complete: {analysis_id}")
print(f"Top suspicious line: Line {analysis['suspicious_lines'][0]['line_number']}")
```

### 6. Generate Report

```python
# Step 6: Generate comprehensive report
response = requests.post(f"{base_url}/report/generate", json={
    "analysis_id": analysis_id,
    "top_n": 5
})
report = response.json()
report_id = report["report_id"]

print("\n=== FAULT LOCALIZATION REPORT ===")
print(report["summary"])
print("\nTop Suspicious Lines:")
for line in report["top_suspicious_lines"]:
    print(f"  Line {line['line_number']}: {line['suspiciousness_score']:.4f} - {line['line_content']}")

print("\nRecommendations:")
for i, rec in enumerate(report["recommendations"], 1):
    print(f"  {i}. {rec}")

# Get text report
response = requests.get(f"{base_url}/report/{report_id}/text")
print("\n" + response.text)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
├─────────────────────────────────────────────────────────────────┤
│  F1: CFG Parser     │  F2: GA Engine      │  F3: Fitness Eval   │
│  (cfg_parser.py)    │  (genetic_engine.py)│  (fitness_eval.py)  │
├─────────────────────────────────────────────────────────────────┤
│  F4: Test Executor  │  F5: Fault Localizer │  F6: Reporter      │
│  (test_executor.py) │  (fault_localizer.py)│  (reporter.py)     │
├─────────────────────────────────────────────────────────────────┤
│                     Models (models.py)                           │
│                     Database (database.py)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Source Code** → F1 (CFG Parser) → **CFG with parameter info**
2. **CFG** → F2 (GA Engine) → **Population of test cases**
3. **Test Cases + Source Code** → F4 (Test Executor) → **Execution results + Coverage**
4. **Execution Results** → F3 (Fitness Evaluator) → **Fitness scores**
5. **Fitness Scores** → F2 (GA Engine) → **Evolved population** (loop back)
6. **Test Results (passed/failed)** → F5 (Fault Localizer) → **Suspicious lines**
7. **Suspicious Lines** → F6 (Reporter) → **Actionable report**

## Testing

Run the test suite:

```bash
pytest test/
```

Available tests:
- `test_f1_analysis.py`: Tests for CFG generation
- `test_f2_analysis.py`: Tests for GA population management

## Troubleshooting

### LibClang Not Found

If you get `LibClang not found` errors:

1. Install LLVM from https://releases.llvm.org/
2. Add LLVM bin directory to your PATH
3. Or set the library path in `cfg_parser.py`:

```python
clang.cindex.Config.set_library_path(r'C:\Program Files\LLVM\bin')
```

### GCC/gcov Not Found

Make sure GCC is installed and in your PATH:

```bash
gcc --version
gcov --version
```

On Windows, install MinGW-w64 or use WSL.

### Coverage Data Not Generated

Ensure:
1. Source code compiles successfully
2. Binary executes without crashing
3. `.gcda` and `.gcno` files are created in the working directory

## Contributing

This is a research/educational project implementing automated test generation and fault localization techniques described in software engineering literature.

## License

MIT License

## References

- **Control Flow Graphs**: Used for program analysis and test generation
- **Genetic Algorithms**: Metaheuristic search for optimal test cases
- **Branch Coverage**: Measure of test suite quality
- **Tarantula Algorithm**: Jones & Harrold (2005) - Spectrum-based fault localization
- **gcov**: GNU coverage testing tool

## Authors

Software Requirements Specification Implementation
Version 1.0
November 2025
