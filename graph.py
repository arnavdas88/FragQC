import retworkx as rx
import networkx as nx

import numpy as np
from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGInNode

from collections import Counter

from utils import get_weighted_edges
from circ import qc


GATE_ERROR = {
    'id': 0.0024623157380400853,
    'u1': 0.0,
    'u2': 0.0024623157380400853,
    'u3': 0.004924631476080171,
    'cx': 0.03130722830688227
}

H = GATE_ERROR['u2']
Rz = GATE_ERROR['u2']
Rx = GATE_ERROR['u2']
CNOT = GATE_ERROR['cx']

error_mapping = {
    "h" : H,
    "rz": Rz,
    "rx": Rx,
    "cx": CNOT
}

input_nodes = [f"qi_{i}" for i in range(5)]
cx_nodes = [f"cx_{i}" for i in range(8)]
output_nodes = [f"qo_{i}" for i in range(5)]

G = nx.MultiDiGraph()

# G.add_nodes_from(input_nodes + cx_nodes + output_nodes)
G.add_nodes_from(cx_nodes)

# Inputs to CX
# G.add_weighted_edges_from( [ ("qi_0", "cx_2", 1), ("qi_3", "cx_2", 1) ] )
# G.add_weighted_edges_from( [ ("qi_1", "cx_0", 1), ("qi_2", "cx_0", 1) ] )
# G.add_weighted_edges_from( [ ("qi_4", "cx_6", 1) ] )

G.add_weighted_edges_from( [ ("cx_2", "cx_3", 2), ("cx_3", "cx_4", 1) ] )
G.add_weighted_edges_from( [ ("cx_0", "cx_1", 2), ("cx_1", "cx_4", 1) ] )
G.add_weighted_edges_from( [ ("cx_1", "cx_6", 1), ("cx_4", "cx_5", 2), ("cx_6", "cx_7", 2) ] )

# CX to Output
# G.add_weighted_edges_from( [ ("cx_3", "qo_0", 1), ("cx_5", "qo_1", 1), ("cx_5", "qo_3", 1) ] )
# G.add_weighted_edges_from( [ ("cx_7", "qo_2", 1), ("cx_7", "qo_4", 1) ] )

A = nx.adjacency_matrix(G.to_undirected()).todense()
A = np.asarray(A, dtype=np.float32)
E = get_weighted_edges(G)

# V = { 'qi_0': 0, 'qi_1': 0, 'qi_2': 0, 'qi_3': 0, 'qi_4': 0, }

V = {}

V['cx_0'] = (2*H) + (2*Rz) + CNOT
V['cx_1'] = (2*H) + (3*Rz) + (2*CNOT)
V['cx_2'] = (2*H) + (2*Rz) + CNOT
V['cx_3'] = (2*H) + (3*Rz) + (2*CNOT)
V['cx_4'] = (2*H) + (5*Rz) + (3*CNOT)
V['cx_5'] = (2*H) + (5*Rz) + (3*CNOT)
V['cx_6'] = (2*H) + (4*Rz) + (3*CNOT)
V['cx_7'] = (2*H) + (4*Rz) + (4*CNOT)

# V['qo_0'] = V['cx_3'] + Rx
# V['qo_1'] = V['cx_5'] + Rx
# V['qo_2'] = V['cx_7'] + Rx
# V['qo_3'] = V['cx_5'] + Rx
# V['qo_4'] = V['cx_7'] + Rx

for i, weight in enumerate(V.values()):
    A[i][i] = weight

NODES = list(G.nodes())

mapping_i2n = { i:val for (i, val) in enumerate(NODES) }
mapping_n2i = { val:i for (i, val) in enumerate(NODES) }

def get_previous_cx_node(dag, cx_node, ):
    for node in dag.predecessors(cx_node):
        if isinstance(node, DAGInNode):
            continue
        if node.op.name == "cx":
            yield node
        else:
            previous_cx = list(get_previous_cx_node(dag, node, ))
            for p_cx in previous_cx:
                yield p_cx

def get_error(dag, cx_node, error_mapping):
    gates = [cx_node]
    error = []
    error_names = []
    while gates:
        cx_node = gates.pop()
        error += [error_mapping[cx_node.op.name]]
        error_names += [cx_node.op.name]
        for node in dag.predecessors(cx_node):
            if isinstance(node, DAGInNode):
                continue
            if node.op.name == "cx":
                continue
            else:
                gates.append( node )
    return sum(error)


def error_cx_adjacency(circuit):
    dag = circuit_to_dag(circuit)
    nodes = [ node for node in dag.topological_op_nodes() ]
    cx_nodes = [cx_node for cx_node in nodes if cx_node.op.name == "cx"]
    N = len(cx_nodes)

    adjacency = np.zeros(shape = ( N, N ))

    for index, cx_node in enumerate(cx_nodes):
        prev_cx = list(get_previous_cx_node(dag, cx_node))
        for cx, count in Counter(prev_cx).items():
            _from = cx_nodes.index(cx)
            _to = cx_nodes.index(cx_node)
            adjacency[_from, _to] = count
            adjacency[_to, _from] = count
        adjacency[index, index] = get_error(dag, cx_node, error_mapping)

    return adjacency

A2 = error_cx_adjacency(qc)
pass