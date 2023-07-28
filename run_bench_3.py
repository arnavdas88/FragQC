# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

# Import QuantumCircuit for loading QASM
from qiskit.circuit import QuantumCircuit

# Import PathLib to load all benchmark circuits from directory
from pathlib import Path
from circ import qc, qc2

# Benchmarking Simulation Imports
from qiskit_ibm_runtime import QiskitRuntimeService, Options, Sampler
from qiskit.providers.fake_provider import FakeManila, FakeNairobi, FakeHanoi
from qiskit_aer.noise import NoiseModel

from utils import run_benchmark

from src.FragQC.utils.random_circuit import random_circuit


qubits = [5, 7, 9, 11, 13, 15, 17, 19]
depths = [9, 12, 15, 18, 21, 24, 27, 30]

if __name__ == '__main__':
    # qasm_directory = Path("./benchmark/circuits/small")
    # qasm_directory = Path("./benchmark/circuits/large")

    service = QiskitRuntimeService(channel="ibm_quantum", token="77156861472499e22abf983c7d826ebbd1862575f069a53a6040276a0550afbce8f32e5a05f36f31391e79689e358c74b3c3e441dda2a97efea8a374f1110852")

    # Make a noise model
    fake_backend = FakeHanoi()
    noise_model = NoiseModel.from_backend(fake_backend)

    kwargs = {
        "service": service,

        # Set the Sampler and runtime options
        "options": Options(
            execution = {"shots": 512},
            simulator = {
                "noise_model": noise_model,
                "basis_gates": fake_backend.configuration().basis_gates,
                "coupling_map": fake_backend.configuration().coupling_map,
                "seed_simulator": 42,
                "max_parallel_threads": 20,
                "max_parallel_shots": 512,
                "max_parallel_experiments": 20,
            },
            optimization_level = 0,
            resilience_level = 0
        ),

        # Run parallel qasm simulator threads
        "backend_names": ["aer_simulator_statevector_gpu"],
        
    }

    config = (fake_backend, kwargs)

    for qubit in qubits:
        for depth in depths:
            circuit = random_circuit(
                        num_qubits = qubit,
                        depth = depth,
                        max_operands = 2,
                        seed = 123
                    )

            # Circuit Fragmentor Initialization
            fragmentor = FragQC(
                circuit,
                fragmentation_procedure = GeneticAlgorithm(),
                hardware = DummyHardware
            )

            # Circuit Fragmentor Execution
            result, circuit_cut = fragmentor.recursive_cut(minimum_success_probability = .8)

            print(f"circuit = random_circuit( num_qubits = {qubit}, depth = {depth}, max_operands = 2, seed = 123412 )")
            print(f"circuit.count_ops : {circuit.count_ops()}")
            noisy_fidelity, fragqc_fidelity, cutqc_fidelity = run_benchmark(circuit, result, circuit_cut, config)
            
            print(f"{noisy_fidelity=}")
            print(f"{fragqc_fidelity=}")
            print(f"{cutqc_fidelity=}")
