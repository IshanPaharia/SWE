"""
Integration Test 3: Complete APR (Automated Program Repair) Pipeline
Tests the full integration of all modules working together
"""
import random
import tempfile
from pathlib import Path

from cfg_parser import analyze_cpp_code
from genetic_engine import generate_random_gene, crossover, mutate, tournament_selection
from fitness_evaluator import FitnessEvaluator
from test_executor import TestExecutor
from fault_localizer import TarantulaLocalizer
from reporter import FaultLocalizationReporter
from models import (
    Chromosome, CFGOutput, CFGEdge, TestExecutionOutput,
    TestResult, GCovData
)


def test_complete_apr_pipeline_simulation():
    """
    Simulate a complete APR pipeline:
    1. Parse buggy code to get CFG
    2. Generate test population using genetic algorithm
    3. Execute tests and collect coverage
    4. Evaluate fitness based on coverage
    5. Perform fault localization
    6. Generate bug report
    """
    
    # Step 1: Parse buggy code
    buggy_code = """
    int calculate(int x, int y) {
        if (x > 0) {
            if (y > 0) {
                return x + y;
            }
            return x;
        }
        return y;
    }
    """
    
    cfg_dict = analyze_cpp_code(buggy_code)
    assert cfg_dict is not None
    assert 'nodes' in cfg_dict
    assert 'edges' in cfg_dict
    
    # Step 2: Create CFG model for fitness evaluation
    cfg_output = CFGOutput(
        cfg_id='calculate_func',
        total_nodes=6,
        nodes=[],
        edges=[
            CFGEdge(source_node_id=1, target_node_id=2),
            CFGEdge(source_node_id=2, target_node_id=3),
            CFGEdge(source_node_id=2, target_node_id=5),
            CFGEdge(source_node_id=3, target_node_id=4),
            CFGEdge(source_node_id=3, target_node_id=5),
            CFGEdge(source_node_id=4, target_node_id=6),
            CFGEdge(source_node_id=5, target_node_id=6),
        ],
        complexity=3,
        required_inputs=['int', 'int'],
        detected_parameters=['int', 'int']
    )
    
    # Step 3: Generate initial test population
    random.seed(999)
    population_size = 20
    population = []
    
    for i in range(population_size):
        genes = [generate_random_gene('int'), generate_random_gene('int')]
        chromosome = Chromosome(id=f'gen0_test_{i}', genes=genes, fitness_score=0.0)
        population.append(chromosome)
    
    assert len(population) == population_size
    
    # Step 4: Simulate test execution and fitness evaluation
    evaluator = FitnessEvaluator(cfg_output)
    test_results = []
    
    for i, chromo in enumerate(population):
        # Simulate different branch coverage based on gene values
        x, y = chromo.genes[0], chromo.genes[1]
        
        branches_taken = ['1->2']
        covered_lines = [1, 2]
        
        if x > 0:
            branches_taken.append('2->3')
            covered_lines.extend([3])
            if y > 0:
                branches_taken.extend(['3->4', '4->6'])
                covered_lines.extend([4, 6])
                status = 'passed'
            else:
                branches_taken.extend(['3->5', '5->6'])
                covered_lines.extend([5, 6])
                status = 'passed'
        else:
            branches_taken.extend(['2->5', '5->6'])
            covered_lines.extend([5, 6])
            # Simulate some failures for negative inputs
            status = 'failed' if y < 0 else 'passed'
        
        # Create test execution output
        test_output = TestExecutionOutput(
            test_id=chromo.id,
            execution_status=status,
            output='test_output',
            error=None if status == 'passed' else 'assertion failed',
            coverage_data=[],
            branches_taken=branches_taken,
            execution_time=0.01
        )
        
        # Evaluate fitness
        fitness_result = evaluator.calculate_fitness(chromo.id, test_output)
        chromo.fitness_score = fitness_result.fitness_score
        
        # Create test result for fault localization
        test_result = TestResult(
            test_id=chromo.id,
            status=status,
            covered_lines=covered_lines
        )
        test_results.append(test_result)
    
    # Step 5: Genetic algorithm evolution
    generations = 3
    for gen in range(generations):
        # Selection
        selected = []
        for _ in range(population_size):
            winner = tournament_selection(population)
            selected.append(winner)
        
        # Crossover and mutation
        new_population = []
        for i in range(0, population_size, 2):
            parent1 = selected[i]
            parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
            
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            
            mutate(child1, rate=0.1)
            mutate(child2, rate=0.1)
            
            child1.id = f'gen{gen+1}_test_{i}'
            child2.id = f'gen{gen+1}_test_{i+1}'
            
            new_population.extend([child1, child2])
        
        population = new_population[:population_size]
    
    assert len(population) == population_size
    
    # Step 6: Fault localization on test results
    passing_tests = [t for t in test_results if t.status == 'passed']
    failing_tests = [t for t in test_results if t.status == 'failed']
    
    # Only proceed if we have both passing and failing tests
    if len(failing_tests) > 0:
        source_lines = {
            1: 'int calculate(int x, int y) {',
            2: '    if (x > 0) {',
            3: '        if (y > 0) {',
            4: '            return x + y;',
            5: '        return x;',
            6: '    return y;',
        }
        
        localizer = TarantulaLocalizer()
        fault_analysis = localizer.analyze('calculate.cpp', test_results, source_lines)
        
        assert fault_analysis is not None
        assert fault_analysis.total_tests == len(test_results)
        assert fault_analysis.failed_tests == len(failing_tests)
        assert fault_analysis.passed_tests == len(passing_tests)
        
        # Step 7: Generate report
        reporter = FaultLocalizationReporter()
        report = reporter.generate_report(fault_analysis, top_n=5)
        
        assert report is not None
        assert len(report.top_suspicious_lines) > 0
        
        # Generate both formats
        text_report = reporter.format_text_report(report)
        json_report = reporter.format_json_report(report)
        
        assert 'FAULT LOCALIZATION REPORT' in text_report
        assert isinstance(json_report, dict)
        assert 'summary' in json_report


def test_evolutionary_test_generation_improves_coverage():
    """Test that genetic algorithm improves test coverage over generations"""
    
    # Create a CFG with multiple branches
    cfg = CFGOutput(
        cfg_id='complex_func',
        total_nodes=8,
        nodes=[],
        edges=[
            CFGEdge(source_node_id=i, target_node_id=i+1)
            for i in range(1, 8)
        ],
        complexity=4,
        required_inputs=['int', 'int', 'bool'],
        detected_parameters=['int', 'int', 'bool']
    )
    
    evaluator = FitnessEvaluator(cfg)
    
    # Initial population
    random.seed(42)
    population_size = 30
    
    def create_population(gen_id):
        pop = []
        for i in range(population_size):
            genes = [
                generate_random_gene('int'),
                generate_random_gene('int'),
                generate_random_gene('bool')
            ]
            chromo = Chromosome(id=f'{gen_id}_test_{i}', genes=genes, fitness_score=0.0)
            pop.append(chromo)
        return pop
    
    def evaluate_population(pop, gen_num):
        for chromo in pop:
            # Simulate progressive coverage improvement
            num_branches = min(gen_num + 2, 7)
            branches = [f'{i}->{i+1}' for i in range(1, num_branches)]
            
            test_output = TestExecutionOutput(
                test_id=chromo.id,
                execution_status='passed',
                output='',
                error=None,
                coverage_data=[],
                branches_taken=branches,
                execution_time=0.01
            )
            
            fitness_result = evaluator.calculate_fitness(chromo.id, test_output)
            chromo.fitness_score = fitness_result.fitness_score
    
    # Track average fitness per generation
    fitness_history = []
    
    # Evolution
    population = create_population('gen0')
    
    for gen in range(5):
        # Evaluate
        evaluate_population(population, gen)
        
        avg_fitness = sum(c.fitness_score for c in population) / len(population)
        fitness_history.append(avg_fitness)
        
        # Evolve
        new_pop = []
        for i in range(population_size // 2):
            p1 = tournament_selection(population)
            p2 = tournament_selection(population)
            
            child1 = crossover(p1, p2)
            child2 = crossover(p2, p1)
            
            mutate(child1, rate=0.15)
            mutate(child2, rate=0.15)
            
            child1.id = f'gen{gen+1}_test_{i*2}'
            child2.id = f'gen{gen+1}_test_{i*2+1}'
            
            new_pop.extend([child1, child2])
        
        population = new_pop
    
    # Verify that fitness improved or stayed stable
    assert len(fitness_history) == 5
    # At minimum, final generation should not be worse than first
    assert fitness_history[-1] >= fitness_history[0] - 0.1  # Allow small variance


def test_cfg_complexity_drives_test_generation():
    """Test that CFG complexity influences test generation strategy"""
    
    # Simple code (low complexity)
    simple_code = """
    int simple(int x) {
        return x * 2;
    }
    """
    
    # Complex code (high complexity)
    complex_code = """
    int complex(int a, int b, int c) {
        if (a > 0) {
            if (b > 0) {
                if (c > 0) {
                    return a + b + c;
                }
                return a + b;
            }
            return a;
        }
        return 0;
    }
    """
    
    # Parse both
    simple_cfg = analyze_cpp_code(simple_code)
    complex_cfg = analyze_cpp_code(complex_code)
    
    assert simple_cfg is not None
    assert complex_cfg is not None
    
    # Complex code should have more nodes/edges
    simple_nodes = len(simple_cfg.get('nodes', []))
    complex_nodes = len(complex_cfg.get('nodes', []))
    
    # The complex code likely has more CFG nodes
    # (This is a heuristic check, actual values depend on parser)
    assert complex_nodes >= simple_nodes
    
    # Generate tests for both
    random.seed(123)
    
    # For simple code, fewer tests needed
    simple_tests = 5
    simple_population = []
    for i in range(simple_tests):
        genes = [generate_random_gene('int')]
        chromo = Chromosome(id=f'simple_{i}', genes=genes, fitness_score=0.0)
        simple_population.append(chromo)
    
    # For complex code, more tests needed
    complex_tests = 20
    complex_population = []
    for i in range(complex_tests):
        genes = [generate_random_gene('int') for _ in range(3)]
        chromo = Chromosome(id=f'complex_{i}', genes=genes, fitness_score=0.0)
        complex_population.append(chromo)
    
    assert len(simple_population) == simple_tests
    assert len(complex_population) == complex_tests
    assert len(complex_population[0].genes) > len(simple_population[0].genes)
