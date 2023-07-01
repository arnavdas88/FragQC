import uuid
from .utils import get_qubo_qiskit

from qiskit_optimization.algorithms import OptimizationAlgorithm , MinimumEigenOptimizer, CplexOptimizer
from qiskit_optimization.problems.variable import VarType
from qiskit_optimization.converters.quadratic_program_to_qubo import QuadraticProgramToQubo
from qiskit_optimization.translators import from_docplex_mp

from typing import Any, Union

from src.FragQC.Result import Result

class Qiskit:
    def __init__(self, solver: OptimizationAlgorithm = CplexOptimizer()) -> None:
        self.solver = solver
        self.id = uuid.uuid4()

    def __call__(self, A, ) -> Result:
        normalized_A = (A * A.mean()) / A.max()
        V = A.diagonal()
        qubo = get_qubo_qiskit( normalized_A, V )


        # Solver
        sampleset = self.solver.solve(qubo) # label is str(self.id)


        fragments, score = sampleset.variables_dict.values(), sampleset.fval

        result = Result(min_cost = score, partition = fragments, raw_results = sampleset)

        return result
