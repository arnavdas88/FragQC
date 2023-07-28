import time
from humanize import time as htime

from qiskit import Aer, transpile

# Evaluate fidelity
from qiskit.result import ProbDistribution
from qiskit.quantum_info.analysis import hellinger_fidelity

# Circuit Knitting for reconstruction
from circuit_knitting_toolbox.circuit_cutting.cutqc import verify
from circuit_knitting_toolbox.circuit_cutting.cutqc import cut_circuit_wires
from circuit_knitting_toolbox.circuit_cutting.cutqc import evaluate_subcircuits
from circuit_knitting_toolbox.circuit_cutting.cutqc import reconstruct_full_distribution

def fragqc(qc, circuit_cut, **kwargs):
    qc.remove_final_measurements()

    # Get sub-circuits probabilities
    sip_start = time.perf_counter()
    subcircuit_instance_probabilities = evaluate_subcircuits(circuit_cut, **kwargs)
    sip_end = time.perf_counter()
    print(f"[i] cutqc.evaluate_subcircuits took {htime.precisedelta(sip_end - sip_start)}")

    # Get reconstructed results
    rfd_start = time.perf_counter()
    reconstructed_probabilities = reconstruct_full_distribution( 
        circuit = qc, subcircuit_instance_probabilities = subcircuit_instance_probabilities, 
        cuts = circuit_cut, num_threads=10 )
    rfd_end = time.perf_counter()
    print(f"[i] cutqc.reconstruct_full_distribution took {htime.precisedelta(rfd_end - rfd_start)}")

    return circuit_cut, reconstructed_probabilities

def cutqc(qc, **kwargs):
    qc.remove_final_measurements()
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
    reconstructed_probabilities = reconstruct_full_distribution( qc, subcircuit_instance_probabilities, cuts, num_threads=10 )
    qc.measure_all()

    return cuts, reconstructed_probabilities

def noisy(qc, backend):
    qc = qc.copy()
    qc.remove_final_measurements()
    qc.measure_all()
    backend.set_options(
            max_parallel_threads = 0,
            max_parallel_experiments = 0,
            max_parallel_shots = 0,
    )
    job = backend.run(qc, )
    return job.result().get_counts()

def svs(qc,):
    qc = qc.copy()
    qc.remove_final_measurements()
    qc.measure_all()

    backend = Aer.get_backend('aer_simulator')

    backend.set_options(
            max_parallel_threads = 0,
            max_parallel_experiments = 0,
            max_parallel_shots = 0,
    )

    # Run and get counts
    job = backend.run(qc)
    return job.result().get_counts()


def get_bitstring(qc, probabilities):
    # Create a dict for the reconstructed distribution
    distribution = {i: prob for i, prob in enumerate(probabilities)}
    # Represent states as bitstrings (instead of ints)
    dict_bitstring = ProbDistribution(data=distribution).binary_probabilities(num_bits=len(qc.qregs))

    return {k.zfill(len(qc.qubits)):v for k, v in dict_bitstring.items()}


def run_benchmark(qc, result, circuit_cut, config):
    (fake_backend, kwargs) = config

    noisy_fidelity = 0
    svs_dict_bitstring = []
    # print("[ ] Started Noisy Simulation")
    # noisy_output = noisy(qc, fake_backend)
    # svs_dict_bitstring = svs(qc)
    # noisy_fidelity = hellinger_fidelity(svs_dict_bitstring, noisy_output)
    # print("[ ] Ran Noisy Simulation")

    try:
        print("[ ] Started FragQC Simulation")
        fragqc_cuts, fragqc_reconstructed = fragqc(qc, circuit_cut, **kwargs)
        # fragqc_metrics, exact_probabilities = verify(qc, fragqc_reconstructed)
        fragqc_reconstructed_dict_bitstring = get_bitstring(qc, fragqc_reconstructed)
        fragqc_fidelity = None
        # fragqc_fidelity = hellinger_fidelity(svs_dict_bitstring, fragqc_reconstructed_dict_bitstring)
        print("[ ] Ran FragQC Simulation")
    except Exception as ex:
        print("[ ] Cannot run FragQC Simulation")
        fragqc_fidelity = None

    try:
        print("[ ] Started CutQC Simulation")
        cutqc_cuts, cutqc_reconstructed = cutqc(qc, **kwargs)
        # cutqc_metrics, exact_probabilities = verify(qc, cutqc_reconstructed)
        cutqc_reconstructed_dict_bitstring = get_bitstring(qc, cutqc_reconstructed)
        cutqc_fidelity = None
        # cutqc_fidelity = hellinger_fidelity(svs_dict_bitstring, cutqc_reconstructed_dict_bitstring)
        print("[ ] Ran CutQC Simulation")
    except Exception as ex:
        print("[ ] Cannot run CutQC Simulation")
        cutqc_fidelity = None


    # exact_dict_bitstring = get_bitstring(qc, exact_probabilities)

    # # Create the ground truth distribution dict
    # exact_distribution = {i: prob for i, prob in enumerate(exact_probabilities)}
    # # Represent states as bitstrings (instead of ints)
    # exact_dict_bitstring = ProbDistribution(data=exact_distribution).binary_probabilities(num_bits=len(qc.qregs))

    # # Create a dict for the reconstructed distribution
    # reconstructed_distribution = {i: prob for i, prob in enumerate(reconstructed_probabilities)}
    # # Represent states as bitstrings (instead of ints)
    # reconstructed_dict_bitstring = ProbDistribution(data=reconstructed_distribution).binary_probabilities(num_bits=len(qc.qregs))
    
    


    # print(f"{noisy_fidelity=}")
    # print(f"{fragqc_fidelity=}")
    # print(f"{cutqc_fidelity=}")


    return noisy_fidelity, fragqc_fidelity, cutqc_fidelity