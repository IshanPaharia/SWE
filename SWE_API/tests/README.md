# Test Suite Documentation

This directory contains comprehensive test coverage for the SWE_API project, organized into unit tests and integration tests.

## Directory Structure

```
tests/
├── conftest.py                    # Pytest configuration and hooks
├── unit/                          # Unit tests (isolated module testing)
│   ├── test_f1_cfg_parser.py     # CFG parser unit tests
│   ├── test_f2_genetic_engine.py # Genetic algorithm unit tests
│   ├── test_f3_fitness_evaluator.py # Fitness evaluation unit tests
│   ├── test_f4_test_executor.py  # Test execution unit tests
│   ├── test_f5_fault_localizer.py # Fault localization unit tests
│   └── test_f6_reporter.py       # Report generation unit tests
└── integration/                   # Integration tests (multi-module workflows)
    ├── test_i1_code_analysis_workflow.py    # CFG → Genetic → Fitness pipeline
    ├── test_i2_execution_fault_workflow.py  # Execution → Fault → Report pipeline
    └── test_i3_complete_apr_pipeline.py     # Complete APR workflow

```

## Test Categories

### Unit Tests (19 tests)

Unit tests verify individual modules in isolation. Each module has 3-4 focused tests:

**F1: CFG Parser** (`test_f1_cfg_parser.py`)
- Function and control flow detection
- Parameter extraction
- Edge case handling

**F2: Genetic Engine** (`test_f2_genetic_engine.py`)
- Random gene generation
- Crossover operations
- Mutation operations
- Tournament selection

**F3: Fitness Evaluator** (`test_f3_fitness_evaluator.py`)
- Basic coverage calculation
- Branch discovery bonus
- Failure penalties

**F4: Test Executor** (`test_f4_test_executor.py`)
- GCov file parsing
- Branch extraction
- Coverage data collection

**F5: Fault Localizer** (`test_f5_fault_localizer.py`)
- Tarantula algorithm
- Suspiciousness scoring (Ochiai, Jaccard)
- Edge case handling

**F6: Reporter** (`test_f6_reporter.py`)
- Report generation
- Text formatting
- JSON serialization

### Integration Tests (11 tests)

Integration tests verify that modules work correctly together in realistic workflows:

**I1: Code Analysis Workflow** (`test_i1_code_analysis_workflow.py`)
- CFG Parser → Genetic Engine integration
- Genetic Engine → Fitness Evaluator integration
- End-to-end test generation pipeline

**I2: Execution & Fault Detection Workflow** (`test_i2_execution_fault_workflow.py`)
- Test execution with coverage collection
- Fault localization from test results
- Complete bug detection workflow with reports
- Coverage data flow through pipeline

**I3: Complete APR Pipeline** (`test_i3_complete_apr_pipeline.py`)
- Full automated program repair simulation
- Evolutionary test generation with coverage improvement
- CFG complexity-driven test generation

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run only unit tests
```bash
pytest tests/unit/ -v
```

### Run only integration tests
```bash
pytest tests/integration/ -v
```

### Run specific test file
```bash
pytest tests/unit/test_f1_cfg_parser.py -v
```

### Run with coverage report
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run with warnings displayed
```bash
pytest tests/ -v -W default
```

## Test Design Principles

1. **Isolation**: Unit tests test one module at a time with minimal dependencies
2. **Integration**: Integration tests verify real-world workflows across modules
3. **Clarity**: Test names clearly describe what is being tested
4. **Independence**: Tests can run in any order without affecting each other
5. **Determinism**: Random seeds are set where needed for reproducible results

## Configuration

- **conftest.py**: Contains pytest hooks for test reporting and path configuration
- **Fixtures**: Use `tmp_path` fixture for temporary file operations
- **Imports**: All imports are relative to project root (configured in conftest.py)

## Expected Results

- **Total Tests**: 30
- **Unit Tests**: 19
- **Integration Tests**: 11
- **Expected Status**: All passing
- **Warnings**: None (path manipulation warnings resolved)

## Maintenance

When adding new features:

1. **Add unit tests** to `tests/unit/` for new modules or functions
2. **Add integration tests** to `tests/integration/` for new workflows
3. **Follow naming convention**: 
   - Unit: `test_f{N}_{module_name}.py`
   - Integration: `test_i{N}_{workflow_description}.py`
4. **Update this README** with new test descriptions

## Troubleshooting

### Import errors
- Ensure you're running tests from the project root directory
- Check that `conftest.py` is properly configuring the Python path

### Test failures
- Run with `-v` flag for verbose output
- Run with `-s` flag to see print statements
- Run with `--tb=short` for concise tracebacks

### Slow tests
- Integration tests involving compilation may take longer
- Use `-k` flag to run specific tests during development
