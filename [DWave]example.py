# Import a Dummy Circuit
from circ import qc

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the DWave Backend for FragQC
from src.FragQC.fragmentation.QUBO import DWave

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

# Import DWave Utilities
from dwave.system import LeapHybridCQMSampler

# Circuit Fragmentor Initialization
fragmentor = FragQC(
    qc,
    fragmentation_procedure = DWave(
        solver = LeapHybridCQMSampler(
            token = "DEV-250982c5b9884d2243107ec57c616b5206b415de"
        )
    ),
    hardware = DummyHardware
)

# Circuit Fragmentor Execution
fragments, result = fragmentor.fragment()

# Show Results
print("Score :", result.min_cost)

for cx_node_name, fragment_bag, cx_node in fragments:
    print(cx_node_name, fragment_bag)
