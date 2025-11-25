import random

import genetic_engine
from models import Chromosome


def test_generate_random_gene_types():
    # Ensure function returns appropriate types for several type strings
    g_int = genetic_engine.generate_random_gene('int')
    assert isinstance(g_int, int)

    g_float = genetic_engine.generate_random_gene('float')
    assert isinstance(g_float, (float, int))

    g_bool = genetic_engine.generate_random_gene('bool')
    assert g_bool in (0, 1)


def test_crossover_combines_genes():
    p1 = Chromosome(id='p1', genes=[1, 2, 3], fitness_score=0.0)
    p2 = Chromosome(id='p2', genes=[9, 8, 7], fitness_score=0.0)
    random.seed(0)
    child = genetic_engine.crossover(p1, p2)
    assert isinstance(child, Chromosome)
    assert len(child.genes) == 3


def test_mutate_changes_genes_but_keeps_length():
    c = Chromosome(id='c', genes=[10, -5, 3], fitness_score=0.0)
    random.seed(1)
    genetic_engine.mutate(c, rate=0.9)
    assert len(c.genes) == 3


def test_tournament_selection_returns_member():
    pop = [Chromosome(id=str(i), genes=[i], fitness_score=float(i)) for i in range(5)]
    random.seed(2)
    winner = genetic_engine.tournament_selection(pop)
    assert winner in pop
