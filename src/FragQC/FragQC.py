import time
from typing import Any
from qiskit import QuantumCircuit
from src.FragQC.Hardware import Hardware, DummyHardware
from src.FragQC.utils import create_index_node_map, cx_adjacency, cx_latency


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
        latency_error = cx_latency(self.circuit, self.hardware)
        assert adj.shape == ( len(latency_error), len(latency_error) )

        for index, error in enumerate(latency_error):
            adj[index, index] += error
        mapping_i2n, mapping_n2i, mapping_names = create_index_node_map(self.circuit)

        starting_time = time.time()
        fragment_map, score = self.fragmentation_procedure(adj)
        ending_time = time.time()

        return score, [ (name, fragment_bag, cx, ) for (name, cx), fragment_bag in zip(mapping_names.items(), fragment_map) ], (ending_time - starting_time)

    def get_fragments(self, ):
        pass

    def score(self, ):
        pass