import time
from humanize import time as htime

from qiskit import Aer, transpile

import numpy as np

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

    return circuit_cut, reconstructed_probabilities, (sip_end - sip_start) + (rfd_end - rfd_start)
 
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

    return cuts, reconstructed_probabilities, _

def noisy(qc, backend_names, options, *args, **kwargs):
    qc = qc.copy()
    qc.remove_final_measurements()
    qc.measure_all()
    backend = Aer.get_backend(backend_names[0])
    backend.set_options(**options.simulator.__dict__)
    job = backend.run(qc, )
    return job.result().get_counts()

def svs(qc, shots):
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
    job = backend.run(qc, shots=shots)
    return job.result().get_counts()


def get_bitstring(qc, probabilities, shots):
    # Create a dict for the reconstructed distribution
    distribution = {i: prob for i, prob in enumerate(probabilities)}
    # Represent states as bitstrings (instead of ints)
    dict_bitstring = ProbDistribution(data=distribution).binary_probabilities(num_bits=len(qc.qregs))

    return {k.zfill(len(qc.qubits)):np.floor(max(v, 0)*shots) for k, v in dict_bitstring.items()}


def run_benchmark(qc, result, circuit_cut, config):
    kwargs = config

    noisy_fidelity = 0
    svs_dict_bitstring = []
    print("[ ] Started Noisy Simulation")
    noisy_output = noisy(qc, **kwargs)
    svs_dict_bitstring = svs(qc, config['options'].execution.shots)
    noisy_fidelity = hellinger_fidelity(svs_dict_bitstring, noisy_output)
    print("[ ] Ran Noisy Simulation")

    try:
        print("[ ] Started FragQC Simulation")
        fragqc_cuts, fragqc_reconstructed, ttime = fragqc(qc, circuit_cut, **kwargs)
        assert sum(fragqc_reconstructed) > 0.9999
        # fragqc_metrics, exact_probabilities = verify(qc, fragqc_reconstructed)
        fragqc_reconstructed_dict_bitstring = get_bitstring(qc, fragqc_reconstructed, config['options'].execution.shots)
        fragqc_fidelity = hellinger_fidelity(svs_dict_bitstring, fragqc_reconstructed_dict_bitstring)
        print("[ ] Ran FragQC Simulation")
    except Exception as ex:
        print("[ ] Cannot run FragQC Simulation")
        fragqc_fidelity = None
        ttime = None
    
    # print(f"{noisy_fidelity=}")
    # print(f"{fragqc_fidelity=}")

    return noisy_fidelity, fragqc_fidelity, ttime