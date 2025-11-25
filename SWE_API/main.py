from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import random
import os

from models import (
    SourceCodeInput, CFGOutput, CFGNode, CFGEdge, 
    GAConfigInput, EvolveInput, PopulationOutput, Chromosome,
    FitnessEvaluationInput, FitnessEvaluationOutput, BranchCoverageResult,
    TestExecutionInput, TestExecutionOutput,
    FaultLocalizationInput, FaultLocalizationOutput, TestResult,
    ReportRequest, ReportOutput
)
from database import (
    stored_cfgs, active_populations, fitness_evaluations,
    test_executions, fault_analyses, generated_reports
)
from cfg_parser import analyze_cpp_code
import genetic_engine as engine
from fitness_evaluator import FitnessEvaluator
from test_executor import TestExecutor, execute_test_case
from fault_localizer import TarantulaLocalizer, analyze_from_executions
from reporter import FaultLocalizationReporter, generate_quick_report

app = FastAPI(title="Automated Test Case Generator")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- F1 ENDPOINT: PARSE CODE ---
@app.post("/analysis/generate-cfg", response_model=CFGOutput, status_code=status.HTTP_201_CREATED, tags=["F1"])
async def generate_cfg(data: SourceCodeInput):
    if not data.source_code.strip():
        raise HTTPException(status_code=400, detail="Source code empty")

    try:
        # 1. Run Logic (cfg_parser.py)
        result = analyze_cpp_code(data.source_code)
        
        # 2. Map Logic result to API Models
        final_nodes = [CFGNode(**n) for n in result["nodes"]]
        final_edges = [CFGEdge(**e) for e in result["edges"]]
        
        # Calculate Complexity (Count decision points)
        decision_points = ["If", "Loop", "Switch"]
        complexity = len([n for n in final_nodes if any(d in n.code_snippet for d in decision_points)]) + 1

        output = CFGOutput(
            cfg_id=str(uuid.uuid4()),
            total_nodes=len(final_nodes),
            nodes=final_nodes,
            edges=final_edges,
            complexity=complexity,
            required_inputs=result["params"],  # This is sent to F2
            detected_parameters=result["params"]  # For frontend display
        )
        
        # 3. Save to DB
        stored_cfgs[output.cfg_id] = output
        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- F2 ENDPOINT: INITIALIZE POPULATION ---
@app.post("/ga/initialize", response_model=PopulationOutput, status_code=status.HTTP_201_CREATED, tags=["F2"])
async def initialize_population(config: GAConfigInput):
    if config.cfg_id not in stored_cfgs:
        raise HTTPException(status_code=404, detail=f"CFG not found. Please generate a CFG first using /analysis/generate-cfg")
    
    try:
        # 1. Get the required inputs detected by F1
        cfg_data = stored_cfgs[config.cfg_id]
        required_params = cfg_data.required_inputs # e.g. ['int', 'int']
        
        # Handle case where no parameters are detected
        if not required_params:
            required_params = ['int']  # Default to at least one int parameter

        # 2. Create Random Population (genetic_engine.py)
        individuals = []
        for _ in range(config.population_size):
            genes = [engine.generate_random_gene(p_type) for p_type in required_params]
            chr_id = str(uuid.uuid4())[:8]
            individuals.append(Chromosome(
                id=chr_id,
                genes=genes,
                chromosome_id=chr_id,  # Frontend alias
                fitness=0.0  # Frontend alias
            ))

        output = PopulationOutput(
            generation_id=0,
            status="Initialized",
            population_count=len(individuals),
            individuals=individuals,
            # Frontend compatibility fields
            generation=0,
            population=individuals,
            best_individuals=individuals[:10],
            best_fitness=0.0,
            average_fitness=0.0,
            population_id=config.cfg_id
        )
        
        active_populations[config.cfg_id] = output
        return output
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Population initialization failed: {str(e)}")


# --- F2 ENDPOINT: EVOLVE POPULATION ---
@app.post("/ga/evolve", response_model=PopulationOutput, tags=["F2"])
async def evolve_population(data: EvolveInput):
    if data.cfg_id not in active_populations:
        raise HTTPException(status_code=404, detail="Population not found")
    
    current_output = active_populations[data.cfg_id]
    population = current_output.individuals

    # 1. Evaluate Fitness
    for ind in population:
        ind.fitness_score = engine.calculate_fitness_mock(ind)
        ind.fitness = ind.fitness_score  # Frontend alias
    
    # Sort by best fitness
    population.sort(key=lambda x: x.fitness_score, reverse=True)

    # 2. Create Next Generation
    next_gen = []
    # Elitism: Keep top 2
    next_gen.extend(population[:2])

    while len(next_gen) < len(population):
        p1 = engine.tournament_selection(population)
        p2 = engine.tournament_selection(population)
        
        if random.random() < data.crossover_rate:
            child = engine.crossover(p1, p2)
        else:
            child = p1
            new_id = str(uuid.uuid4())[:8]
            child.id = new_id
            child.chromosome_id = new_id  # Frontend alias
        
        engine.mutate(child, data.mutation_rate)
        child.fitness = child.fitness_score  # Frontend alias
        next_gen.append(child)

    new_gen_id = current_output.generation_id + 1
    
    # Calculate fitness statistics
    fitness_scores = [ind.fitness_score for ind in next_gen if ind.fitness_score is not None]
    best_fit = max(fitness_scores) if fitness_scores else 0.0
    avg_fit = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0.0
    
    # Sort by fitness and get top individuals
    sorted_pop = sorted(next_gen, key=lambda x: x.fitness_score or 0, reverse=True)
    
    output = PopulationOutput(
        generation_id=new_gen_id,
        status=f"Evolved Gen {new_gen_id}",
        population_count=len(next_gen),
        individuals=next_gen,
        # Frontend compatibility fields
        generation=new_gen_id,
        population=next_gen,
        best_individuals=sorted_pop[:10],
        best_fitness=best_fit,
        average_fitness=avg_fit,
        population_id=data.cfg_id
    )

    active_populations[data.cfg_id] = output
    return output


# --- F3 ENDPOINT: EVALUATE FITNESS ---
@app.post("/fitness/evaluate", response_model=FitnessEvaluationOutput, tags=["F3"])
async def evaluate_fitness(data: FitnessEvaluationInput):
    """
    Evaluate fitness of a single test case based on branch coverage.
    Requires: CFG from F1, compiled source code, test inputs.
    """
    if data.cfg_id not in stored_cfgs:
        raise HTTPException(status_code=404, detail="CFG not found")
    
    cfg_data = stored_cfgs[data.cfg_id]
    
    try:
        # Execute test case with source code
        execution_result = execute_test_case(
            source_code=data.source_code,
            test_inputs=data.test_case.genes
        )
        
        # Calculate branch coverage
        total_branches = cfg_data.total_nodes
        branches_covered = execution_result.branches_taken
        coverage = len(branches_covered) / total_branches if total_branches > 0 else 0.0
        
        # Return simplified output for frontend
        test_id = data.test_case.chromosome_id or str(uuid.uuid4())[:8]
        return {
            "cfg_id": data.cfg_id,
            "evaluated_count": 1,
            "results": [],
            "best_fitness": coverage,
            "avg_fitness": coverage,
            # Frontend fields
            "test_case_id": test_id,
            "branch_coverage": coverage,
            "branches_covered": branches_covered
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fitness evaluation failed: {str(e)}")


@app.post("/fitness/evaluate-population", response_model=FitnessEvaluationOutput, tags=["F3"])
async def evaluate_population_fitness(cfg_id: str, source_code: str):
    """
    Evaluate fitness for entire population of test cases.
    This connects F2 (population) with F3 (fitness evaluation) and F4 (test execution).
    """
    if cfg_id not in stored_cfgs:
        raise HTTPException(status_code=404, detail="CFG not found")
    
    if cfg_id not in active_populations:
        raise HTTPException(status_code=404, detail="Population not found. Initialize population first (F2).")
    
    cfg_data = stored_cfgs[cfg_id]
    population = active_populations[cfg_id].individuals
    
    try:
        # Execute all test cases and collect results
        test_results = []
        for individual in population:
            execution_result = execute_test_case(
                source_code=source_code,
                test_inputs=individual.genes
            )
            test_results.append((individual.id, execution_result))
        
        # Evaluate fitness for entire population
        evaluator = FitnessEvaluator(cfg_data)
        output = evaluator.evaluate_population(cfg_id, test_results)
        
        # Update chromosomes with fitness scores
        for individual, result in zip(population, output.results):
            individual.fitness_score = result.fitness_score
        
        # Store results
        fitness_evaluations[cfg_id] = output.results
        
        return output
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Population fitness evaluation failed: {str(e)}")


# --- F4 ENDPOINT: EXECUTE TESTS WITH GCOV ---
@app.post("/test/execute", response_model=TestExecutionOutput, tags=["F4"])
async def execute_test(data: TestExecutionInput):
    """
    Compile source code with coverage instrumentation and execute test.
    Uses GCC with --coverage flag and gcov for coverage data collection.
    """
    try:
        # Execute test with coverage collection
        result = execute_test_case(
            source_code=data.source_code,
            test_inputs=data.test_inputs,
            expected_output=data.expected_output
        )
        
        # Store execution result
        test_executions[result.test_id] = result
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")


@app.post("/test/execute-batch", response_model=list[TestExecutionOutput], tags=["F4"])
async def execute_test_batch(source_code: str, test_cases: list[list]):
    """
    Execute multiple test cases on the same source code.
    More efficient than individual executions.
    """
    try:
        results = []
        for test_inputs in test_cases:
            result = execute_test_case(
                source_code=source_code,
                test_inputs=test_inputs
            )
            test_executions[result.test_id] = result
            results.append(result)
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch test execution failed: {str(e)}")


# --- F5 ENDPOINT: FAULT LOCALIZATION (TARANTULA) ---
@app.post("/fault-localization/analyze", response_model=FaultLocalizationOutput, tags=["F5"])
async def analyze_faults(data: FaultLocalizationInput):
    """
    Apply Tarantula algorithm for spectrum-based fault localization.
    Identifies suspicious code lines based on test pass/fail patterns.
    """
    try:
        # Use empty source lines for now (just analyze coverage patterns)
        source_lines = {}
        for test_result in data.test_results:
            for line_num in test_result.covered_lines:
                if line_num not in source_lines:
                    source_lines[line_num] = f"<line {line_num}>"
        
        # Perform Tarantula analysis
        localizer = TarantulaLocalizer()
        analysis = localizer.analyze(
            source_file=data.source_filename,
            test_results=data.test_results,
            source_lines=source_lines
        )
        
        # Add frontend compatibility fields to suspicious lines
        for line in analysis.suspicious_lines:
            line.failed_count = line.failed_coverage
            line.passed_count = line.passed_coverage
        
        # Store analysis result
        fault_analyses[analysis.analysis_id] = analysis
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fault localization failed: {str(e)}")


@app.post("/fault-localization/analyze-from-executions", response_model=FaultLocalizationOutput, tags=["F5"])
async def analyze_faults_from_executions(source_file: str, source_code: str, test_ids: list[str]):
    """
    Convenience endpoint: Perform fault localization from stored test execution results.
    """
    try:
        # Retrieve test execution results
        executions = []
        for test_id in test_ids:
            if test_id in test_executions:
                executions.append((test_id, test_executions[test_id]))
        
        if not executions:
            raise HTTPException(status_code=404, detail="No test execution results found for provided test IDs")
        
        # Perform analysis
        analysis = analyze_from_executions(source_file, source_code, executions)
        
        # Store analysis result
        fault_analyses[analysis.analysis_id] = analysis
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fault localization from executions failed: {str(e)}")


# --- F6 ENDPOINT: GENERATE REPORTS ---
@app.post("/report/generate", response_model=ReportOutput, tags=["F6"])
async def generate_report(data: ReportRequest):
    """
    Generate a comprehensive fault localization report.
    Ranks suspicious code lines and provides actionable recommendations.
    """
    if data.analysis_id not in fault_analyses:
        raise HTTPException(status_code=404, detail="Fault analysis not found. Run F5 first.")
    
    try:
        analysis = fault_analyses[data.analysis_id]
        
        # Generate report
        report = generate_quick_report(analysis, data.top_n)
        
        # Store report
        generated_reports[report.report_id] = report
        
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/report/{report_id}/text", response_class=PlainTextResponse, tags=["F6"])
async def get_report_text(report_id: str):
    """
    Get report in human-readable text format.
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = generated_reports[report_id]
    reporter = FaultLocalizationReporter()
    
    return reporter.format_text_report(report)


@app.get("/report/{report_id}/json", tags=["F6"])
async def get_report_json(report_id: str):
    """
    Get report in JSON format.
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = generated_reports[report_id]
    return report


# --- UTILITY ENDPOINTS ---
@app.get("/status", tags=["Utility"])
async def get_status():
    """
    Get system status and statistics.
    """
    return {
        "status": "running",
        "cfgs_stored": len(stored_cfgs),
        "active_populations": len(active_populations),
        "fitness_evaluations": len(fitness_evaluations),
        "test_executions": len(test_executions),
        "fault_analyses": len(fault_analyses),
        "generated_reports": len(generated_reports)
    }


@app.delete("/clear", tags=["Utility"])
async def clear_all_data():
    """
    Clear all stored data (useful for testing).
    """
    stored_cfgs.clear()
    active_populations.clear()
    fitness_evaluations.clear()
    test_executions.clear()
    fault_analyses.clear()
    generated_reports.clear()
    
    return {"message": "All data cleared successfully"}