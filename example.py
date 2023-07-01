from circ import qc
from src.FragQC.FragQC import FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm
from src.FragQC.fragmentation.QUBO import DWave
from src.FragQC.fragmentation.QUBO import Qiskit

from qiskit_optimization.algorithms import MinimumEigenOptimizer, CplexOptimizer
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler
from qiskit.algorithms import QAOA

from src.FragQC.Hardware import DummyHardware

# from dwave.system import LeapHybridCQMSampler

fragmentor = FragQC(
    qc,
    # fragmentation_procedure = GeneticAlgorithm(
    #     initial_state = [int(x) for x in "1 0 0 1 0 1 0 0".split()]
    # ),
    # fragmentation_procedure = DWave(
    #     # solver = LeapHybridCQMSampler(
    #     #     token = "DEV-250982c5b9884d2243107ec57c616b5206b415de"
    #     # )
    # ),
    fragmentation_procedure = Qiskit(
        solver=MinimumEigenOptimizer(QAOA(optimizer=COBYLA()))
    ),
    hardware = DummyHardware
)

score, fragments, time = fragmentor.fragment()

print("Score :", score)

for cx_node_name, fragment_bag, cx_node in fragments:
    print(cx_node_name, fragment_bag)