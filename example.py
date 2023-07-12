# Import a Dummy Circuit
from circ import qc

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the GeneticAlgorithm Backend for FragQC
from src.FragQC.fragmentation.GeneticAlgorithm import GeneticAlgorithm

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

if __name__ == '__main__':
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
    
    # Circuit Knitting for reconstruction
    from circuit_knitting_toolbox.circuit_cutting.cutqc import verify
    from circuit_knitting_toolbox.circuit_cutting.cutqc import cut_circuit_wires
    from circuit_knitting_toolbox.circuit_cutting.cutqc import evaluate_subcircuits
    from circuit_knitting_toolbox.circuit_cutting.cutqc import reconstruct_full_distribution

    # Get sub-circuits for the fragment
    cuts = cut_circuit_wires(
        circuit=qc, method="manual", subcircuit_vertices=list(result.buckets().values())
    )
    # Get sub-circuits probabilities
    subcircuit_instance_probabilities = evaluate_subcircuits(cuts)

    # Get reconstructed results
    reconstructed_probabilities = reconstruct_full_distribution( qc, subcircuit_instance_probabilities, cuts, num_threads=1 )

    # Evaluate the results
    metrics, exact_probabilities = verify(qc, reconstructed_probabilities)

    # Evaluate fidelity
    from qiskit.result import ProbDistribution
    from qiskit.quantum_info.analysis import hellinger_fidelity

    # Create the ground truth distribution dict
    exact_distribution = {i: prob for i, prob in enumerate(exact_probabilities)}
    # Represent states as bitstrings (instead of ints)
    exact_dict_bitstring = ProbDistribution(data=exact_distribution).binary_probabilities(num_bits=len(qc.qregs))

    # Create a dict for the reconstructed distribution
    reconstructed_distribution = {i: prob for i, prob in enumerate(reconstructed_probabilities)}
    # Represent states as bitstrings (instead of ints)
    reconstructed_dict_bitstring = ProbDistribution(data=reconstructed_distribution).binary_probabilities(num_bits=len(qc.qregs))

    fidelity = hellinger_fidelity(exact_dict_bitstring, reconstructed_dict_bitstring)

    for state, (eprob, rprob) in zip(exact_dict_bitstring.keys(), zip(exact_dict_bitstring.values(), reconstructed_dict_bitstring.values())):
        print(f"{state.zfill(5)} : {eprob:.7f}, {rprob:.7f}, {abs(eprob - rprob):.7f}")
    
    pass

