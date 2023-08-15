# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm
from src.FragQC.fragmentation.QUBO import DWave

# Cost calculation for benchmarking
from src.FragQC.fragmentation.GeneticAlgorithm.utils import cost_calculation

# Import DWave Utilities
from dwave.system import LeapHybridCQMSampler

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

# Import QuantumCircuit for loading QASM
from qiskit.circuit import QuantumCircuit

# Import PathLib to load all benchmark circuits from directory
from pathlib import Path, PosixPath

import pandas as pd
from humanize import time as htime

from circ import qc, qc2
from config import config
from utils import run_benchmark

from src.FragQC.utils.random_circuit import random_circuit


# depths = [5, 7, 9, 11, 13, 15, 17, 19]
# qubits = [9, 12, 15, 18, 21, 24, 27, 30]
# cx     = [ 5, 6, 7, 8, 9, 10, 11, 12 ]

table = []

if __name__ == '__main__':
    qasm_directory = Path("./benchmark/circuits/large")
    # qasm_files = qasm_directory.glob('*.qasm')
    # qasm_files = qasm_directory.glob('ising_n26.qasm')
    qasm_files = qasm_directory.glob('ghz_n23.qasm')

    for qasm_file in qasm_files:
        name = qasm_file.name.split("/")[-1]


        print("[ ]")
        print(f"[+] [     {name}     ]")

        # Load the QASM file
        circuit = QuantumCircuit.from_qasm_file(qasm_file)
        print(f"[i] circuit.count_ops : {circuit.count_ops()}")
    
        # Circuit Fragmentor Initialization
        fragmentor_1 = FragQC(
            circuit,
            fragmentation_procedure = DWave(
                solver = LeapHybridCQMSampler(
                    token = "DEV-250982c5b9884d2243107ec57c616b5206b415de"
                )
            ),
            hardware = DummyHardware
        )

        # Circuit Fragmentor Execution
        result_1, circuit_cut_1, _ = fragmentor_1.cut()



        fragmentor_2 = FragQC(
            circuit,
            fragmentation_procedure = GeneticAlgorithm(minima_iteration_threshold=2048),
            hardware = DummyHardware
        )

        # Circuit Fragmentor Execution
        result_2, circuit_cut_2, _ = fragmentor_2.cut()

        pass
