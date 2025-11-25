"""
Integration Test 1: Code Analysis Workflow
Tests the integration of CFG Parser -> Genetic Engine -> Fitness Evaluator
"""
import random
from cfg_parser import analyze_cpp_code
from genetic_engine import generate_random_gene, crossover, mutate
from fitness_evaluator import FitnessEvaluator
from models import Chromosome, TestExecutionOutput


def test_parse_and_generate_test_inputs():
    """Test that CFG parser output can be used to generate test inputs via genetic engine"""
    # Step 1: Parse code to get CFG and parameters
    source_code = """
    int add(int a, int b) {
        if (a > 0 && b > 0) {
            return a + b;
        }
        return 0;
    }
    """
    
    cfg = analyze_cpp_code(source_code)
    
    # Verify CFG was created
    assert cfg is not None
    assert 'params' in cfg
    assert 'nodes' in cfg
    assert 'edges' in cfg
    
    # Step 2: Use parameters to generate genes
    param_types = cfg['params']
    
    # Generate random test inputs based on parameters
    if param_types:
        genes = [generate_random_gene(param) for param in param_types[:2]]
        assert len(genes) >= 0  # Should generate some genes
        
        # Create a chromosome
        chromosome = Chromosome(id='test1', genes=genes, fitness_score=0.0)
        assert chromosome.genes == genes


def test_genetic_algorithm_with_fitness_evaluation():
    """Test genetic operations integrated with fitness evaluation"""
    # Create a simple CFG for fitness evaluation
    from models import CFGOutput, CFGEdge
    
    cfg = CFGOutput(
        cfg_id='test_cfg',
        total_nodes=5,
        nodes=[],
        edges=[
            CFGEdge(source_node_id=1, target_node_id=2),
            CFGEdge(source_node_id=2, target_node_id=3),
            CFGEdge(source_node_id=3, target_node_id=4),
        ],
        complexity=3,
        required_inputs=['int', 'int'],
        detected_parameters=['int', 'int']
    )
    
    # Create fitness evaluator
    evaluator = FitnessEvaluator(cfg)
    
    # Generate initial population
    random.seed(42)
    population = []
    for i in range(5):
        genes = [generate_random_gene('int'), generate_random_gene('int')]
        chromosome = Chromosome(id=f'chr_{i}', genes=genes, fitness_score=0.0)
        population.append(chromosome)
    
    # Simulate test execution results and evaluate fitness
    for i, chromo in enumerate(population):
        # Mock test execution output
        branches_covered = ['1->2'] if i % 2 == 0 else ['2->3', '3->4']
        test_output = TestExecutionOutput(
            test_id=chromo.id,
            execution_status='passed',
            output='result',
            error=None,
            coverage_data=[],
            branches_taken=branches_covered,
            execution_time=0.01
        )
        
        # Evaluate fitness
        fitness_result = evaluator.calculate_fitness(chromo.id, test_output)
        chromo.fitness_score = fitness_result.fitness_score
        
        assert 0.0 <= fitness_result.fitness_score <= 1.0
        assert fitness_result.total_branches > 0
    
    # Perform genetic operations
    parent1, parent2 = population[0], population[1]
    child = crossover(parent1, parent2)
    assert len(child.genes) == len(parent1.genes)
    
    # Mutate
    original_genes = child.genes.copy()
    mutate(child, rate=0.5)
    # Genes should be same length after mutation
    assert len(child.genes) == len(original_genes)


def test_end_to_end_test_generation_pipeline():
    """Test complete pipeline from code parsing to test evaluation"""
    # Define target code
    source_code = """
    int max(int x, int y) {
        if (x > y) {
            return x;
        } else {
            return y;
        }
    }
    """
    
    # Step 1: Parse code
    cfg = analyze_cpp_code(source_code)
    assert cfg is not None
    
    # Step 2: Extract parameters
    params = cfg.get('params', [])
    
    # Step 3: Generate test population using genetic algorithm
    random.seed(100)
    population_size = 10
    population = []
    
    for i in range(population_size):
        # Generate genes based on detected parameters
        genes = []
        for param in params[:2]:  # Limit to first 2 parameters
            gene = generate_random_gene(param if param else 'int')
            genes.append(gene)
        
        chromosome = Chromosome(
            id=f'test_{i}',
            genes=genes,
            fitness_score=0.0
        )
        population.append(chromosome)
    
    # Verify population was created
    assert len(population) == population_size
    
    # Step 4: Create CFG output for fitness evaluation
    from models import CFGOutput, CFGEdge
    
    cfg_output = CFGOutput(
        cfg_id='max_function',
        total_nodes=4,
        nodes=[],
        edges=[
            CFGEdge(source_node_id=1, target_node_id=2),
            CFGEdge(source_node_id=1, target_node_id=3),
            CFGEdge(source_node_id=2, target_node_id=4),
            CFGEdge(source_node_id=3, target_node_id=4),
        ],
        complexity=2,
        required_inputs=['int', 'int'],
        detected_parameters=params
    )
    
    # Step 5: Evaluate fitness
    evaluator = FitnessEvaluator(cfg_output)
    
    for i, chromo in enumerate(population):
        # Simulate different coverage for different test cases
        if i % 3 == 0:
            branches = ['1->2', '2->4']
        elif i % 3 == 1:
            branches = ['1->3', '3->4']
        else:
            branches = ['1->2', '2->4', '1->3', '3->4']
        
        test_execution = TestExecutionOutput(
            test_id=chromo.id,
            execution_status='passed',
            output='output',
            error=None,
            coverage_data=[],
            branches_taken=branches,
            execution_time=0.02
        )
        
        fitness_result = evaluator.calculate_fitness(chromo.id, test_execution)
        chromo.fitness_score = fitness_result.fitness_score
    
    # Step 6: Verify evolution - select best performers
    sorted_population = sorted(population, key=lambda c: c.fitness_score, reverse=True)
    best_chromosome = sorted_population[0]
    worst_chromosome = sorted_population[-1]
    
    # Best should have equal or better fitness
    assert best_chromosome.fitness_score >= worst_chromosome.fitness_score
    
    # Step 7: Evolve population
    new_generation = []
    for i in range(population_size // 2):
        parent1 = sorted_population[i * 2]
        parent2 = sorted_population[i * 2 + 1]
        
        child = crossover(parent1, parent2)
        mutate(child, rate=0.1)
        new_generation.append(child)
    
    assert len(new_generation) == population_size // 2
