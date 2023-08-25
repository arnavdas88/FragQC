# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm
from src.FragQC.fragmentation.QUBO import DWave
from src.FragQC.fragmentation.Metis import MetisAlgorithm

# Import DWave Utilities
from dwave.system import LeapHybridCQMSampler

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware, GateError

# Import QuantumCircuit for loading QASM
from qiskit import transpile
from qiskit.circuit import QuantumCircuit

# Import PathLib to load all benchmark circuits from directory
from pathlib import Path, PosixPath

import json

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
    qasm_files = qasm_directory.glob('*.qasm')
    # qasm_files = qasm_directory.glob('shors_ecc9.qasm')
    # qasm_files = qasm_directory.glob('ghz_n20.qasm')

    for qasm_file in qasm_files:
        name = qasm_file.name.split("/")[-1]


        print("[ ]")
        print(f"[+] [     {name}     ]")

        # Load the QASM file
        circuit = QuantumCircuit.from_qasm_file(qasm_file)
        circuit = transpile(circuit, basis_gates=list(GateError.__GATE_MAPPING__.keys()) + ['cx'])
        print(f"[i] circuit.count_ops : {circuit.count_ops()}")

        cx_count = circuit.count_ops()['cx']
        half_cx = int(cx_count / 2)
        initial_state = ([0] * half_cx) + ([1] * (cx_count - half_cx)) 
        # initial_state = [0, 1] * half_cx
    
        # Circuit Fragmentor Initialization
        fragmentor = FragQC(
            circuit,
            # fragmentation_procedure = DWave(
            #     solver = LeapHybridCQMSampler(
            #         token = "DEV-250982c5b9884d2243107ec57c616b5206b415de"
            #     )
            # ),
            fragmentation_procedure = GeneticAlgorithm(initial_state=initial_state, minima_iteration_threshold=4096),
            # fragmentation_procedure = MetisAlgorithm(),
            hardware = DummyHardware
        )

        # Circuit Fragmentor Execution
        # result, circuit_cut, _ = fragmentor.cut()
        result, circuit_cut = fragmentor.recursive_cut(minimum_success_probability = .7)
        
        noisy_fidelity, fragqc_fidelity, ttime = run_benchmark(circuit, result, circuit_cut, config)
        
        print(f"[ ] {noisy_fidelity=}")
        print(f"[ ] {fragqc_fidelity=}")
        print(f"[ ] in {htime.precisedelta(ttime)}")
        row = {
                "circuit":  name,
                "noisy_fidelity": noisy_fidelity,
                "fragqc_fidelity": fragqc_fidelity,
                "fragments.length": len(circuit_cut['subcircuits']),
                "fragments.partition": "".join([str(p) for p in result.partition]),
                "num_cust": result.num_cuts,
                "timedelta": ttime,
                "humanize_timedelta": htime.precisedelta(ttime),
            }
        print(f"[j] {row}")
        table.append(
            row
        )
    result_table = pd.DataFrame(data=table)
    print(table)    
    print(result_table)

    json.dump(table, open('results.json', 'w+'))
