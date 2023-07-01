import warnings
import numpy as np
from dimod import Integer, Binary


def get_qubo_dwave(A, V):

    # Defining the variables
    variables = [ Binary(f'z_{i}') for i in range(A.shape[0])]
    z = [ 1 - 2*var for var in variables]

    objective_A = 0

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if i != j:
                objective_A += ( A[i][j] ) * (1 - (z[i]*z[j])) / 2

    objective_B = 0

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if i < j:
                objective_B += V[i] * V[j] * z[i] * z[j]

    # Ensures there is atleast one cut
    objective_C = ( sum(variables) - len(variables) / 2 ) ** 2

    objective = objective_A + (2 * objective_B) + objective_C

    return objective



# Problem modelling imports
from docplex.mp.model import Model

# Qiskit imports
from qiskit_optimization import QuadraticProgram

def get_qubo_qiskit(A, V) -> QuadraticProgram:

    # Defining the variables
    mdl = Model()
    variables = [ mdl.binary_var(f'z_{i}') for i in range(A.shape[0])]

    z = [ 1 - 2*var for var in variables]

    objective_A = 0

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if i != j:
                objective_A += ( A[i][j] ) * (1 - (z[i]*z[j])) / 2

    objective_B = 0

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if i < j:
                objective_B += V[i] * V[j] * z[i] * z[j]

    # Ensures there is atleast one cut
    objective_C = ( mdl.sum(variables) - len(variables) / 2 ) ** 2

    objective = objective_A + (2 * objective_B) + objective_C

    return objective