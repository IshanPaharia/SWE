import random
import uuid
from typing import List
from models import Chromosome

def generate_random_gene(param_type: str):
    """
    Generates a random gene based on the expected C++ type.
    """
    if "int" in param_type:
        return random.randint(-100, 100)
    elif "float" in param_type or "double" in param_type:
        return round(random.uniform(-100.0, 100.0), 2)
    elif "bool" in param_type:
        return random.choice([0, 1])
    return 0 

def calculate_fitness_mock(chromosome: Chromosome) -> float:
    """
    MOCK Fitness: Returns a random score.
    TODO: Replace with real 'gcov' coverage analysis later.
    """
    return round(random.uniform(0.1, 0.9), 2)

def tournament_selection(population: List[Chromosome]) -> Chromosome:
    """
    Selects the best individual from a random subgroup (Tournament Size = 3).
    """
    k = 3
    competitors = random.sample(population, k=min(k, len(population)))
    return max(competitors, key=lambda c: c.fitness_score)

def crossover(p1: Chromosome, p2: Chromosome) -> Chromosome:
    """
    Single-Point Crossover: Combines half of P1 with half of P2.
    """
    if len(p1.genes) < 2:
        return p1 # Cannot crossover a single gene, just return parent
    
    point = random.randint(1, len(p1.genes) - 1)
    new_genes = p1.genes[:point] + p2.genes[point:]
    
    return Chromosome(
        id=str(uuid.uuid4())[:8],
        genes=new_genes,
        fitness_score=0.0
    )

def mutate(chromosome: Chromosome, rate: float):
    """
    Enhanced mutation to find faulty test cases.
    Includes: standard mutations, boundary values, equal values, and aggressive exploration.
    """
    # SPECIAL MUTATION 1: Occasionally make genes equal (detects a == b bugs)
    if len(chromosome.genes) >= 2 and random.random() < 0.3:
        # Pick two random gene positions and make them equal
        idx1, idx2 = random.sample(range(len(chromosome.genes)), 2)
        chromosome.genes[idx2] = chromosome.genes[idx1]
    
    # SPECIAL MUTATION 2: Boundary value testing (10% chance)
    if random.random() < 0.1:
        idx = random.randint(0, len(chromosome.genes) - 1)
        val = chromosome.genes[idx]
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            boundary_values = [0, -1, 1, -100, 100]
            chromosome.genes[idx] = random.choice(boundary_values)
            return  # Skip standard mutation this time
    
    # STANDARD MUTATION: Apply to each gene with given rate
    for i in range(len(chromosome.genes)):
        if random.random() < rate:
            val = chromosome.genes[i]
            
            # Mutate Integers - MORE AGGRESSIVE
            if isinstance(val, int) and not isinstance(val, bool):
                mutation_type = random.choice(['small', 'large', 'sign_flip', 'boundary'])
                
                if mutation_type == 'small':
                    chromosome.genes[i] += random.randint(-5, 5)
                elif mutation_type == 'large':
                    chromosome.genes[i] += random.randint(-50, 50)
                elif mutation_type == 'sign_flip':
                    chromosome.genes[i] = -val
                else:  # boundary
                    chromosome.genes[i] = random.choice([0, -1, 1, val])
                
            # Mutate Floats - MORE AGGRESSIVE
            elif isinstance(val, float):
                mutation_type = random.choice(['small', 'large', 'boundary'])
                
                if mutation_type == 'small':
                    chromosome.genes[i] = round(val + random.uniform(-5.0, 5.0), 2)
                elif mutation_type == 'large':
                    chromosome.genes[i] = round(val + random.uniform(-50.0, 50.0), 2)
                else:  # boundary
                    chromosome.genes[i] = random.choice([0.0, -1.0, 1.0, val])
                
            # Mutate Booleans (Flip 0 -> 1)
            elif isinstance(val, bool) or val in [0, 1]: 
                chromosome.genes[i] = 1 - val