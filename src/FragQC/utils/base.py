from src.FragQC.utils.cx_latency_utils import error_probability_full_circuit
from src.FragQC.Result import Result

from qiskit.converters import circuit_to_dag, dag_to_circuit
from collections import OrderedDict

def remove_idle_qwires(circ):
    dag = circuit_to_dag(circ)

    idle_wires = list(dag.idle_wires())
    for w in idle_wires:
        dag._remove_idle_wire(w)
        dag.qubits.remove(w)

    dag.qregs = OrderedDict()

    return dag_to_circuit(dag)

def combine_results(base_cut_result, subcircuit_cut_result, ):
    # Combine partition
    part = base_cut_result.partition.copy()
    for x in subcircuit_cut_result.base_mapping:
        part[x] = -1
    for val, indeces in subcircuit_cut_result.buckets().items():
        value = val
        if value in part:
            value = max(part) + 1
        for i in indeces:
            part[i] = value

    res = Result(
        min_cost = base_cut_result.min_cost + subcircuit_cut_result.min_cost,
        partition = part,
        time = base_cut_result.time + subcircuit_cut_result.time,
        raw_results = None ,
        # history = [subcircuit_cut_result, base_cut_result],
        # subcircuits = subcircuit_cut_result.subcircuits
    )
    for result in [base_cut_result, subcircuit_cut_result]:
        if result.history:
            res.history += result.history
        else:
            res.history.append(result)

    res.subcircuits = subcircuit_cut_result.subcircuits if len(subcircuit_cut_result.subcircuits) > len(base_cut_result.subcircuits) else base_cut_result.subcircuits
    return res


def least_success_probability(result, hardware):
    success_probability_considered = [1]
    success_probability_all = []
    for subcircuit, part in result.subcircuit_partition():
        if len(part) > 1:
            success_probability_considered.append(error_probability_full_circuit(subcircuit, hardware))
            success_probability_all.append(error_probability_full_circuit(subcircuit, hardware))
        else:
            success_probability_all.append(None)
    
    success_probability_min = min(success_probability_considered)
    
    return success_probability_min, -1 if success_probability_min == 1 else success_probability_all.index(success_probability_min)