# Import a Dummy Circuit
from src.FragQC.utils.random_circuit import random_circuit

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

# Circuit Fragmentor Initialization
fragmentor = FragQC(
    random_circuit(num_qubits = 10, depth = 50).decompose(gates_to_decompose = ['h', 'u1', 'u2', 'cx']),
    fragmentation_procedure = GeneticAlgorithm(),
    hardware = DummyHardware
)

# Circuit Fragmentor Execution
fragments, result = fragmentor.fragment()

# Show Results
print("Score :", result.min_cost)

for cx_node_name, fragment_bag, cx_node in fragments:
    print(cx_node_name, fragment_bag)
