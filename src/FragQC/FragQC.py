import time
from typing import Any
from qiskit import QuantumCircuit
from src.FragQC.Hardware import Hardware, DummyHardware
from src.FragQC.utils import create_index_node_map, cx_adjacency, individual_fragment_error, error_probability_full_circuit
from src.FragQC.utils.circuit_knitting_toolbox import path_map_subcircuit, replace_from_base_map
from src.FragQC.utils.base import combine_results, least_success_probability

# Circuit Knitting for reconstruction
from circuit_knitting_toolbox.circuit_cutting.cutqc import verify
from circuit_knitting_toolbox.circuit_cutting.cutqc import cut_circuit_wires
from circuit_knitting_toolbox.circuit_cutting.cutqc import evaluate_subcircuits
from circuit_knitting_toolbox.circuit_cutting.cutqc import reconstruct_full_distribution

class FragQC:
    def __init__(self, circuit : QuantumCircuit, fragmentation_procedure = None, hardware: Hardware = DummyHardware ) -> None:
        if not fragmentation_procedure:
            raise Exception("No Fragmentation procedure is defined!")
        self.raw_circuit = circuit
        self.circuit = circuit.copy()
        self.circuit.remove_final_measurements()
        self.fragmentation_procedure = fragmentation_procedure
        self.hardware = hardware

        self.subcircuits = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    def fragment(self, ):
        adj = cx_adjacency(self.circuit, self.hardware)
        fragment_error = individual_fragment_error(self.circuit, self.hardware)
        full_circuit_error_probability = error_probability_full_circuit(self.circuit, self.hardware)
        assert adj.shape == ( len(fragment_error), len(fragment_error) )

        for index, error in enumerate(fragment_error):
            adj[index, index] += error
        mapping_i2n, mapping_n2i, mapping_names = create_index_node_map(self.circuit)

        starting_time = time.time()
        result = self.fragmentation_procedure(adj)
        ending_time = time.time()
        result.time = (ending_time - starting_time)

        fragment_map, score = result.partition, result.min_cost

        return [ (name, fragment_bag, cx, ) for (name, cx), fragment_bag in zip(mapping_names.items(), fragment_map) ], result

    def cut(self, previous_cut = None, cut_index=0):
        if previous_cut:
            subcircuits, subcircuit_vertices = list(zip(*previous_cut))
            subcircuits, subcircuit_vertices = list(subcircuits), list(subcircuit_vertices)

        if previous_cut:
            _circuit = self.circuit
            self.circuit = subcircuits[cut_index]

        fragments, result = self.fragment()

        if previous_cut:
            result.base_mapping = subcircuit_vertices.pop(cut_index)

        if previous_cut:
            self.circuit = _circuit

        if previous_cut:
            subcircuit_vertices += list(result.buckets().values())
        else:
            subcircuit_vertices = list(result.buckets().values())

        circuit_cut = cut_circuit_wires(
                circuit=self.circuit, 
                method="manual", 
                subcircuit_vertices=subcircuit_vertices
            )
        result.subcircuits = circuit_cut['subcircuits']
        return fragments, result, circuit_cut

    def recursive_cut(self, ):
        # subcircuit_idx_to_cut = 0
        # if not self.subcircuits:
        #     fragments, result, circuit_cut = self.cut()
        #     self.subcircuits = result
        # else:
        #     fragments, result, circuit_cut = self.cut(self.subcircuits.subcircuit_partition(), subcircuit_idx_to_cut)
        #     self.subcircuits = combine_results(self.subcircuits, result)

        # return self.subcircuits

        if not self.subcircuits:
            fragments, result, circuit_cut = self.cut()
            self.subcircuits = result
        
        prob, idx = least_success_probability(result, self.hardware)
        while prob < .832:
                fragments, result, circuit_cut = self.cut(self.subcircuits.subcircuit_partition(), idx)
                self.subcircuits = combine_results(self.subcircuits, result)
                prob, idx = least_success_probability(result, self.hardware)

