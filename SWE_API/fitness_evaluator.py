"""
F3: Fitness Evaluation Module
Evaluates fitness of test cases based on branch coverage.
"""

from typing import List, Dict, Set
from models import (
    Chromosome, BranchCoverageResult, FitnessEvaluationOutput,
    CFGOutput, TestExecutionOutput
)
import uuid


class FitnessEvaluator:
    """
    Evaluates the fitness of test cases based on branch coverage.
    Higher fitness = more branches covered.
    """
    
    def __init__(self, cfg: CFGOutput):
        self.cfg = cfg
        self.all_branches: Set[str] = self._extract_all_branches()
        self.global_covered_branches: Set[str] = set()
    
    def _extract_all_branches(self) -> Set[str]:
        """Extract all possible branches from CFG"""
        branches = set()
        for edge in self.cfg.edges:
            branch_id = f"{edge.source_node_id}->{edge.target_node_id}"
            branches.add(branch_id)
        return branches
    
    def calculate_fitness(
        self, 
        test_case_id: str, 
        execution_result: TestExecutionOutput
    ) -> BranchCoverageResult:
        """
        Calculate fitness score based on branch coverage.
        
        Fitness formula:
        - Base score: (unique_branches_covered / total_branches)
        - Bonus: +0.2 if this test covers new branches not seen before
        - Penalty: -0.1 if test failed
        """
        covered_branches = set(execution_result.branches_taken)
        
        # Identify new branches covered by this test
        new_branches = covered_branches - self.global_covered_branches
        self.global_covered_branches.update(new_branches)
        
        # Calculate base coverage
        total_branches = len(self.all_branches) if self.all_branches else 1
        coverage_percentage = (len(covered_branches) / total_branches) * 100
        
        # Calculate fitness score
        fitness_score = len(covered_branches) / total_branches
        
        # Bonus for discovering new branches
        if new_branches:
            fitness_score += 0.2 * (len(new_branches) / total_branches)
        
        # Penalty for failed tests
        if execution_result.execution_status == "failed":
            fitness_score -= 0.1
        
        # Normalize to [0, 1]
        fitness_score = max(0.0, min(1.0, fitness_score))
        
        return BranchCoverageResult(
            test_case_id=test_case_id,
            branches_covered=list(covered_branches),
            total_branches=total_branches,
            coverage_percentage=round(coverage_percentage, 2),
            fitness_score=round(fitness_score, 4)
        )
    
    def evaluate_population(
        self,
        cfg_id: str,
        test_results: List[tuple[str, TestExecutionOutput]]
    ) -> FitnessEvaluationOutput:
        """
        Evaluate fitness for an entire population of test cases.
        
        Args:
            cfg_id: ID of the CFG being tested
            test_results: List of (test_case_id, execution_result) tuples
        
        Returns:
            FitnessEvaluationOutput with all evaluation results
        """
        results = []
        
        for test_case_id, execution_result in test_results:
            result = self.calculate_fitness(test_case_id, execution_result)
            results.append(result)
        
        # Calculate statistics
        fitness_scores = [r.fitness_score for r in results]
        best_fitness = max(fitness_scores) if fitness_scores else 0.0
        avg_fitness = sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0.0
        
        return FitnessEvaluationOutput(
            cfg_id=cfg_id,
            evaluated_count=len(results),
            results=results,
            best_fitness=round(best_fitness, 4),
            avg_fitness=round(avg_fitness, 4)
        )
    
    def update_chromosome_fitness(
        self,
        chromosome: Chromosome,
        fitness_result: BranchCoverageResult
    ) -> Chromosome:
        """Update a chromosome with its calculated fitness score"""
        chromosome.fitness_score = fitness_result.fitness_score
        return chromosome


def calculate_branch_distance(
    target_branch: str,
    execution_trace: List[str]
) -> float:
    """
    Calculate the "branch distance" - how close a test case came to 
    executing a target branch. Used for guiding the search.
    
    Returns: Distance metric (0 = branch executed, higher = further away)
    """
    if target_branch in execution_trace:
        return 0.0
    
    # Simple heuristic: count nodes away from target
    # In a real implementation, this would use control dependencies
    return 1.0

