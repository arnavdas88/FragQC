# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

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
    qasm_directory = Path("./benchmark/circuits/private_bench")
    # qasm_files = qasm_directory.glob('*.qasm')
    qasm_files = qasm_directory.glob('ising_n26.qasm')

    for qasm_file in qasm_files:
        name = qasm_file.name.split("/")[-1]


        print("[ ]")
        print(f"[+] [     {name}     ]")

        # Load the QASM file
        circuit = QuantumCircuit.from_qasm_file(qasm_file)
        print(f"[i] circuit.count_ops : {circuit.count_ops()}")
    
        # Circuit Fragmentor Initialization
        fragmentor = FragQC(
            circuit,
            fragmentation_procedure = GeneticAlgorithm(minima_iteration_threshold=2048),
            hardware = DummyHardware
        )

        # Circuit Fragmentor Execution
        result, circuit_cut = fragmentor.recursive_cut(minimum_success_probability = .8)
        
        noisy_fidelity, fragqc_fidelity, ttime = run_benchmark(circuit, result, circuit_cut, config)
        
        print(f"[ ] {noisy_fidelity=}")
        print(f"[ ] {fragqc_fidelity=}")
        print(f"[ ] in {htime.precisedelta(ttime)}")

        table.append(
            {
                "circuit":  name,
                "noisy_fidelity": noisy_fidelity,
                "fragqc_fidelity": fragqc_fidelity,
                "fragments.length": len(circuit_cut['subcircuits']),
                "fragments.partition": result.partition,
                "timedelta": ttime,
                "humanize_timedelta": htime.precisedelta(ttime),
            }
        )
    result_table = pd.DataFrame(data=table)
    print(result_table)    
