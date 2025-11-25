# Search-Based Test Generation and Fault Localization System

An automated system for generating test cases and localizing faults in C/C++ programs using Genetic Algorithms and Spectrum-Based Fault Localization (Tarantula algorithm).

## Overview

This system combines evolutionary algorithms with software testing techniques to automatically generate test cases that maximize code coverage and identify suspicious code lines that may contain bugs. The system analyzes C/C++ source code, evolves test inputs using genetic algorithms, executes tests with coverage instrumentation, and applies the Tarantula fault localization technique to pinpoint potential bugs.

## Key Features

### Control Flow Graph (CFG) Analysis
- Parses C/C++ source code using LibClang and regex fallback
- Generates visual control flow graphs with entry, exit, decision, and statement nodes
- Detects function parameters automatically
- Calculates cyclomatic complexity

### Genetic Algorithm-Based Test Generation
- Initializes population of test cases with diverse inputs
- Evolves test cases over multiple generations using:
  - Tournament selection
  - Single-point crossover
  - Enhanced mutation strategies (boundary values, equal values, sign flips)
- Optimizes for maximum branch coverage

### Fitness Evaluation
- Compiles code with GCC coverage instrumentation (`--coverage` flag)
- Executes tests and measures branch coverage using gcov
- Calculates fitness scores based on code coverage metrics

### Test Execution
- Automatically determines expected outputs for simple functions (min, max, add, subtract, etc.)
- Executes compiled binaries with generated test inputs
- Captures actual outputs and compares with expected results
- Identifies passing and failing test cases

### Spectrum-Based Fault Localization
- Applies Tarantula algorithm to calculate suspiciousness scores
- Ranks code lines by likelihood of containing faults
- Analyzes execution patterns of passing vs. failing tests
- Generates detailed fault localization reports

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                       │
│  - Code input interface                                      │
│  - CFG visualization                                         │
│  - GA evolution monitoring                                   │
│  - Test results display                                      │
│  - Fault localization reports                                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ F1: CFG Parser (LibClang/Regex)                      │   │
│  └────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │ F2: Genetic Algorithm Engine                         │   │
│  │    - Population initialization                       │   │
│  │    - Selection, crossover, mutation                  │   │
│  │    - Multi-generation evolution                      │   │
│  └────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │ F3: Fitness Evaluator (gcov integration)             │   │
│  └────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │ F4: Test Executor (GCC + subprocess)                 │   │
│  └────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │ F5: Fault Localizer (Tarantula)                      │   │
│  └────────────────┬─────────────────────────────────────┘   │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │ F6: Report Generator                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **LibClang**: Python bindings for Clang compiler for C/C++ parsing
- **Pydantic**: Data validation and settings management
- **GCC/G++**: C/C++ compiler with coverage instrumentation support
- **gcov**: GNU coverage testing tool

### Frontend
- **React 18**: JavaScript library for building user interfaces
- **Vite**: Fast frontend build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **Lucide React**: Icon library

### Development Tools
- **Python 3.12+**: Backend runtime
- **Node.js 18+**: Frontend build tooling
- **MinGW-w64/GCC**: C/C++ compiler on Windows

## Installation

### Prerequisites

1. **Python 3.12 or higher**
2. **Node.js 18 or higher**
3. **GCC/G++ compiler with gcov support**
   - Windows: Install MinGW-w64 or MSYS2
   - Linux: `sudo apt install gcc g++ gcov`
   - macOS: `xcode-select --install`
4. **LLVM/Clang** (optional, for better CFG parsing)

### Backend Setup

```bash
cd SWE_API

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd SWE_Frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage Guide

### Step 1: Prepare Your Code
Write or paste a simple C/C++ function (2 parameters recommended) with a potential bug:

```cpp
#include <iostream>
using namespace std;

int findMin(int a, int b) {
    if (a <= b) {
        return a;
    } else {
        if (b < 0) {
            return 0;  // BUG: Should return b
        }
        return b;
    }
}

int main() {
    int x, y;
    cin >> x >> y;
    int result = findMin(x, y);
    cout << result << endl;
    return 0;
}
```

### Step 2: Generate Control Flow Graph
- Click "Execute" on Step 1
- View the visual CFG with nodes and edges
- Verify detected parameters and complexity metrics

### Step 3: Run Genetic Algorithm
- Configure population size (default: 20) and generations (default: 30)
- Click "Execute" on Step 2
- Watch the population evolve over generations
- Monitor best fitness and average fitness scores

### Step 4: Evaluate Fitness
- Automatically runs for top test cases
- Shows branch coverage for each test
- Displays coverage metrics and statistics

### Step 5: Execute Tests
- Tests run automatically with calculated expected outputs
- View passing and failing test cases
- Analyze which tests exposed the bug

### Step 6: View Fault Localization
- Examine suspicious lines ranked by Tarantula score
- Higher scores indicate higher likelihood of containing the fault
- Review execution statistics (passed/failed counts per line)

## How It Works

### Genetic Algorithm Evolution

1. **Initialization**: Generate random test inputs based on detected parameter types
2. **Fitness Evaluation**: Run tests and measure branch coverage
3. **Selection**: Use tournament selection to pick parents with high coverage
4. **Crossover**: Combine parent test cases to create offspring (75% rate)
5. **Mutation**: Apply various mutation strategies (30% rate):
   - Make parameters equal (detects `a == b` bugs)
   - Create positive/negative pairs (detects sign bugs)
   - Boundary value testing (0, -1, 1, -100, 100)
   - Small/large changes, sign flips
6. **Elitism**: Keep top 2 individuals in each generation
7. **Repeat**: Evolve for configured number of generations

### Tarantula Fault Localization

The suspiciousness of a statement `s` is calculated as:

```
suspiciousness(s) = (failed(s) / totalFailed) / 
                    ((failed(s) / totalFailed) + (passed(s) / totalPassed))
```

Where:
- `failed(s)`: Number of failing tests that execute statement `s`
- `passed(s)`: Number of passing tests that execute statement `s`
- Higher scores indicate statements more likely to contain faults

## API Endpoints

### F1: CFG Generation
```
POST /analysis/generate-cfg
Body: { "filename": "test.cpp", "source_code": "..." }
Response: { "cfg_id", "nodes", "edges", "complexity", "detected_parameters" }
```

### F2: GA Population
```
POST /ga/initialize
Body: { "cfg_id": "...", "population_size": 20 }

POST /ga/evolve
Body: { "cfg_id": "...", "mutation_rate": 0.3, "crossover_rate": 0.75 }
```

### F3: Fitness Evaluation
```
POST /fitness/evaluate
Body: { "cfg_id": "...", "test_case": {...}, "source_code": "..." }
Response: { "branch_coverage", "branches_covered" }
```

### F4: Test Execution
```
POST /test/execute
Body: { "source_filename": "...", "source_code": "...", 
        "test_inputs": [10, -5], "expected_output": -5 }
Response: { "execution_status", "output", "coverage_data" }
```

### F5: Fault Localization
```
POST /fault-localization/analyze
Body: { "source_filename": "...", "test_results": [...] }
Response: { "suspicious_lines": [...], "total_tests", "passed", "failed" }
```

## Configuration

### Backend Configuration (models.py)
- `population_size`: 5-1000 (default: 20)
- `mutation_rate`: 0.0-1.0 (default: 0.3)
- `crossover_rate`: 0.0-1.0 (default: 0.75)

### Frontend Configuration (WorkflowPage.jsx)
- `populationSize`: Default 20
- `generations`: Default 30

### Mutation Strategies
- Equal values mutation: 25% chance
- Positive/negative mutation: 25% chance
- Boundary value mutation: 10% chance
- Standard mutations: Applied at configured rate (30%)

## Limitations

### Supported Code Patterns
- 2-parameter functions (optimal)
- Simple arithmetic operations (min, max, add, subtract, multiply, divide)
- Integer inputs and outputs
- Functions with clear logic paths

### Known Limitations
- Complex algorithms (factorial, fibonacci) not fully supported
- Array/string operations require manual test oracles
- Functions with >2 parameters may not work correctly
- Expected output calculation is heuristic-based

### System Requirements
- Requires GCC/G++ compiler on system PATH
- gcov must be available for coverage collection
- Windows users need MinGW-w64 or equivalent
- Sufficient disk space for temporary compilation artifacts

## Project Structure

```
SWE/
├── SWE_API/                    # Backend FastAPI application
│   ├── main.py                 # Main API endpoints (F1-F6)
│   ├── models.py               # Pydantic data models
│   ├── cfg_parser.py           # CFG generation logic
│   ├── genetic_engine.py       # GA implementation
│   ├── fitness_evaluator.py    # Fitness calculation
│   ├── test_executor.py        # Test execution + gcov
│   ├── fault_localizer.py      # Tarantula algorithm
│   ├── reporter.py             # Report generation
│   ├── database.py             # In-memory data storage
│   └── requirements.txt        # Python dependencies
│
├── SWE_Frontend/               # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   └── WorkflowPage.jsx  # Main workflow component
│   │   ├── App.jsx             # Root component
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Tailwind styles
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   └── tailwind.config.js      # Tailwind configuration
│
└── README.md                   # This file
```

## Research Background

This system implements concepts from:
- **Search-Based Software Testing (SBST)**: Using meta-heuristic algorithms to generate test cases
- **Genetic Algorithms**: Evolutionary computation for test input optimization
- **Spectrum-Based Fault Localization (SBFL)**: Statistical fault localization using coverage data
- **Tarantula Algorithm**: Ranking program elements by suspiciousness scores

### Key References
- Jones, J. A., & Harrold, M. J. (2005). "Empirical evaluation of the Tarantula automatic fault-localization technique"
- McMinn, P. (2004). "Search-based software test data generation: a survey"
- Fraser, G., & Arcuri, A. (2011). "EvoSuite: automatic test suite generation for object-oriented software"

## Troubleshooting

### Backend Issues

**Problem**: `g++ not found`
```bash
# Windows: Add MinGW to PATH
set PATH=%PATH%;C:\msys64\mingw64\bin

# Verify installation
g++ --version
gcov --version
```

**Problem**: `LibClang failed`
- System automatically falls back to regex parser
- For better parsing, install LLVM and configure path in `cfg_parser.py`

**Problem**: `UnicodeEncodeError`
- System includes automatic Unicode sanitization
- Invisible characters (non-breaking spaces) are removed automatically

### Frontend Issues

**Problem**: CORS errors
- Ensure backend is running on port 8000
- Check `vite.config.js` proxy configuration

**Problem**: 404 errors on API calls
- Verify all endpoint paths match between frontend and backend
- Check browser console for actual request URLs

### Test Execution Issues

**Problem**: All tests show as passed (0 failures)
- Verify expected output calculation is correct
- Check if function is supported (2 parameters, simple operations)
- Review backend debug logs for actual vs expected outputs

**Problem**: 0% coverage
- Check if compilation succeeded (look for [ERROR] in backend logs)
- Verify gcov is installed and accessible
- Ensure source code is valid C/C++

## Contributing

Contributions are welcome! Please ensure:
1. Code follows existing style conventions
2. All endpoints maintain backward compatibility
3. Frontend components are responsive and accessible
4. Backend includes proper error handling
5. Documentation is updated for new features

## Future Enhancements

- Support for multi-parameter functions (3+ parameters)
- Custom test oracle input for complex algorithms
- Machine learning-based fault localization
- Support for more programming languages
- Parallel test execution
- Integration with CI/CD pipelines
- Advanced mutation operators
- Multi-objective fitness functions

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

Built using modern web technologies and established software engineering research principles. Special thanks to the open-source communities behind FastAPI, React, LibClang, and GCC/gcov.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Status**: Active Development

