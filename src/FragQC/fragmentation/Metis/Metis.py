import random
from src.FragQC.Result import Result
from src.FragQC.fragmentation.GeneticAlgorithm.utils import cost_calculation

import pymetis

from typing import Any, List, Mapping

from dataclasses import dataclass, field

@dataclass
class MetisResult:
    cost: float
    num_cuts: float
    partition: List[int] = field()

class MetisAlgorithm:
    def __init__(self, ) -> None:
        pass

    def __call__(self, A, ) -> Result:
        n_cuts, bipartition = pymetis.part_graph(2, adjacency=A, recursive=True, options=pymetis.Options(ncuts=4))
        cost = cost_calculation(A, bipartition)
        result = Result(min_cost = cost, partition = bipartition, raw_results = MetisResult(partition=bipartition, num_cuts=n_cuts, cost=cost))

        return result
