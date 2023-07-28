# Import a Dummy Circuit
from circ import qc, qc2

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

if __name__ == '__main__':
    # Circuit Fragmentor Initialization
    fragmentor = FragQC(
        qc2,
        fragmentation_procedure = GeneticAlgorithm(),
        hardware = DummyHardware
    )

    # Circuit Fragmentor Execution
    result = fragmentor.recursive_cut()
