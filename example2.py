# Import a Dummy Circuit
from circ import qc

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

from qiskit_ibm_runtime import QiskitRuntimeService, Options, Sampler
from qiskit.providers.fake_provider import FakeManila, FakeNairobi
from qiskit_aer.noise import NoiseModel

# Circuit Knitting for reconstruction
from circuit_knitting_toolbox.circuit_cutting.cutqc import verify
from circuit_knitting_toolbox.circuit_cutting.cutqc import cut_circuit_wires
from circuit_knitting_toolbox.circuit_cutting.cutqc import evaluate_subcircuits
from circuit_knitting_toolbox.circuit_cutting.cutqc import reconstruct_full_distribution

# Evaluate fidelity
from qiskit.result import ProbDistribution
from qiskit.quantum_info.analysis import hellinger_fidelity


def fragqc(qc, **kwargs):
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

    # Get sub-circuits for the fragment
    cuts = cut_circuit_wires(
        circuit=qc, method="manual", subcircuit_vertices=list(result.buckets().values())
    )
    # Get sub-circuits probabilities
    subcircuit_instance_probabilities = evaluate_subcircuits(cuts, **kwargs)

    # Get reconstructed results
    reconstructed_probabilities = reconstruct_full_distribution( qc, subcircuit_instance_probabilities, cuts, num_threads=1 )

    return cuts, reconstructed_probabilities

def cutqc(qc, **kwargs):
    # Get sub-circuits for the fragment
    cuts = cut_circuit_wires(
        circuit=qc, method="automatic",
        max_cuts=5,
        num_subcircuits=[5],
        max_subcircuit_width=100
    )
    # Get sub-circuits probabilities
    subcircuit_instance_probabilities = evaluate_subcircuits(cuts, **kwargs)

    # Get reconstructed results
    reconstructed_probabilities = reconstruct_full_distribution( qc, subcircuit_instance_probabilities, cuts, num_threads=1 )

    return cuts, reconstructed_probabilities

def noisy(qc, backend):
    qc2 = qc.copy()
    qc2.measure_all()
    job = fake_backend.run(qc2)
    return job.result().get_counts()

def get_bitstring(qc, probabilities):
    # Create a dict for the reconstructed distribution
    distribution = {i: prob for i, prob in enumerate(probabilities)}
    # Represent states as bitstrings (instead of ints)
    dict_bitstring = ProbDistribution(data=distribution).binary_probabilities(num_bits=len(qc.qregs))

    return dict_bitstring

if __name__ == '__main__':

    service = QiskitRuntimeService(channel="ibm_quantum", token="77156861472499e22abf983c7d826ebbd1862575f069a53a6040276a0550afbce8f32e5a05f36f31391e79689e358c74b3c3e441dda2a97efea8a374f1110852")

    # Make a noise model
    fake_backend = FakeManila()
    noise_model = NoiseModel.from_backend(fake_backend)

    kwargs = {
        "service": service,

        # Set the Sampler and runtime options
        "options": Options(
            execution = {"shots": 4096},
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

    # job = Sampler(backend=service.backend("ibmq_qasm_simulator"), options=kwargs['options']).run(qc)
    # result = job.result()
    noisy_output = noisy(qc, fake_backend)

    fragqc_cuts, fragqc_reconstructed = fragqc(qc, **kwargs)
    cutqc_cuts, cutqc_reconstructed = cutqc(qc, **kwargs)

    # Evaluate the results
    fragqc_metrics, exact_probabilities = verify(qc, fragqc_reconstructed)
    cutqc_metrics, exact_probabilities = verify(qc, cutqc_reconstructed)

    exact_dict_bitstring = get_bitstring(qc, exact_probabilities)
    fragqc_reconstructed_dict_bitstring = get_bitstring(qc, fragqc_reconstructed)
    cutqc_reconstructed_dict_bitstring = get_bitstring(qc, cutqc_reconstructed)

    # # Create the ground truth distribution dict
    # exact_distribution = {i: prob for i, prob in enumerate(exact_probabilities)}
    # # Represent states as bitstrings (instead of ints)
    # exact_dict_bitstring = ProbDistribution(data=exact_distribution).binary_probabilities(num_bits=len(qc.qregs))

    # # Create a dict for the reconstructed distribution
    # reconstructed_distribution = {i: prob for i, prob in enumerate(reconstructed_probabilities)}
    # # Represent states as bitstrings (instead of ints)
    # reconstructed_dict_bitstring = ProbDistribution(data=reconstructed_distribution).binary_probabilities(num_bits=len(qc.qregs))
    
    
    noisy_fidelity = hellinger_fidelity(exact_dict_bitstring, noisy_output)
    fragqc_fidelity = hellinger_fidelity(exact_dict_bitstring, fragqc_reconstructed_dict_bitstring)
    cutqc_fidelity = hellinger_fidelity(exact_dict_bitstring, cutqc_reconstructed_dict_bitstring)

    # for state, (eprob, rprob) in zip(exact_dict_bitstring.keys(), zip(exact_dict_bitstring.values(), reconstructed_dict_bitstring.values())):
    #     print(f"{state.zfill(5)} : {eprob:.7f}, {rprob:.7f}, {abs(eprob - rprob):.7f}")

    print(f"{noisy_fidelity=}")
    print(f"{fragqc_fidelity=}")
    print(f"{cutqc_fidelity=}")
    
    pass

