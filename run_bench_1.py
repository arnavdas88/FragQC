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

# Benchmarking Simulation Imports
from qiskit_ibm_runtime import QiskitRuntimeService, Options, Sampler
from qiskit.providers.fake_provider import FakeManila, FakeNairobi, FakeHanoi
from qiskit_aer.noise import NoiseModel

from utils import run_benchmark

if __name__ == '__main__':
    # qasm_directory = Path("./benchmark/circuits/small")
    qasm_directory = Path("./benchmark/circuits/large")

    service = QiskitRuntimeService(channel="ibm_quantum", token="77156861472499e22abf983c7d826ebbd1862575f069a53a6040276a0550afbce8f32e5a05f36f31391e79689e358c74b3c3e441dda2a97efea8a374f1110852")

    # Make a noise model
    fake_backend = FakeHanoi()
    noise_model = NoiseModel.from_backend(fake_backend)

    kwargs = {
        "service": service,

        # Set the Sampler and runtime options
        "options": Options(
            execution = {"shots": 1024},
            simulator = {
                "noise_model": noise_model,
                "basis_gates": fake_backend.configuration().basis_gates,
                "coupling_map": fake_backend.configuration().coupling_map,
                "seed_simulator": 42
            },
            optimization_level = 0,
            resilience_level = 0
        ),

        # Run parallel qasm simulator threads
        "backend_names": ["ibmq_qasm_simulator"],
        
    }

    config = (fake_backend, kwargs)

    for qasm_file in qasm_directory.glob('*.qasm'):
        # Load the QASM file
        qc = QuantumCircuit.from_qasm_file(qasm_file)

        # Circuit Fragmentor Initialization
        fragmentor = FragQC(
            qc,
            fragmentation_procedure = GeneticAlgorithm(),
            hardware = DummyHardware
        )

        # Circuit Fragmentor Execution
        result, circuit_cut = fragmentor.recursive_cut(minimum_success_probability = .8)

        run_benchmark(qc, result, circuit_cut, config)
        pass
