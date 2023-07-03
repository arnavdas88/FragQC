from collections import Counter
import numpy as np

from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGInNode

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
        error += [error_mapping.get(cx_node.op.name)]
        error_names += [cx_node.op.name]
        for node in dag.predecessors(cx_node):
            if isinstance(node, DAGInNode):
                continue
            if node.op.name == "cx":
                continue
            else:
                gates.append( node )
    return sum(error)


def cx_adjacency(circuit, hardware):
    dag = circuit_to_dag(circuit)
    nodes = [ node for node in dag.topological_op_nodes() ]
    cx_nodes = [cx_node for cx_node in nodes if cx_node.op.name == "cx"]

    N = len(cx_nodes) # + 1 # for n break points, their will be n+1 peices
    adjacency = np.zeros(shape = ( N, N ))

    for index, cx_node in enumerate(cx_nodes):
        prev_cx = list(get_previous_cx_node(dag, cx_node))
        for cx, count in Counter(prev_cx).items():
            _from = cx_nodes.index(cx)
            _to = cx_nodes.index(cx_node)
            adjacency[_from, _to] = count
            adjacency[_to, _from] = count
        # Diagonals
        adjacency[index, index] = get_error(dag, cx_node, hardware.error_model)
        # adjacency[index, index] = error_probability(dag, cx_node)

    return adjacency

def create_index_node_map(circuit):
    dag = circuit_to_dag(circuit)
    nodes = [ node for node in dag.topological_op_nodes() ]
    cx_nodes = [cx_node for cx_node in nodes if cx_node.op.name == "cx"]

    mapping_i2n = { index: cx for index, cx in enumerate(cx_nodes) }
    mapping_n2i = { cx: index for index, cx in enumerate(cx_nodes) }

    mapping_names = { (cx.op.label if cx.op.label else f"cx_{index}"): cx for index, cx in enumerate(cx_nodes) }

    return mapping_i2n, mapping_n2i, mapping_names
