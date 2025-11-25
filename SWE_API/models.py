from pydantic import BaseModel, Field
from typing import List, Optional, Any

# --- F1 MODELS (Code Analysis) ---
class SourceCodeInput(BaseModel):
    filename: str = Field(..., json_schema_extra={"example": "test.cpp"})
    source_code: str = Field(..., json_schema_extra={"example": "int main() { return 0; }"})

class CFGNode(BaseModel):
    node_id: int
    code_snippet: str
    is_entry: bool = False
    is_exit: bool = False

class CFGEdge(BaseModel):
    source_node_id: int
    target_node_id: int
    label: Optional[str] = None

class CFGOutput(BaseModel):
    cfg_id: str
    total_nodes: int
    nodes: List[CFGNode]
    edges: List[CFGEdge]
    complexity: int
    required_inputs: List[str]
    detected_parameters: List[str]  # Alias for frontend 

# --- F2 MODELS (Genetic Algorithm) ---
class GAConfigInput(BaseModel):
    cfg_id: str
    population_size: int = Field(20, ge=5, le=1000, description="Population size (minimum 5)")

class EvolveInput(BaseModel):
    cfg_id: str
    mutation_rate: float = 0.3  # Increased for better edge case detection
    crossover_rate: float = 0.8

# RENAMED: 'TestCaseChromosome' -> 'Chromosome' to stop Pytest confusion
class Chromosome(BaseModel):
    id: str
    genes: List[Any]
    fitness_score: float = 0.0
    # Frontend compatibility
    chromosome_id: Optional[str] = None  # Alias for id
    fitness: Optional[float] = None  # Alias for fitness_score

class PopulationOutput(BaseModel):
    generation_id: int
    status: str
    population_count: int
    individuals: List[Chromosome]
    # Aliases for frontend compatibility
    generation: Optional[int] = None  # Same as generation_id
    population: Optional[List[Chromosome]] = None  # Same as individuals
    best_individuals: Optional[List[Chromosome]] = None  # Top individuals
    best_fitness: Optional[float] = None
    average_fitness: Optional[float] = None
    population_id: Optional[str] = None  # For tracking

# --- F3 MODELS (Fitness Evaluation) ---
class TestCaseInput(BaseModel):
    chromosome_id: Optional[str] = None
    genes: List[Any]
    fitness: Optional[float] = 0.0

class FitnessEvaluationInput(BaseModel):
    test_case: TestCaseInput
    source_code: str
    cfg_id: str

class BranchCoverageResult(BaseModel):
    test_case_id: str
    branches_covered: List[str]  # List of branch identifiers
    total_branches: int
    coverage_percentage: float
    fitness_score: float
    # Frontend compatibility
    branch_coverage: Optional[float] = None  # Coverage as decimal (0.0-1.0)

class FitnessEvaluationOutput(BaseModel):
    cfg_id: str
    evaluated_count: int
    results: List[BranchCoverageResult]
    best_fitness: float
    avg_fitness: float
    # Frontend compatibility - single test case result
    test_case_id: Optional[str] = None
    branch_coverage: Optional[float] = None
    branches_covered: Optional[List[str]] = None

# --- F4 MODELS (Test Execution) ---
class TestExecutionInput(BaseModel):
    source_filename: str  # Frontend sends source_filename
    source_code: str
    test_inputs: List[Any]
    expected_output: Optional[Any] = None

class GCovData(BaseModel):
    file_name: str
    line_number: int
    execution_count: int
    source_line: str

class TestExecutionOutput(BaseModel):
    test_id: str
    execution_status: str  # "passed", "failed", "error"
    output: Optional[str] = None
    error: Optional[str] = None
    coverage_data: List[GCovData]
    branches_taken: List[str]
    execution_time: float

# --- F5 MODELS (Fault Localization) ---
class TestResult(BaseModel):
    test_id: str
    status: str  # "passed" or "failed"
    covered_lines: List[int]

class FaultLocalizationInput(BaseModel):
    source_filename: str  # Frontend sends source_filename
    test_results: List[TestResult]

class SuspiciousLine(BaseModel):
    file_name: str
    line_number: int
    line_content: str
    suspiciousness_score: float
    failed_coverage: int  # Number of failed tests covering this line
    passed_coverage: int  # Number of passed tests covering this line
    # Frontend compatibility
    failed_count: Optional[int] = None  # Alias for failed_coverage
    passed_count: Optional[int] = None  # Alias for passed_coverage

class FaultLocalizationOutput(BaseModel):
    analysis_id: str
    source_file: str
    total_tests: int
    failed_tests: int
    passed_tests: int
    suspicious_lines: List[SuspiciousLine]

# --- F6 MODELS (Reporting) ---
class ReportRequest(BaseModel):
    analysis_id: str
    top_n: int = Field(10, ge=1, le=100, description="Number of top suspicious lines to report")
    include_recommendations: Optional[bool] = True

class ReportOutput(BaseModel):
    report_id: str
    generated_at: str
    analysis_id: str
    summary: str
    top_suspicious_lines: List[SuspiciousLine]
    recommendations: Optional[List[str]] = []