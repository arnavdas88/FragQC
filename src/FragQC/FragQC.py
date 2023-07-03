import time
from typing import Any
from qiskit import QuantumCircuit
from src.FragQC.Hardware import Hardware, DummyHardware
from src.FragQC.utils import create_index_node_map, cx_adjacency, individual_fragment_error


class FragQC:
    def __init__(self, circuit : QuantumCircuit, fragmentation_procedure = None, hardware: Hardware = DummyHardware ) -> None:
        if not fragmentation_procedure:
            raise Exception("No Fragmentation procedure is defined!")
        self.circuit = circuit
        self.fragmentation_procedure = fragmentation_procedure
        self.hardware = hardware

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    def fragment(self, ):
        adj = cx_adjacency(self.circuit, self.hardware)
        fragment_error = individual_fragment_error(self.circuit, self.hardware)
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

    def get_fragments(self, ):
        pass

    def score(self, ):
        pass