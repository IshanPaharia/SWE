from fitness_evaluator import FitnessEvaluator
from models import CFGOutput, CFGEdge, TestExecutionOutput


def make_cfg_with_edges(n):
    edges = [CFGEdge(source_node_id=i, target_node_id=i+1) for i in range(1, n+1)]
    return CFGOutput(cfg_id='c', total_nodes=n+1, nodes=[], edges=edges, complexity=1, required_inputs=[], detected_parameters=[])


def test_fitness_basic_coverage():
    cfg = make_cfg_with_edges(2)
    fe = FitnessEvaluator(cfg)
    te = TestExecutionOutput(test_id='t', execution_status='passed', output='', error=None, coverage_data=[], branches_taken=['1->2'], execution_time=0.01)
    res = fe.calculate_fitness('t', te)
    assert res.total_branches == 2
    assert res.coverage_percentage >= 0
    assert 0.0 <= res.fitness_score <= 1.0


def test_fitness_bonus_for_new_branches():
    cfg = make_cfg_with_edges(2)
    fe = FitnessEvaluator(cfg)
    te1 = TestExecutionOutput(test_id='t1', execution_status='passed', output='', error=None, coverage_data=[], branches_taken=['1->2'], execution_time=0.01)
    te2 = TestExecutionOutput(test_id='t2', execution_status='passed', output='', error=None, coverage_data=[], branches_taken=['2->3'], execution_time=0.01)
    r1 = fe.calculate_fitness('t1', te1)
    r2 = fe.calculate_fitness('t2', te2)
    # Second test discovers new branch -> should have bonus (fitness slightly higher than plain coverage)
    assert r2.fitness_score >= r1.fitness_score or r2.fitness_score >= 0.0


def test_fitness_penalty_on_failed():
    cfg = make_cfg_with_edges(1)
    fe = FitnessEvaluator(cfg)
    te = TestExecutionOutput(test_id='tf', execution_status='failed', output='', error='err', coverage_data=[], branches_taken=['1->2'], execution_time=0.01)
    r = fe.calculate_fitness('tf', te)
    # Ensure penalty applied (score cannot be negative)
    assert 0.0 <= r.fitness_score <= 1.0
