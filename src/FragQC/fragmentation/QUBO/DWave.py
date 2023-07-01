import uuid
from .utils import get_qubo_dwave

from dimod import ConstrainedQuadraticModel, BinaryQuadraticModel, Integer, Binary, ExactCQMSolver, Sampler
from typing import Any


class DWave:
    def __init__(self, solver: Sampler = ExactCQMSolver()) -> None:
        self.solver = solver
        self.id = uuid.uuid4()

    def __call__(self, A, ) -> Any:
        normalized_A = (A * A.mean()) / A.max()
        V = A.diagonal()
        qubo = get_qubo_dwave( normalized_A, V )

        # Defining the model
        cqm = ConstrainedQuadraticModel()

        cqm.set_objective(qubo)

        # Solver
        sampler = self.solver
        sampleset = sampler.sample_cqm(cqm, label=str(self.id))

        record = sampleset.lowest().record[0]

        fragments, score = record[0], record[1]

        return fragments, score
