from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGOpNode, DAGInNode, DAGOutNode

import numpy as np

# DAG Node Operation
def node_type(node):
    return type(node)

def is_leaf_node(node):
    # return node._type == 'out'
    return isinstance(node, DAGOutNode)


def is_op_node(node):
    # return node._type == 'op'
    return isinstance(node, DAGOpNode)

def is_seed_node(node):
    return isinstance(node, DAGInNode)

def select_node_at_qreg(node_list, qreg):
    for node in node_list:
        if qreg in node.qargs:
            return node

# Layer Operations

def search_node_in_layers(node, layers):
    for index, layer in enumerate(layers):
        if node in layer:
            return index
    return None

def select_in_layer(layers, layer = 0, qregs = 0):
    layer = layers[layer]
    for index, node in enumerate(layer):
        if qregs in [qreg.index for qreg in node.qargs]:
            return index, node
    return -1, None

def add_node_in_layers(node, layer_number, layers):
    if layer_number > len(layers):
        raise Exception()

    if layer_number == len(layers):
        layers += [ [node, ] ]
    else:
        layers[layer_number] += [ node, ]

    return layers

# Direct Utility

# get_layers_of_execution is DEPRECATED
def get_layers_of_execution(dag):
    """ DEPRICATED """
    layers = [ list(dag.input_map.values()) ]

    for node in dag.nodes():
        if isinstance(node, DAGOpNode):
            predecessors = dag.predecessors(node)
            predecessors_layer = [ search_node_in_layers(predecessor_node, layers) for predecessor_node in predecessors ]

            add_node_in_layers(node, max(predecessors_layer) + 1, layers)
            index = search_node_in_layers(node, layers)

    # Late operations
    qregs = list(range(len(layers[0])))
    hardened_qregs = []
    for index, layer in enumerate(layers[1:]):
        for qreg in qregs:
            if qreg not in hardened_qregs:
                _filled_ = [ [ qreg.index for qreg in node.qargs ] for node in layer ]
                filled = dict( [ (i, []) for i in qregs])
                for fl in _filled_:
                    for f in fl:
                        filled[f] = fl
                filled = list(filled.values())

                occupied = any([(qreg in occupy) for occupy in filled])
                self_occupancy = len(filled) > qreg
                if self_occupancy:
                    self_occupancy = qreg in filled[qreg]
                affects_others = len(filled) > qreg
                if affects_others:
                    affects_others = len(filled[qreg]) > 1
                affected_by_others = any([(qreg in occupy) for i, occupy in enumerate(filled) if i != qreg])
                dependent_on_other_qregs = (affects_others or affected_by_others)
                empty_spot = (not dependent_on_other_qregs) and (not self_occupancy)
                if dependent_on_other_qregs:
                    hardened_qregs += [ qreg ]
                if empty_spot:
                    # Shift nodes forward
                    for shift_i in range(index, 0, -1):
                        _index, _node = select_in_layer(layers, layer = shift_i, qregs = qreg)
                        if _node:
                            node = layers[shift_i].pop(_index)
                            layers[shift_i + 1].append(node)
                    pass

    return layers[1:]

def latency_previous_subcircuit(node, dag, hardware):
    latency = { qreg.index: [] for qreg in node.qargs }
    node_to_consider = list(dag.predecessors(node))

    while node_to_consider:
        cursor  = node_to_consider.pop()
        if isinstance(cursor, DAGInNode):
            continue
        elif cursor.name == 'cx':
            continue
        else:
            _index = cursor.qargs[0].index
            # if _index not in latency:
            #     latency[_index] = []   
            latency[_index] += [hardware.latency_model.SINGLE_GATE_CONST_LATENCY]
            [node_to_consider.append(p_node) for p_node in dag.predecessors(cursor) if isinstance(p_node, DAGOpNode)]


    return sum(sorted(latency.values(), key=lambda x:sum(x), reverse=True)[0])

def get_previous_cx_node(dag, cx_node, ):
    """ DEPRICATED """
    for node in dag.predecessors(cx_node):
        if isinstance(node, DAGInNode):
            continue
        if node.op.name == "cx":
            yield node
        else:
            previous_cx = list(get_previous_cx_node(dag, node, ))
            for p_cx in previous_cx:
                yield p_cx

def error_probability(dag, cx_node, hardware):
    predecessor_stack = [cx_node]
    successor_stack   = [cx_node]
    single_qubit_gates = []
    double_qubit_gates = []
    while predecessor_stack:
        _cx_node = predecessor_stack.pop()
        for node in dag.predecessors(_cx_node):
            if isinstance(node, DAGInNode):
                continue
            if node.op.name == "cx":
                continue
            predecessor_stack.append( node )
            single_qubit_gates.append(node)

    # Only for last cx
    consider_successors = False
    successors_gates = []
    successors_gate_names = []
    while successor_stack:
        _any_node = successor_stack.pop()
        successors = list(dag.successors(_any_node))
        successors = list(filter(is_op_node, successors))
        
        successor_node = select_node_at_qreg(successors, _any_node.qargs[0]) # 0th qreg is control
        
        if len(successors) == 0:
            consider_successors = True
            break
        successor_stack.append(successor_node)
        if successor_node.op.name == 'cx':
            break
        successors_gates.append(successor_node)
        successors_gate_names.append(successor_node.op.name)

    if consider_successors:
        single_qubit_gates += [*successors_gates]

    k1 = len(single_qubit_gates) # All single qubit gates before cx to last cx
    k2 = max(1, len(double_qubit_gates)) # Constant, No. of two qubit gates

    latency = latency_previous_subcircuit(cx_node, dag, hardware)

    p1 = hardware.error_model.u2 # probability of error of single qubit gates
    p2 = hardware.error_model.cx # probability of error of two qubit gates


    t1 = hardware.relaxation_time
    t2 = hardware.coherence_time

    p_success = [ (1 - p1) ** k1, (1 - p2)**k2,  np.exp( -( latency/t1 + latency/t2) )]
    p_success = np.prod(p_success)

    return 1 - p_success

def error_probability_full_circuit(circuit, hardware):
    dag = circuit_to_dag(circuit)
    layer_count = circuit.depth()

    # Fetch the layers
    layers = list(dag.layers())

    # Cerify if dag layer count equates to the depth of the circuit
    assert len(layers) == layer_count

    # stores layer wise latency
    latency = []


    for layer in layers:
        op_nodes = layer['graph'].op_nodes()
        op_latency = [hardware.latency_model.get(op.name) for op in op_nodes]
        layer_latency = max(op_latency)

        latency.append(layer_latency)

    single_qubit_gates = [instruction for instruction, _, _ in circuit.data if instruction.num_qubits == 1]
    double_qubit_gates = [instruction for instruction, _, _ in circuit.data if instruction.num_qubits == 2]

    k1 = len(single_qubit_gates) # All single qubit gates before cx to last cx
    k2 = len(double_qubit_gates) # Constant, No. of two qubit gates

    total_latency = sum(latency)

    p1 = hardware.error_model.u2 # probability of error of single qubit gates
    p2 = hardware.error_model.cx # probability of error of two qubit gates


    t1 = hardware.relaxation_time
    t2 = hardware.coherence_time

    p_success = [ 
        ((1 - p1) ** k1) if k1 else 0, 
        ((1 - p2) ** k2) if k2 else 0,  
        np.exp( -( total_latency/t1 + total_latency/t2) )
    ]
    p_success = np.prod(p_success)

    return p_success


def individual_fragment_error(circuit, hardware):
    dag = circuit_to_dag(circuit)
    layers = list(dag.layers())

    nodes = [ node for node in dag.topological_op_nodes() ]
    cx_nodes = [cx_node for cx_node in nodes if cx_node.op.name == "cx"]
    N = len(cx_nodes)

    total_error = []

    for cx_node in cx_nodes:

        # latency_time = latency_previous_subcircuit(cx_node, dag)

        error = error_probability(dag, cx_node, hardware)
        total_error += [ error ]

    return total_error

