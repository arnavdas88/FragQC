import time
from typing import Any

from qiskit import QuantumCircuit
from qiskit.transpiler.passes import RemoveBarriers

from src.FragQC.Hardware import Hardware, DummyHardware
from src.FragQC.utils import create_index_node_map, cx_adjacency, individual_fragment_error, error_probability_full_circuit
from src.FragQC.utils.circuit_knitting_toolbox import path_map_subcircuit, replace_from_base_map
from src.FragQC.utils.base import combine_results, least_success_probability, remove_idle_qwires

# Circuit Knitting for reconstruction
from circuit_knitting_toolbox.circuit_cutting.cutqc import verify
from circuit_knitting_toolbox.circuit_cutting.cutqc import cut_circuit_wires
from circuit_knitting_toolbox.circuit_cutting.cutqc import evaluate_subcircuits
from circuit_knitting_toolbox.circuit_cutting.cutqc import reconstruct_full_distribution

class FragQC:
    def __init__(self, circuit : QuantumCircuit, fragmentation_procedure = None, hardware: Hardware = DummyHardware, max_cut_num = 5 ) -> None:
        if not fragmentation_procedure:
            raise Exception("No Fragmentation procedure is defined!")
        self.raw_circuit = circuit
        self.circuit = circuit.copy().decompose(gates_to_decompose=['swap', 'x', 'ccx', 'tdg', 't', 'cu1'])
        self.circuit.remove_final_measurements()
        self.circuit = RemoveBarriers()(self.circuit)
        # self.circuit = remove_idle_qwires(self.circuit)
        self.fragmentation_procedure = fragmentation_procedure
        self.hardware = hardware
        self.max_cut_num = max_cut_num

        self.subcircuits = None
        self.try_cuts = 0

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    def fragment(self, ):
        adj = cx_adjacency(self.circuit, self.hardware)
        print(f"[i] Circuit found {len(adj)} Cx gates.")
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
        
        # Experimental turned off
        # if previous_cut:
        #     for circ, node in zip(subcircuits, subcircuit_vertices):
        #         assert circ.count_ops()['cx'] == len(node)

        fragments, result = self.fragment()

        if previous_cut:
            assert len(subcircuit_vertices[cut_index]) == len(result.partition) == self.circuit.count_ops()['cx']
            # if not ( len(subcircuit_vertices[cut_index]) == len(result.partition) == self.circuit.count_ops()['cx']):
            #     print(len(subcircuit_vertices[cut_index]), len(result.partition), self.circuit.count_ops()['cx'])
            #     pass

            result.base_mapping = subcircuit_vertices.pop(cut_index)

        if previous_cut:
            self.circuit = _circuit

        if previous_cut:
            subcircuit_vertices += list(result.buckets().values())
        else:
            subcircuit_vertices = list(result.buckets().values())
        result.base_mapping = None

        circuit_cut = cut_circuit_wires(
                circuit=self.circuit, 
                method="manual", 
                subcircuit_vertices=subcircuit_vertices,
                verbose=False
            )

        # Experimental turned off
        # for circ, node in zip(circuit_cut['subcircuits'], subcircuit_vertices):
        #     assert circ.count_ops()['cx'] == len(node)
        if circuit_cut['num_cuts'] > self.max_cut_num - 1:
            if previous_cut:
                print("[ ] Early Stop !")
                return self.subcircuits, circuit_cut, True
            else:
                if self.try_cuts < 10:
                    self.try_cuts += 1
                    return self.cut(previous_cut, cut_index)
                else:
                    raise Exception("No small cuts found.")

        partition_vector = [0, ] * self.circuit.count_ops()['cx']
        subcircuits = [None, ] * len(circuit_cut['subcircuits'])
        for pnum, (subcirc, part) in enumerate(zip(circuit_cut['subcircuits'], subcircuit_vertices)):
            for idx in part:
                partition_vector[idx] = pnum
            subcircuits[pnum] = subcirc

        result.subcircuits = subcircuits
        result.partition = partition_vector

        # for circ, node in zip(result.subcircuits, subcircuit_vertices):
        #     assert circ.count_ops()['cx'] == len(node)
        
        # for circ, node in result.subcircuit_partition():
        #     assert circ.count_ops()['cx'] == len(node)
        
        # for experimental purposes
        assert circuit_cut['num_cuts'] < self.max_cut_num
        
        return result, circuit_cut, False

    def recursive_cut(self, minimum_success_probability = 0.7):
        early_stop = False

        if not self.subcircuits:
            self.subcircuits, circuit_cut, early_stop = self.cut()

        prob, idx = least_success_probability(self.subcircuits, self.hardware)
        while (prob < minimum_success_probability) and (not early_stop):
            self.subcircuits, _circuit_cut, early_stop = self.cut(self.subcircuits.subcircuit_partition(), idx)
            prob, idx = least_success_probability(self.subcircuits, self.hardware)
            if not early_stop:
                circuit_cut = _circuit_cut
        
        return self.subcircuits, circuit_cut

