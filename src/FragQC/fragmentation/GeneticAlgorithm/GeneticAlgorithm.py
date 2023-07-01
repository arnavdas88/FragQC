from .utils import error_balanced_mincut_finding_algorithm
import random
from typing import Any


class GeneticAlgorithm:
    def __init__(self, initial_state = None) -> None:
        self.initial_state = initial_state

    def __call__(self, A, ) -> Any:
        if self.initial_state is None:
            self.initial_state = random.sample(population = [0, 1] * A.shape[0], k = A.shape[0])
        fragments, score = error_balanced_mincut_finding_algorithm(A, self.initial_state)
        return fragments, score
