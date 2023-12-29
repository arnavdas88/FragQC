import time
from typing import Any

from qiskit import QuantumCircuit
from qiskit.transpiler.passes import RemoveBarriers

from src.FragQC.Hardware import Hardware, DummyHardware
from src.FragQC.utils import create_index_node_map, cx_adjacency, individual_fragment_error, error_probability_full_circuit
from src.FragQC.utils.base import combine_results, least_success_probability, remove_idle_qwires, auto_order
from src.FragQC.utils.circuit_knitting_toolbox import path_map_subcircuit, replace_from_base_map

from src.FragQC.fragmentation.GeneticAlgorithm.utils import cost_calculation
from src.FragQC.Result import Result

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

        self.result : Result = None
        self.try_cuts = 0

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    def prepare_graph(self, ):
        adj = cx_adjacency(self.circuit, self.hardware)
        print(f"[i] Circuit found {len(adj)} Cx gates.")
        fragment_error = individual_fragment_error(self.circuit, self.hardware)
        full_circuit_error_probability = error_probability_full_circuit(self.circuit, self.hardware)
        assert adj.shape == ( len(fragment_error), len(fragment_error) )

        for index, error in enumerate(fragment_error):
            adj[index, index] += error
        
        return adj


    def fragment(self, ):
        adj = self.prepare_graph()
        mapping_i2n, mapping_n2i, mapping_names = create_index_node_map(self.circuit)

        starting_time = time.time()
        result = self.fragmentation_procedure(adj)
        ending_time = time.time()
        if result.time == 0:
            result.time = (ending_time - starting_time)

        fragment_map, score = result.partition, result.min_cost

        standard_cost = cost_calculation(adj, result.partition)
        if standard_cost == 0.0:
            return self.fragment()
        print(f"[i] Standardized cost for the fragmentation is {standard_cost}")

        return [ (name, fragment_bag, cx, ) for (name, cx), fragment_bag in zip(mapping_names.items(), fragment_map) ], result

    def cut(self, previous_cut = None, cut_index=0):
        if previous_cut:
            previous_cut = list(previous_cut)

            # Auto-fix subcircuit_vertices
            previous_cut = auto_order(previous_cut)


        if previous_cut:
            subcircuits, subcircuit_vertices = list(zip(*previous_cut))
            subcircuits, subcircuit_vertices = list(subcircuits), list(subcircuit_vertices)


        if previous_cut:
            _circuit = self.circuit
            self.circuit = subcircuits[cut_index]
        
        # Experimental turned off
        # if previous_cut:
        #     for circ, node in zip(subcircuits, subcircuit_vertices):
        #         assert circ.count_ops().get('cx', 0) == len(node)

        fragments, result = self.fragment()

        if previous_cut:
            assert len(subcircuit_vertices[cut_index]) == len(result.partition) == self.circuit.count_ops().get('cx', 0) + self.circuit.count_ops().get('cz', 0)
            # assert len(result.partition) == self.circuit.count_ops().get('cx', 0) + self.circuit.count_ops().get('cz', 0)
            # if not ( len(subcircuit_vertices[cut_index]) == len(result.partition) == self.circuit.count_ops().get('cx', 0) +  + self.circuit.count_ops().get('cz', 0)):
            #     print(len(subcircuit_vertices[cut_index]), len(result.partition), self.circuit.count_ops().get('cx', 0) +  + self.circuit.count_ops().get('cz', 0))
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
        #     assert circ.count_ops().get('cx', 0) == len(node)
        if circuit_cut['num_cuts'] > self.max_cut_num:
            if previous_cut:
                print("[ ] Early Stop !")
                return self.result, circuit_cut, True
            else:
                if self.try_cuts < 10:
                    self.try_cuts += 1
                    return self.cut(previous_cut, cut_index)
                else:
                    raise Exception("No small cuts found.")

        partition_vector = [0, ] * (self.circuit.count_ops().get('cx', 0) + self.circuit.count_ops().get('cz', 0))
        subcircuits = [None, ] * len(circuit_cut['subcircuits'])
        for pnum, (subcirc, part) in enumerate(zip(circuit_cut['subcircuits'], subcircuit_vertices)):
            for idx in part:
                partition_vector[idx] = pnum
            subcircuits[pnum] = subcirc

        result.subcircuits = subcircuits
        result.partition = partition_vector

        if self.result:
            result.num_cuts = self.result.num_cuts
        result.num_cuts.append(circuit_cut['num_cuts']) 

        # for circ, node in zip(result.subcircuits, subcircuit_vertices):
        #     assert circ.count_ops().get('cx', 0) + circ.count_ops().get('cz', 0) == len(node)
        
        # for circ, node in result.subcircuit_partition():
        #     assert circ.count_ops().get('cx', 0) + circ.count_ops().get('cz', 0) == len(node)
        
        # for experimental purposes
        assert circuit_cut['num_cuts'] < self.max_cut_num + 1
        
        return result, circuit_cut, False

    def recursive_cut(self, minimum_success_probability = 0.7):
        early_stop = False

        if not self.result:
            self.result, circuit_cut, early_stop = self.cut()

        prob, idx = least_success_probability(self.result, self.hardware)
        while (prob < minimum_success_probability) and (not early_stop):
            self.result, _circuit_cut, early_stop = self.cut(self.result.subcircuit_partition(), idx)
            prob, idx = least_success_probability(self.result, self.hardware)
            if not early_stop:
                circuit_cut = _circuit_cut
        
        return self.result, circuit_cut

