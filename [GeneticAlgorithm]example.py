# Import a Dummy Circuit
from circ import qc

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

# Circuit Fragmentor Initialization
fragmentor = FragQC(
    qc,
    fragmentation_procedure = GeneticAlgorithm(
        initial_state = [int(x) for x in "1 0 0 1 0 1 0 0".split()]
    ),
    hardware = DummyHardware
)

# Circuit Fragmentor Execution
fragments, result = fragmentor.fragment()

# Show Results
print("Score :", result.min_cost)

for cx_node_name, fragment_bag, cx_node in fragments:
    print(cx_node_name, fragment_bag)
