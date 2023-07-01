import qiskit
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGOpNode

latency_gate = {
    'h' : 0.00211322491,
    'cx': 0.022731196524,
    'rx': 0.0019999324,
    'rz': 0.0019999321,
}

def avg(lst):
    return sum(lst) / len(lst)

def time_list(layer):
    time = []
    for node in layer:
        time += [ latency_gate[node.op.name] ]
    return time

def search_node_in_layers(node, layers):
    for index, layer in enumerate(layers):
        if node in layer:
            return index
    return None

def add_node_in_layers(node, layer_number, layers):
    if layer_number > len(layers):
        raise Exception()

    if layer_number == len(layers):
        layers += [ [node, ] ]
    else:
        layers[layer_number] += [ node, ]

    return layers

def get_layers_of_execution(dag):
    layers = [ list(dag.input_map.values()) ]

    for node in dag.nodes():
        if isinstance(node, DAGOpNode):
            predecessors = dag.predecessors(node)
            predecessors_layer = [ search_node_in_layers(predecessor_node, layers) for predecessor_node in predecessors ]

            add_node_in_layers(node, max(predecessors_layer) + 1, layers)
            index = search_node_in_layers(node, layers)



    return layers[1:]

def latency_between_two_nodes(dag, layers, node_A, node_B):

    layer_wise_time = []

    index_A = search_node_in_layers(node_A, layers)
    index_B = search_node_in_layers(node_B, layers)

    if index_A > index_B:
        index_B, index_A = index_A, index_B

    size = index_B - index_A
    for i in range(index_A + 1, index_B):
        layer = layers[i]
        layer_time_list = time_list(layer)
        layer_avg_time = avg(layer_time_list)
        layer_wise_time += [ layer_avg_time  ]

    return size, layer_wise_time, sum(layer_wise_time)

# Example usage
from circ import qc


# Convert the circuit to a DAG
dag = circuit_to_dag(qc)

# Get the layers of execution
layers = get_layers_of_execution(dag)

# Print the layers
for i, layer in enumerate(layers):
    print(f"Layer {i}:")
    for node in layer:
        print(node.op)
    print()

node_A = None
node_B = None
for node in dag.topological_op_nodes():
    if node.name == 'cx':
        if node.op.label == "CNot_6":
            node_A = node
        if node.op.label == "CNot_7":
            node_B = node


print(latency_between_two_nodes(dag, layers, node_A, node_B))