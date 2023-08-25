import numpy as np

# importing Qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

from qiskit import QuantumRegister
from qiskit import ClassicalRegister
from qiskit import QuantumCircuit, execute,IBMQ
from qiskit.tools.monitor import job_monitor

from qiskit.opflow import X, Z, Zero
from qiskit.algorithms import EvolutionProblem, TrotterQRTE
from qiskit import BasicAer
from qiskit.utils import QuantumInstance

from qiskit.opflow import (
    SummedOp,
    PauliOp,
    CircuitOp,
    ExpectationBase,
    CircuitSampler,
    PauliSumOp,
    StateFn,
    OperatorBase,
)
from qiskit.circuit.library import PauliEvolutionGate


num_qubits = 5
qc = QuantumCircuit(num_qubits)

params = np.random.uniform(low=0., high=np.pi,  size=(2, ))

qc.rx(params, range(num_qubits))

gates = ['h', 'rx', 'ry', 'rz', 'cx', 'dgt', 'u2', 'u3', 'i', 'sx']

# qc = qc.decompose(gates)
qc = transpile(qc, basis_gates=gates)
print(qc)

with open(f"/workspace/FragQC/benchmark/circuits/private_bench/trotter_qrte{len(qc.qubits)}.qasm", "w+") as file:
    file.write(qc.decompose(gates).qasm())