# Import a Dummy Circuit
from circ import qc

# Import the FragQC Circuit Cutting Engine
from src.FragQC.FragQC import FragQC

# Import the Qiskit Backend for FragQC
from src.FragQC.fragmentation.QUBO import Qiskit

# Import a Dummy Hardware Configuration 
from src.FragQC.Hardware import DummyHardware

# Import Qiskit Utilities
from qiskit_optimization.algorithms import MinimumEigenOptimizer # EigenSolver
from qiskit.algorithms.optimizers import COBYLA # Optimizer
from qiskit.algorithms import QAOA # QAOA Algorithm
from qiskit import IBMQ # IBM Account

# Loading IBM Account
IBMQ.save_account(token = "77156861472499e22abf983c7d826ebbd1862575f069a53a6040276a0550afbce8f32e5a05f36f31391e79689e358c74b3c3e441dda2a97efea8a374f1110852")
IBMQ.load_account()
provider = IBMQ.get_provider(hub = "ibm-q", group = "open", project = "main")

# Circuit Fragmentor Initialization
fragmentor = FragQC(
    qc,
    fragmentation_procedure = Qiskit(
        solver = MinimumEigenOptimizer(
            min_eigen_solver = QAOA(
                optimizer = COBYLA(), 
                reps = 2, 
                quantum_instance = provider.get_backend("ibmq_qasm_simulator")
            )
        )
    ),
    hardware = DummyHardware
)

# Circuit Fragmentor Execution
fragments, result = fragmentor.fragment()

# Show Results
print("Score :", result.min_cost)

for cx_node_name, fragment_bag, cx_node in fragments:
    print(cx_node_name, fragment_bag)
