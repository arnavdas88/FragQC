import uuid
from .utils import get_qubo_qiskit

# from qiskit.algorithms.minimum_eigensolvers import QAOA, NumPyMinimumEigensolver
# from qiskit.algorithms.optimizers import COBYLA
# from qiskit.primitives import Sampler
# from qiskit.utils.algorithm_globals import algorithm_globals
from qiskit_optimization.algorithms import OptimizationAlgorithm , MinimumEigenOptimizer, CplexOptimizer
from qiskit_optimization.problems.variable import VarType
from qiskit_optimization.converters.quadratic_program_to_qubo import QuadraticProgramToQubo
from qiskit_optimization.translators import from_docplex_mp

from typing import Any, Union

# Union[OptimizationAlgorithm, ]
class Qiskit:
    def __init__(self, solver: OptimizationAlgorithm = CplexOptimizer()) -> None:
        self.solver = solver
        self.id = uuid.uuid4()

    def __call__(self, A, ) -> Any:
        normalized_A = (A * A.mean()) / A.max()
        V = A.diagonal()
        qubo = get_qubo_qiskit( normalized_A, V )


        # Solver
        sampleset = self.solver.solve(qubo) # label is str(self.id)

        record = sampleset.lowest().record[0]

        fragments, score = record[0], record[1]

        return fragments, score
