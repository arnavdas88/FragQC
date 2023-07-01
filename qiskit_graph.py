import qiskit

from qiskit.dagcircuit import DAGOpNode, DAGInNode
from qiskit.converters import circuit_to_dag


# Create a Qiskit circuit
qc = qiskit.QuantumCircuit(5)

for i in range(5):
    qc.h(i)
    qc.rz(-.4, i)

qc.cnot(0, 3, label = "CNot_2") # CX2

qc.cnot(1, 2, label="CNot_0") # CX0
qc.rz(.1,3)

qc.rz(.2,2)

qc.cnot(0, 3, label="CNot_3") # CX3

qc.rx(.3,0)
qc.cnot(1, 2, label="CNot_1") # CX1
qc.rz(.4,3)

qc.rz(.5,1)
qc.rz(.6,2)

qc.cnot(1, 3, label="CNot_4") # CX4

qc.cnot(2, 4, label="CNot_6") # CX6

qc.rz(.7,3)
qc.rz(.8,4)

qc.cnot(1, 3, label="CNot_5") # CX5

qc.rx(.9,1)
qc.cnot(2, 4, label="CNot_7") # CX7

qc.rx(5.15,2)
qc.rx(5.15,3)
qc.rx(5.15,4)



# Convert the circuit to a DAG
dag = circuit_to_dag(qc)

def get_cx_predecessor(dag, node, line="control"):
    p1, p2 = list(dag.predecessors(node))
    if line == "target":
        qargs_of_context = node.qargs[0]
    elif line == "control":
        qargs_of_context = node.qargs[1]

    if qargs_of_context in p1.qargs:
        return p1
    if qargs_of_context in p2.qargs:
        return p2


def get_recurrent_predecessors(dag, node, init=True):
    if isinstance(node, DAGOpNode):
        if not node.name == 'cx' or init:
            # _node = get_cx_predecessor(dag, node)
            for _node in dag.predecessors(node):
                if isinstance(_node, DAGOpNode):
                    if _node.name == 'cx':
                        continue
                    yield _node
                    for n in get_recurrent_predecessors(dag, _node, init=False):
                        yield n

latency_gate = {
    'h': 0.00211322491,
    'cx': 0.022731196524,
    'rx': 0.0019999321,
    'rz': 0.0019999321,
}
def dependent_registers(dag, dest_node):
    if isinstance(dest_node, DAGOpNode):
        regs = [ *dest_node.qargs ]
        for interim_node in dag.predecessors(dest_node):
            if isinstance(interim_node, DAGOpNode):
                regs += list(dependent_registers(dag, interim_node))
    return set(regs)

def get_latency_over(dag, dest_node):
    if isinstance(dest_node, DAGOpNode):

        dep_registers = list(dependent_registers(dag, dest_node))
        dag_walk = []
        for reg in dep_registers:
            dag_walk.append( dag.nodes_on_wire(reg) )

        layer_cursor = 1
        COUNTING_DISTANCE = False
        while layer_cursor:

            # Get one Layer
            layer_nodes_start = []
            for walker in dag_walk:
                node = walker.__next__()
                if isinstance(node, DAGInNode):
                    node = walker.__next__()
                if isinstance(node, DAGOpNode):
                    layer_nodes_start += [ walker.__next__() ]
                else:
                    continue

            layer_to_count_from = None
            continue_depth_iteration = True
            latency_depth = [0, ] * len(layer_nodes_start)
            layer_nodes = [ layer_nodes_start ]
            while continue_depth_iteration:
                for index, layer in enumerate(layer_nodes[-1]):
                    pass
                # layer_nodes += [ ... ]
                continue_depth_iteration = False
                pass
            for index, node in enumerate(layer_nodes_start):
                # Look Forward
                if not COUNTING_DISTANCE and (dest_node in list(dag.successors(node))):
                    COUNTING_DISTANCE = True
                    layer_to_count_from = index
                    break
                    # return get_distance(dag,  set(layer_nodes_start).difference([node]), dest_node)
                # else:
                    # successor_qargs = [n.qargs for n in dag.successors(node)]
                    # if [n.qargs for n in dag.successors(node)] > 1:
            for index, node in enumerate(layer_nodes_start[layer_to_count_from: ]):
                pass




            layer_cursor += 1


    pass

def get_distance(dag, layer_nodes, dest_node):
    return 0

# Iterate over the nodes in the DAG
for node in dag.topological_op_nodes():
    if node.name == 'cx':
        if node.op.label == "CNot_7":
            latency = get_latency_over(dag, node)
            pass
        # Fetch the predecessors of the node
        predecessors = set([ p for p in get_recurrent_predecessors(dag, node) if isinstance(p, DAGOpNode)])
        print(f"Predecessors for {node.op.label} ({len(predecessors)}): ", [p.name for p in predecessors])
        print()

print()