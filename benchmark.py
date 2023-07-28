from qiskit.circuit.random import random_circuit
from circ import qc

from src.FragQC.FragQC import FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm
from src.FragQC.fragmentation.QUBO import DWave

from src.FragQC.utils.random_circuit import random_circuit

from dwave.system import LeapHybridCQMSampler

circuit = random_circuit(
    num_qubits = 20,
    depth = 20,
    max_operands = 2,
    seed = 123412
)
fragmentor = FragQC(
    circuit.decompose(gates_to_decompose=['swap']),
    fragmentation_procedure = GeneticAlgorithm()
)

fragments, result = fragmentor.fragment()

# print("Score :", score)

for cx_node_name, fragment_bag, cx_node in fragments:
    print(cx_node_name, fragment_bag)