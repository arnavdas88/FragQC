import qiskit
from qiskit import QuantumCircuit

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