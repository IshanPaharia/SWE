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

