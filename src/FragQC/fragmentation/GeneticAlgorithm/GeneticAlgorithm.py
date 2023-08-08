import random
from .utils import error_balanced_mincut_finding_algorithm
from src.FragQC.Result import Result

from typing import Any, List, Mapping

from dataclasses import dataclass, field

@dataclass
class GeneticAlgorithmResult:
    cost: float
    iteration: int
    history: List[Mapping[str, Any]] = field()
    partition: List[int] = field()

class GeneticAlgorithm:
    def __init__(self, initial_state = None, minima_iteration_threshold = 256) -> None:
        self.initial_state = initial_state
        self.minima_iteration_threshold = minima_iteration_threshold

    def __call__(self, A, ) -> Result:
        _initial_state = self.initial_state if self.initial_state else random.sample(population = [0, 1] * A.shape[0], k = A.shape[0])

        fragments, score, result = error_balanced_mincut_finding_algorithm(A, _initial_state, minima_iteration_threshold=self.minima_iteration_threshold)

        result = Result(min_cost = score, partition = fragments, raw_results = GeneticAlgorithmResult(**result))

        return result
