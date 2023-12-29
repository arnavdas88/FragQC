import numpy as np

from qiskit.circuit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.circuit import Reset
from qiskit.circuit.library.standard_gates import (IGate, U1Gate, U2Gate, XGate,
                                                   YGate, ZGate, HGate, RXGate, 
                                                   RYGate, RZGate, CXGate,
                                                   CYGate, CZGate, SwapGate)
from qiskit.circuit.exceptions import CircuitError
# from qiskit.util import deprecate_arguments

def random_circuit(num_qubits, depth, max_operands=2, reset=False, seed=None,
                   *, n_qubits=None):  # pylint:disable=unused-argument
    """Generate random circuit of arbitrary size and form.

    This function will generate a random circuit by randomly selecting gates
    from the set of standard gates in :mod:`qiskit.extensions`. For example:

    .. jupyter-execute::

        from qiskit.circuit.random import random_circuit

        circ = random_circuit(2, 2, measure=True)
        circ.draw(output='mpl')

    Args:
        num_qubits (int): number of quantum wires
        depth (int): layers of operations (i.e. critical path length)
        max_operands (int): maximum operands of each gate (between 1 and 2)
        reset (bool): if True, insert middle resets
        seed (int): sets random seed (optional)
        n_qubits (int): deprecated, use num_qubits instead

    Returns:
        QuantumCircuit: constructed circuit

    Raises:
        CircuitError: when invalid options given
    """
    if max_operands < 1 or max_operands > 2:
        raise CircuitError("max_operands must be between 1 and 2")

    one_q_ops = [IGate, U1Gate, U2Gate,
                 HGate, RXGate, RYGate, RZGate]
    one_param = [U1Gate, RXGate, RYGate, RZGate, ]
    two_param = [U2Gate]
    two_q_ops = [CXGate, CZGate ] #, CYGate ]# SwapGate]

    qr = QuantumRegister(num_qubits, 'q')
    qc = QuantumCircuit(num_qubits)

    if reset:
        one_q_ops += [Reset]

    if seed is None:
        seed = np.random.randint(0, np.iinfo(np.int32).max)
    rng = np.random.default_rng(seed)

    # apply arbitrary random operations at every depth
    for _ in range(depth):
        # choose either 1, or 2 qubits for the operation
        remaining_qubits = list(range(num_qubits))
        while remaining_qubits:
            max_possible_operands = min(len(remaining_qubits), max_operands)
            num_operands = rng.choice(range(max_possible_operands)) + 1
            rng.shuffle(remaining_qubits)
            operands = remaining_qubits[:num_operands]
            remaining_qubits = [q for q in remaining_qubits if q not in operands]
            if num_operands == 1:
                operation = rng.choice(one_q_ops)
            elif num_operands == 2:
                operation = rng.choice(two_q_ops)
            if operation in one_param:
                num_angles = 1
            elif operation in two_param:
                num_angles = 2
            else:
                num_angles = 0
            angles = [rng.uniform(0, 2 * np.pi) for x in range(num_angles)]
            register_operands = [qr[i] for i in operands]
            op = operation(*angles)

            qc.append(op, register_operands)

    return qc