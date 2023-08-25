# Benchmarking Simulation Imports
from qiskit_ibm_runtime import QiskitRuntimeService, Options, Sampler
from qiskit.providers.fake_provider import FakeManila, FakeNairobi, FakeHanoi, FakeKolkata, FakeSherbrooke, FakeGuadalupe
from qiskit_aer.noise import NoiseModel

# Make a noise model
# fake_backend = FakeHanoi()
# fake_backend = FakeGuadalupe()
fake_backend = FakeSherbrooke()
noise_model = NoiseModel.from_backend(fake_backend)

config = {
    "service": None,

    # Set the Sampler and runtime options
    "options": Options(
        execution = {"shots": 1024},
        simulator = {
            "noise_model": noise_model,
            "basis_gates": fake_backend.operation_names,
            # "basis_gates": fake_backend.configuration().basis_gates,
            "coupling_map": fake_backend.coupling_map,
            # "coupling_map": fake_backend.configuration().coupling_map,
            "seed_simulator": 42,
            "max_parallel_threads": 20,
            "max_parallel_shots": 512,
            "max_parallel_experiments": 20,
        },
    ),

    # Run parallel qasm simulator threads
    "backend_names": ["aer_simulator_statevector"],
    
}